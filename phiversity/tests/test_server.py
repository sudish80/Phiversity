import json
import threading
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pytest

from phiversity.server import RenderServer, make_handler
from http.server import ThreadingHTTPServer


@dataclass
class FakeResult:
    title: str
    final_video: Path


@pytest.fixture()
def site(tmp_path, monkeypatch):
    frontend = tmp_path / "Frontend"
    frontend.mkdir()
    (frontend / "index.html").write_text("<html>landing</html>")
    (frontend / "app.html").write_text("<html>app</html>")
    lectures = tmp_path / "lectures"
    slug = "demo-test"
    (lectures / slug).mkdir(parents=True)
    (lectures / slug / "lecture.mp4").write_bytes(b"0123456789abcdef")
    (lectures / slug / "manifest.json").write_text(json.dumps({
        "title": "Test Lecture", "question": "2+2?",
        "format": "numerical", "theme": {"preset": "math"},
        "segments": [{"voice_seconds": 5.0}, {"voice_seconds": 4.5}]}))

    # a fake pipeline so tests never render manim
    import phiversity.server as server_mod

    def fake_run_pipeline(cfg, log=print):
        log("[1/5] plan : fake")
        log("[4/5] render: Segment0 (voice 5.0s)")
        out = Path(cfg.out_dir) / "demo-test" / "lecture.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"0123456789abcdef")
        log(f"done  : {out}")
        return FakeResult("Test Lecture", out)

    monkeypatch.setattr(server_mod, "run_pipeline", fake_run_pipeline)

    render_server = RenderServer(frontend, lectures,
                                 tmp_path / "chat-thread.json")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0),
                                make_handler(render_server))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", render_server
    httpd.shutdown()


def get(base, path, headers=None):
    req = urllib.request.Request(base + path, headers=headers or {})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, dict(resp.headers), resp.read()


