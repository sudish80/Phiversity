from pathlib import Path

import pytest

from phiversity.compose import (ComposeError, _format_srt, _ts, _wrap,
                                  align_and_mux, concat, crossfade_join,
                                  has_audio_stream, normalize_foreign,
                                  smart_concat, write_segment_srt)
from phiversity.config import TTSConfig
from phiversity.tts import estimate_duration, ffprobe_duration, synthesize


def make_silence(path: Path, seconds: float) -> Path:
    import subprocess
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", "anullsrc=r=44100:cl=mono", "-t", str(seconds),
         "-c:a", "pcm_s16le", str(path)],
        check=True)
    return path


def make_color_video(path: Path, seconds: float) -> Path:
    import subprocess
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", f"testsrc=duration={seconds}:size=320x240:rate=15",
         "-pix_fmt", "yuv420p", "-c:v", "libx264", str(path)],
        check=True)
    return path


class TestSilenceTTS:
    def test_silence_engine_writes_wav(self, tmp_path):
        cfg = TTSConfig(engine="silence")
        path, duration = synthesize("hello world, this is a test",
                                   tmp_path / "a.wav", cfg)
        assert path.exists()
        assert duration == pytest.approx(estimate_duration(
            "hello world, this is a test"), abs=0.2)

    def test_estimate_duration_bounds(self):
        assert estimate_duration("one two three") >= 2.5
        assert estimate_duration("word " * 200) <= 90

    def test_ffprobe_duration(self, tmp_path):
        wav = make_silence(tmp_path / "s.wav", 2.5)
        assert ffprobe_duration(wav) == pytest.approx(2.5, abs=0.05)

    def test_unknown_engine_raises_then_falls_back(self, tmp_path, capsys):
        cfg = TTSConfig(engine="does-not-exist")
        path, duration = synthesize("some words", tmp_path / "b.wav", cfg)
        assert path.exists() and duration > 0
        assert "warn" in capsys.readouterr().out


class TestSrt:
    def test_wrap(self):
        lines = _wrap("aaa bbb ccc ddd", 7)
        assert all(len(line) <= 7 for line in lines)
        assert " ".join(lines) == "aaa bbb ccc ddd"

    def test_timestamp_format(self):
        assert _ts(3661.5) == "01:01:01,500"

    def test_format_srt(self):
        text = _format_srt([(0.0, 2.0, ["hello", "world"])])
        assert "1\n00:00:00,000 --> 00:00:02,000\nhello\nworld\n" in text

    def test_write_segment_srt(self, tmp_path):
        srt = write_segment_srt("a b c", 4.2, tmp_path / "sub.srt")
        assert srt.exists()
        assert "00:00:04,200" in srt.read_text()


class TestAlignAndMux:
    def test_pads_video_when_audio_longer(self, tmp_path):
        video = make_color_video(tmp_path / "v.mp4", 2.0)
        audio = make_silence(tmp_path / "a.wav", 3.0)
        out = align_and_mux(video, audio, tmp_path / "seg.mp4")
        assert ffprobe_duration(out) == pytest.approx(3.0, abs=0.15)

    def test_pads_audio_when_video_longer(self, tmp_path):
        video = make_color_video(tmp_path / "v.mp4", 3.0)
        audio = make_silence(tmp_path / "a.wav", 2.0)
        out = align_and_mux(video, audio, tmp_path / "seg.mp4")
        assert ffprobe_duration(out) == pytest.approx(3.0, abs=0.15)

    def test_burns_captions(self, tmp_path):
        video = make_color_video(tmp_path / "v.mp4", 2.0)
        audio = make_silence(tmp_path / "a.wav", 2.0)
        srt = write_segment_srt("caption text here", 2.0,
                                tmp_path / "cap.srt")
        out = align_and_mux(video, audio, tmp_path / "seg.mp4", srt=srt)
        assert out.exists() and ffprobe_duration(out) > 1.5

    def test_concat_two(self, tmp_path):
        parts = []
        for i, dur in enumerate([2.0, 3.0]):
            video = make_color_video(tmp_path / f"v{i}.mp4", dur)
            audio = make_silence(tmp_path / f"a{i}.wav", dur)
            parts.append(align_and_mux(video, audio,
                                       tmp_path / f"seg{i}.mp4"))
        out = concat(parts, tmp_path / "final.mp4")
        assert ffprobe_duration(out) == pytest.approx(5.0, abs=0.2)

    def test_concat_single_moves_file(self, tmp_path):
        video = make_color_video(tmp_path / "v.mp4", 1.0)
        audio = make_silence(tmp_path / "a.wav", 1.0)
        part = align_and_mux(video, audio, tmp_path / "seg.mp4")
        out = concat([part], tmp_path / "final.mp4")
        assert out.exists() and not part.exists()

    def test_concat_with_relative_output_dir(self, tmp_path, monkeypatch):
        """Regression: concat must work even when paths are relative."""
        monkeypatch.chdir(tmp_path)
        parts = []
        for i in range(2):
            video = make_color_video(tmp_path / f"v{i}.mp4", 1.0)
            audio = make_silence(tmp_path / f"a{i}.wav", 1.0)
            parts.append(align_and_mux(video, audio,
                                      Path(f"seg{i}.mp4")))
        out = concat(parts, Path("nested/final.mp4"))
        assert out.exists() and ffprobe_duration(out) > 1.5


