# Build.md — Phiversity Newton Ad Capture & Encode

## Overview

`newton-story.html` is a single-file Three.js r128 + GSAP 3.12.5 vertical ad (1080×1920, ~59.5s).
`capture.mjs` captures it frame-by-frame with Playwright + FFmpeg and muxes audio.

## Prerequisites

- Node.js 20+
- `npm install playwright` (Chromium browser downloaded automatically)
- FFmpeg 4.4+ with libx264 and aac encoders

## Files

| File | Purpose |
|------|---------|
| `newton-story.html` | Single-file ad (renders on open) |
| `capture.mjs` | Capture + encode pipeline |
| `assets/clips/moon-test.mp4` | Phiversity-rendered worked solution (17s) |
| `assets/fonts/LiberationSerif-Italic.ttf` | Notebook page text font |
| `newton-moon-test.mp4` | Final output |

## Running

```bash
# Install Playwright browser
npx playwright install chromium

# Capture and encode (takes ~6-8 min)
node capture.mjs newton-story.html newton-moon-test.mp4

# Output: newton-moon-test.mp4 (~3.5 MB, 59.5s, H.264/AAC)
```

## Pipeline Details

1. **Capture**: Chromium headless (viewport 1080×1920, deviceScaleFactor 1). For each of 1785 frames at 30 fps, `window.__seek(t)` is called then a JPEG q92 screenshot is streamed to ffmpeg stdin.
2. **Encode**: H.264 `yuv420p`, CRF 18, `+faststart`, BT.709 colour tags.
3. **Audio**: Brown noise wind bed, page rustle (22.8s), pen scratch (23.8–29.6s), soft music (-22 dB until 37.5s), chime (54.5s). Mixed and normalised to -14 LUFS / -1 dBTP.
4. **Mux**: Video + normalised AAC audio into final MP4.

## Determinism

`draw(t)` is a pure function of time. `window.__seek(t)` seeks to any time and produces identical pixels regardless of seek direction. No `Math.random`, no wall-clock time, no CSS animations.

## Known Limitations

- The quill tip is not separately animated; text is revealed via a clip rectangle on the canvas texture.
- The Moon is drawn larger than real size (per brief specification).
- The notebook text uses Liberation Serif Italic (IM Fell English Italic not available locally).
- The apple physics use a simplified scale factor (scene units are not real metres).