def post(base, path, body):
    req = urllib.request.Request(
        base + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


class TestStaticAndConfig:
    def test_serves_index(self, site):
        base, _ = site
        status, _, body = get(base, "/")
        assert status == 200 and b"landing" in body

    def test_serves_nested_page(self, site):
        base, _ = site
        status, _, body = get(base, "/app.html")
        assert status == 200 and b"app" in body

    def test_player_assets_served(self, site, tmp_path):
        """The phi-player previewer must be present in the shared assets.

        The fixture frontend is a stub, so write the real files into it
        first - the server reads them from disk per request.
        """
        import shutil
        real = Path(__file__).resolve().parents[2] / "Frontend" / "assets"
        app_js = real / "app.js"
        style = real / "style.css"
        if not app_js.is_file():
            pytest.skip("frontend assets not found")
        base, server = site
        shutil.copyfile(app_js, server.frontend / "app.js")
        shutil.copyfile(style, server.frontend / "style.css")
        _, _, js = get(base, "/app.js")
        _, _, css = get(base, "/style.css")
        assert b"lfPlayer" in js                      # player factory
        assert b"requestFullscreen" in js              # fullscreen control
        assert b".phi-player" in css                   # player styles

    def test_wired_pages_use_the_player(self, site):
        base, server = site
        import shutil
        real = Path(__file__).resolve().parents[2] / "Frontend"
        for rel in ("app/generate/item.html", "app/library.html",
                    "app/recent.html"):
            source = real / rel
            if not source.is_file():
                pytest.skip("frontend page not found")
            target = server.frontend / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        _, _, item = get(base, "/app/generate/item.html")
        _, _, library = get(base, "/app/library.html")
        assert b"lfPlayer" in item and b"playerbox" in item
        assert b"lfPlayer" in library

    def test_chat_page_served_and_wired(self, site):
        """The Phiversity chat UI is the chat + video-generation front end:
        it must boot against /api/config, POST /api/generate, poll jobs,
        and play results through the phi-player - with the canned canvas
        demo kept only as the offline fallback."""
        base, server = site
        import shutil
        real = Path(__file__).resolve().parents[2] / "Frontend"
        if not (real / "chat.html").is_file():
            pytest.skip("chat page not found")
        for rel in ("chat.html", "assets/app.js", "login.html"):
            source = real / rel
            target = server.frontend / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        _, _, page = get(base, "/chat.html")
        assert b"Phiversity Chat" in page
        for marker in (b"/api/config", b"/api/generate", b"/api/jobs/",
                       b"/api/chats", b"lfPlayer", b"cannedAnswer",
                       b"trackJob", b"openVideo", b"assets/app.js",
                       b'id="drawer"', b"Recent chats", b"chatRow"):
            assert marker in page, marker
        _, _, login_page = get(base, "/login.html")
        assert b"location='chat.html'" in login_page  # lands in the chat

        _, _, app_js = get(base, "/assets/app.js")
        # the sidebar navigation is gone entirely: app pages are bare
        assert b"LF_NAV" not in app_js
        assert b"lfnav" not in app_js

    def test_sample_page_is_a_video_grid(self, site):
        """Sample lectures show the actual topic videos, YouTube-style."""
        base, server = site
        import shutil
        real = Path(__file__).resolve().parents[2] / "Frontend"
        for rel in ("app/templates.html", "assets/app.js"):
            source = real / rel
            if not source.is_file():
                pytest.skip("frontend page not found")
            target = server.frontend / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        _, _, page = get(base, "/app/templates.html")
        assert b"/api/config" in page and b"/api/lectures" in page
        assert b"lfPlayer" in page          # videos embedded directly
        assert b"demo-" in page             # topics matched to their videos
        assert b"Regenerate" not in page    # clean cards: no meta row/tags

    def test_traversal_is_refused(self, site):
        base, _ = site
        # must never expose files outside the frontend folder
        status, _, body = get(base, "/../../etc/passwd")
        assert b"root:" not in body

    def test_config_lists_topics(self, site):
        base, _ = site
        config = json.loads(urllib.request.urlopen(
            base + "/api/config", timeout=10).read())
        topics = [t["topic"] for t in config["topics"]]
        assert "pythagoras" in topics and "methane" in topics
        assert config["themes"] and config["voices"]


class TestLectures:
    def test_lists_generated_lectures(self, site):
        base, _ = site
        data = json.loads(urllib.request.urlopen(
            base + "/api/lectures", timeout=10).read())
        assert data["lectures"][0]["slug"] == "demo-test"
        assert data["lectures"][0]["narration_seconds"] == 9.5
        assert data["lectures"][0]["format"] == "numerical"

    def test_video_full_download(self, site):
        base, _ = site
        status, headers, body = get(base, "/api/lectures/demo-test/video")
        assert status == 200 and body == b"0123456789abcdef"
        assert headers["Accept-Ranges"] == "bytes"

    def test_video_range_request(self, site):
        base, _ = site
        status, headers, body = get(
            base, "/api/lectures/demo-test/video",
            headers={"Range": "bytes=4-7"})
        assert status == 206
        assert body == b"4567"
        assert headers["Content-Range"] == "bytes 4-7/16"

    def test_unknown_lecture_404(self, site):
        base, _ = site
        with pytest.raises(urllib.error.HTTPError):
            get(base, "/api/lectures/nope/video")


class TestSearchStatusDelete:
    def test_search_filters_by_text(self, site):
        base, _ = site
        data = json.loads(urllib.request.urlopen(
            base + "/api/search?q=Test", timeout=10).read())
        assert len(data["lectures"]) == 1
        data = json.loads(urllib.request.urlopen(
            base + "/api/search?q=nothing-matches-this",
            timeout=10).read())
        assert data["lectures"] == []
        data = json.loads(urllib.request.urlopen(
            base + "/api/search?q=", timeout=10).read())
        assert len(data["lectures"]) == 1   # empty query = everything

    def test_status_reports_health(self, site):
        base, _ = site
        status = json.loads(urllib.request.urlopen(
            base + "/api/status", timeout=10).read())
        assert status["server"] == "ok"
        assert status["generated_lectures"] >= 1
        assert status["sample_lectures"] >= 5
        assert isinstance(status["llm_configured"], bool)
        assert status["ffmpeg"] is True and status["manim"] is True

    def test_delete_lecture(self, site):
        base, server = site
        slug = "to-delete"
        target = server.lectures_dir / slug
        target.mkdir(parents=True)
        (target / "lecture.mp4").write_bytes(b"x")
        (target / "manifest.json").write_text(json.dumps(
            {"title": "Doomed", "segments": []}))
        status, headers, _ = get(base, f"/api/lectures/{slug}/video")
        assert status == 200
        req = urllib.request.Request(
            f"{base}/api/lectures/{slug}", method="DELETE")
        with urllib.request.urlopen(req, timeout=10) as resp:
            assert json.loads(resp.read())["deleted"] == slug
        assert not target.exists()
        with pytest.raises(urllib.error.HTTPError):
            get(base, f"/api/lectures/{slug}/video")

    def test_delete_rejects_bad_slugs(self, site):
        base, _ = site
        for bad in ("../lectures", "sub/dir", ".hidden"):
            req = urllib.request.Request(
                f"{base}/api/lectures/{bad}", method="DELETE")
            with pytest.raises(urllib.error.HTTPError):
                urllib.request.urlopen(req, timeout=10)


class TestChatPersistence:
    def test_thread_round_trip(self, site):
        """The chat transcript persists on disk (videos are referenced by
        URL only - they are never copied into the thread)."""
        base, _ = site
        assert json.loads(urllib.request.urlopen(
            base + "/api/chat", timeout=10).read())["messages"] == []
        messages = [{"role": "user", "text": "explain friction"},
                    {"role": "bot", "kind": "job", "id": "abc",
                     "text": "Generating...", "status": "done",
                     "video": "/api/lectures/demo-test/video"}]
        status, body = post(base, "/api/chat", {"messages": messages})
        assert status == 200 and body["ok"] is True
        loaded = json.loads(urllib.request.urlopen(
            base + "/api/chat", timeout=10).read())["messages"]
        assert loaded == messages

    def test_thread_survives_server_restart(self, tmp_path):
        from phiversity.server import RenderServer
        chat_file = tmp_path / "chat-thread.json"
        one = RenderServer(tmp_path / "f1", tmp_path / "l1", chat_file)
        one.save_chat([{"role": "user", "text": "hello"}])
        two = RenderServer(tmp_path / "f1", tmp_path / "l1", chat_file)
        assert two.load_chat() == [{"role": "user", "text": "hello"}]

    def test_clear_thread(self, site):
        base, server = site
        post(base, "/api/chat", {"messages": [{"role": "user",
                                               "text": "x"}]})
        req = urllib.request.Request(base + "/api/chat", method="DELETE")
        urllib.request.urlopen(req, timeout=10)
        assert server.load_chat() == []

    def test_invalid_thread_rejected(self, site):
        base, _ = site
        req = urllib.request.Request(
            base + "/api/chat", data=b'{"messages": "not a list"}',
            headers={"Content-Type": "application/json"})
        with pytest.raises(urllib.error.HTTPError):
            urllib.request.urlopen(req, timeout=10)


class TestSavedChats:
    MESSAGES = [
        {"role": "user", "text": "explain the quadratic"},
        {"role": "bot", "kind": "job", "id": "j1", "status": "done",
         "text": "Generating...", "video": "/api/lectures/demo-test/video",
         "title": "Test Lecture"},
    ]

    def test_chat_crud(self, site):
        base, _ = site
        # create two chats
        status, body = post(base, "/api/chats/chat-one",
                            {"title": "Quadratic chat",
                             "messages": self.MESSAGES})
        assert status == 200 and body["id"] == "chat-one"
        post(base, "/api/chats/chat-two",
             {"title": None,
              "messages": [{"role": "user", "text": "hello springs"}]})
        # listing: newest first, with video references
        data = json.loads(urllib.request.urlopen(
            base + "/api/chats", timeout=10).read())
        ids = [c["id"] for c in data["chats"]]
        assert ids == ["chat-two", "chat-one"]
        one = next(c for c in data["chats"] if c["id"] == "chat-one")
        assert one["title"] == "Quadratic chat"
        assert one["messages"] == 2
        assert one["videos"] == [{"title": "Test Lecture",
                                  "video": "/api/lectures/demo-test/video"}]
        two = next(c for c in data["chats"] if c["id"] == "chat-two")
        assert two["title"] == "hello springs"   # from first user message
        # full load
        full = json.loads(urllib.request.urlopen(
            base + "/api/chats/chat-one", timeout=10).read())
        assert full["messages"] == self.MESSAGES
        # delete one
        req = urllib.request.Request(base + "/api/chats/chat-two",
                                     method="DELETE")
        urllib.request.urlopen(req, timeout=10)
        with pytest.raises(urllib.error.HTTPError):
            get(base, "/api/chats/chat-two")

    def test_bad_chat_ids_rejected(self, site):
        base, _ = site
        status, _ = post(base, "/api/chats/../evil", {"messages": []})
        assert status in (400, 404)
        status, _ = post(base, "/api/chats/sub/dir", {"messages": []})
        assert status in (400, 404)
        with pytest.raises(urllib.error.HTTPError):
            get(base, "/api/chats/missing-chat")

    def test_legacy_thread_migrates_into_chats(self, tmp_path):
        from phiversity.server import RenderServer
        legacy = tmp_path / "chat-thread.json"
        legacy.write_text(json.dumps(
            {"messages": [{"role": "user", "text": "old question"}]}))
        server = RenderServer(tmp_path / "f", tmp_path / "l", legacy)
        chats = server.list_chats()
        assert len(chats) == 1
        assert chats[0]["id"] == "imported"
        assert chats[0]["title"] == "old question"
        # the JSON thread file becomes the SQLite database itself
        from phiversity.db import is_sqlite_file
        assert is_sqlite_file(legacy)
        assert server.list_chats()[0]["id"] == "imported"


class TestJobs:
    def test_generate_requires_question_or_topic(self, site):
        base, _ = site
        status, body = post(base, "/api/generate", {})
        assert status == 400 and "question" in body["error"]

    def test_generate_rejects_unknown_topic(self, site):
        base, _ = site
        status, body = post(base, "/api/generate",
                            {"topic": "quantum-entanglement"})
        assert status == 400 and "no bundled lecture" in body["error"]

    def test_job_lifecycle(self, site):
        base, server = site
        status, body = post(base, "/api/generate",
                            {"question": "what is 2+2?", "quality": "l"})
        assert status == 202
        job_id = body["id"]
        job = None
        for _ in range(50):
            job = server.get_job(job_id)
            if job.status == "done":
                break
            time.sleep(0.1)
        assert job.status == "done"
        assert job.video == "/api/lectures/demo-test/video"
        assert job.title == "Test Lecture"
        assert any("[4/5] render" in line for line in job.logs)
        # and it is queryable over HTTP
        data = json.loads(urllib.request.urlopen(
            f"{base}/api/jobs/{job_id}", timeout=10).read())
        assert data["status"] == "done" and data["progress"] == 100

    def test_job_autodetects_brand_intro(self, site):
        """API jobs must auto-detect Intro.mp4 exactly like the CLI, so the
        user's brand clip plays instead of the generic title card."""
        import phiversity.server as server_mod

        base, server = site
        (server.lectures_dir.parent / "Intro.mp4").write_bytes(b"intro")
        seen = {}

        def probe(cfg, log=print):
            seen["intro_clip"] = cfg.intro_clip
            return server_mod.run_pipeline.__wrapped__(cfg, log=log) \
                if hasattr(server_mod.run_pipeline, "__wrapped__") \
                else None

        original = server_mod.run_pipeline

        def recording(cfg, log=print):
            seen["intro_clip"] = cfg.intro_clip
            return original(cfg, log=log)

        server_mod.run_pipeline = recording
        try:
            post(base, "/api/generate", {"question": "branding?"})
            for _ in range(50):
                if "intro_clip" in seen:
                    break
                time.sleep(0.1)
        finally:
            server_mod.run_pipeline = original
        assert seen["intro_clip"] == "Intro.mp4"

    def test_jobs_listing(self, site):
        base, server = site
        post(base, "/api/generate", {"question": "q1"})
        data = json.loads(urllib.request.urlopen(
            base + "/api/jobs", timeout=10).read())
        assert len(data["jobs"]) >= 1

class TestDatabase:
    def test_jobs_survive_server_restart(self, site):
        """Jobs persist in SQLite: a restart keeps history and marks
        still-running renders as interrupted."""
        import phiversity.server as server_mod
        base, server = site
        post(base, "/api/generate", {"question": "persist me"})
        job = None
        for _ in range(50):
            jobs = [j for j in server.list_jobs()
                    if j["question"] == "persist me"]
            if jobs and jobs[0]["status"] == "done":
                job = jobs[0]
                break
            time.sleep(0.1)
        assert job is not None
        db_path = server.db.path
        server.db.close()
        revived = server_mod.RenderServer(server.frontend,
                                           server.lectures_dir, db_path)
        restored = [j for j in revived.list_jobs()
                    if j["question"] == "persist me"]
        assert restored and restored[0]["status"] == "done"
        assert restored[0]["video"] == "/api/lectures/demo-test/video"
        revived.db.close()

    def test_running_jobs_marked_interrupted(self, tmp_path):
        import phiversity.server as server_mod
        from phiversity.db import Database
        db_path = tmp_path / "phiversity.db"
        db = Database(db_path)
        db.save_job({"id": "zombie", "created": time.time(),
                     "status": "running", "stage": "render",
                     "progress": 58, "title": "", "question": "q",
                     "topic": "", "video": "", "error": "", "logs": []})
        db.close()
        revived = server_mod.RenderServer(tmp_path / "f",
                                          tmp_path / "l", db_path)
        job = revived.get_job("zombie")
        assert job is not None
        assert job.status == "error"
        assert "interrupted" in job.error
        revived.db.close()

    def test_lecture_index_syncs_with_disk(self, tmp_path):
        import shutil as shutil_mod
        import phiversity.server as server_mod
        lectures = tmp_path / "lectures"
        slug = "demo-sync"
        (lectures / slug).mkdir(parents=True)
        (lectures / slug / "lecture.mp4").write_bytes(b"x")
        (lectures / slug / "manifest.json").write_text(json.dumps(
            {"title": "Synced", "question": "q?", "format": "numerical",
             "theme": {"preset": "math"},
             "segments": [{"voice_seconds": 3.0}]}))
        server = server_mod.RenderServer(tmp_path / "f", lectures,
                                         tmp_path / "db.sqlite")
        rows = server.list_lectures()
        assert rows[0]["slug"] == slug and rows[0]["title"] == "Synced"
        assert rows[0]["narration_seconds"] == 3.0
        server.db.close()
        shutil_mod.rmtree(lectures / slug)
        server = server_mod.RenderServer(tmp_path / "f", lectures,
                                         tmp_path / "db.sqlite")
        assert server.list_lectures() == []
        server.db.close()

    def test_legacy_chat_files_migrate_into_db(self, tmp_path):
        import phiversity.server as server_mod
        chats = tmp_path / "chats"
        chats.mkdir()
        (chats / "abc.json").write_text(json.dumps(
            {"title": "Old chat", "modified": 123.0,
             "messages": [{"role": "user", "text": "hi"}]}))
        server = server_mod.RenderServer(tmp_path / "f", tmp_path / "l",
                                         tmp_path / "phiversity.db")
        summaries = server.list_chats()
        assert [c["id"] for c in summaries] == ["abc"]
        assert summaries[0]["title"] == "Old chat"
        assert not (chats / "abc.json").exists()   # migrated once
        server.db.close()

class TestFollowUps:
    def make_lecture(self, lectures, slug, scenes):
        import shutil as shutil_mod
        d = lectures / slug
        (d / "work" / "segments").mkdir(parents=True, exist_ok=True)
        (d / "lecture.mp4").write_bytes(b"full")
        segs = []
        for i, (scene, narration) in enumerate(scenes):
            (d / "work" / "segments" / f"{scene}.mp4").write_bytes(b"seg")
            segs.append({"scene": scene, "narration": narration,
                         "voice_seconds": 2.0 + i})
        (d / "manifest.json").write_text(json.dumps(
            {"title": "Base Lecture", "format": "conceptual",
             "theme": {"preset": "math"}, "segments": segs}))
        return d

    def test_followup_extends_existing_lecture(self, site, monkeypatch):
        import phiversity.pipeline as pl
        import phiversity.server as server_mod
        base, server = site

        # a finished lecture + its done job on the record
        self.make_lecture(server.lectures_dir, "demo-base",
                          [("Segment0", "first beat"),
                           ("Segment1", "second beat")])
        # the anchor job is known only to the database (not in memory),
        # so follow-up resolution has to go through SQLite
        server.db.save_job({"id": "job-old", "created": time.time(),
                            "status": "done", "stage": "compose",
                            "progress": 100, "title": "Base Lecture",
                            "question": "base", "topic": "",
                            "video": "/api/lectures/demo-base/video",
                            "error": "", "logs": []})

        # patch the heavy pipeline internals: TTS, render, mux, stitch
        from pathlib import Path as P
        def fake_synth(text, out, cfg):
            out = P(out); out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"wav")
            return out, 5.0
        def fake_render(code, name, workdir, cfg, client=None, kit="",
                        log=print):
            # a real (tiny) mp4 so ffprobe/edge-clip checks behave
            out = P(workdir) / f"{name}.mp4"
            out.parent.mkdir(parents=True, exist_ok=True)
            import subprocess
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
                 "-i", "color=c=0x101319:s=320x180:d=1",
                 "-pix_fmt", "yuv420p", "-c:v", "libx264", str(out)],
                check=True)
            return out
        def fake_align(video, audio, out, srt=None):
            out = P(out); out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"aligned")
            return out
        def fake_concat(parts, junctions=None, out=None):
            out = P(out if out is not None else parts[0])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(b"stitched")
            return out
        monkeypatch.setattr(pl, "synthesize", fake_synth)
        monkeypatch.setattr(pl, "render_with_healing", fake_render)
        monkeypatch.setattr(pl, "align_and_mux", fake_align)
        monkeypatch.setattr(pl, "smart_concat", fake_concat)

        class FakeLLM:
            def plan_followup(self, question, title, previous,
                              max_segments=3, start_index=0):
                assert "first beat" in previous
                return {"title": title, "question": None,
                        "preset": "math", "format": "conceptual",
                        "segments": [
                            {"narration": "the follow-up beat",
                             "visual": {"objective": "answer follow-up"}}]}
            def code_scenes(self, title, segments, latex=True,
                            playbook="", lesson_format=""):
                return ["from manim import *\n\n\nclass Segment2(Scene):\n"
                        "    def construct(self):\n"
                        "        self.add(Text('x'))\n        self.wait(1)\n"]

        monkeypatch.setattr(server_mod, "LLMClient", lambda cfg: FakeLLM())
        monkeypatch.setenv("LLM_API_KEY", "test-key")

        status, body = post(base, "/api/generate",
                            {"question": "now explain it more deeply",
                             "follow_up_of": "job-old"})
        assert status == 202
        for _ in range(80):
            job = server.get_job(body["id"])
            if job.status in ("done", "error"):
                break
            time.sleep(0.1)
        assert job.status == "done", job.error
        assert job.video == "/api/lectures/demo-base/video"
        manifest = json.loads(
            (server.lectures_dir / "demo-base" / "manifest.json"
             ).read_text())
        narrations = [s["narration"] for s in manifest["segments"]]
        assert narrations[:2] == ["first beat", "second beat"]
        assert narrations[2] == "the follow-up beat"
        assert manifest["segments"][2]["scene"] == "Segment2"
        server.db.close()

    def test_followup_falls_back_to_fresh(self, site):
        base, server = site
        status, body = post(base, "/api/generate",
                            {"question": "fresh question",
                             "follow_up_of": "does-not-exist"})
        assert status == 202
        job = None
        for _ in range(50):
            job = server.get_job(body["id"])
            if job.status in ("done", "error"):
                break
            time.sleep(0.1)
        assert job.status == "done"
        assert any("fresh lecture" in line for line in job.logs)
        server.db.close()