class TestNormalizeForeign:
    def make_clip(self, path: Path, seconds: float, with_audio: bool) -> Path:
        import subprocess
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
               "-i", f"testsrc=duration={seconds}:size=320x240:rate=12"]
        if with_audio:
            cmd += ["-f", "lavfi", "-i",
                    f"sine=frequency=440:duration={seconds}"]
        # output options must come after every -i
        cmd += ["-pix_fmt", "yuv420p", "-c:v", "libx264"]
        if with_audio:
            cmd += ["-c:a", "aac", "-shortest"]
        cmd.append(str(path))
        subprocess.run(cmd, check=True)
        return path

    def _streams(self, path: Path) -> dict:
        import json
        import subprocess
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_type,width,height,avg_frame_rate",
             "-of", "json", str(path)],
            capture_output=True, text=True, check=True).stdout
        data = json.loads(out)["streams"]
        video = next(s for s in data if s["codec_type"] == "video")
        has_audio = any(s["codec_type"] == "audio" for s in data)
        return {"w": video["width"], "h": video["height"],
                "fps": video["avg_frame_rate"], "audio": has_audio}

    def test_scales_pads_and_adds_silent_audio(self, tmp_path):
        clip = self.make_clip(tmp_path / "in.mp4", 1.5, with_audio=False)
        out = normalize_foreign(clip, tmp_path / "out.mp4", 640, 480, 30)
        info = self._streams(out)
        assert (info["w"], info["h"]) == (640, 480)
        assert info["fps"].startswith("30")
        assert info["audio"] is True          # silent track added
        assert ffprobe_duration(out) == pytest.approx(1.5, abs=0.15)

    def test_keeps_existing_audio(self, tmp_path):
        clip = self.make_clip(tmp_path / "in2.mp4", 1.2, with_audio=True)
        assert has_audio_stream(clip) is True
        out = normalize_foreign(clip, tmp_path / "out2.mp4", 640, 480, 30)
        info = self._streams(out)
        assert info["audio"] is True
        assert (info["w"], info["h"]) == (640, 480)


class TestSmartConcat:
    def make_uniform(self, tmp_path, name, seconds):
        video = make_color_video(tmp_path / f"v_{name}.mp4", seconds)
        audio = make_silence(tmp_path / f"a_{name}.wav", seconds)
        return align_and_mux(video, audio, tmp_path / f"seg_{name}.mp4")

    def test_all_cuts_behave_like_concat(self, tmp_path):
        parts = [self.make_uniform(tmp_path, i, 2.0) for i in range(3)]
        out = smart_concat(parts, ["none", "carry-over"],
                           tmp_path / "final.mp4")
        assert ffprobe_duration(out) == pytest.approx(6.0, abs=0.2)

    def test_fade_junction_overlaps_by_fade_duration(self, tmp_path):
        a = self.make_uniform(tmp_path, "a", 3.0)
        b = self.make_uniform(tmp_path, "b", 3.0)
        out = crossfade_join(a, b, "fade", tmp_path / "xf.mp4",
                             duration=0.6)
        assert ffprobe_duration(out) == pytest.approx(5.4, abs=0.15)

    def test_mixed_cut_and_fade(self, tmp_path):
        a = self.make_uniform(tmp_path, "x", 2.0)
        b = self.make_uniform(tmp_path, "y", 2.0)
        c = self.make_uniform(tmp_path, "z", 2.0)
        out = smart_concat([a, b, c], ["fade", "carry-over"],
                           tmp_path / "mixed.mp4", fade_duration=0.5)
        # one crossfade removes 0.5s of overlap, the cut removes none
        assert ffprobe_duration(out) == pytest.approx(5.5, abs=0.25)

    def test_junction_count_validated(self, tmp_path):
        a = self.make_uniform(tmp_path, "first", 1.0)
        b = self.make_uniform(tmp_path, "second", 1.0)
        with pytest.raises(ComposeError):
            smart_concat([a, b], [], tmp_path / "bad.mp4")
