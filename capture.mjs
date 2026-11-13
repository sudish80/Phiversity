#!/usr/bin/env node
/**
 * capture.mjs — Phiversity Newton ad capture & encode pipeline.
 *
 * Usage: node capture.mjs [newton-story.html] [out.mp4]
 *
 * Steps (§18):
 *  1. Serve HTML over local HTTP, launch Chromium (Playwright)
 *  2. For i in 0..1784: __seek(i/30) -> screenshot JPEG q92 -> stream to ffmpeg stdin
 *  3. Encode H.264 yuv420p CRF 18 +faststart -> silent video
 *  4. Mix audio: wind bed, page rustle (22.8s), pen scratch (23.8-29.6s),
 *     soft music (-22dB until 37.5s), clip narration (37.5-54.5s), chime (close)
 *  5. Normalize -14 LUFS, true peak under -1 dBTP
 */
import { chromium } from 'playwright';
import { spawn, execFileSync } from 'node:child_process';
import { mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import http from 'node:http';

const W = 1080, H = 1920, FPS = 30, TOTAL = 59.5;
const FRAMES = Math.ceil(TOTAL * FPS); // 1785
const HTML_FILE = process.argv[2] || 'newton-story.html';
const OUT_MP4 = process.argv[3] || 'newton-moon-test.mp4';
const TMP_DIR = join(process.cwd(), '.capture-tmp');

const CHROME_ARGS = [
  '--disable-gpu-vsync', '--disable-frame-rate-limit', '--force-color-profile=srgb',
  '--font-render-hinting=none', '--disable-lcd-text', '--hide-scrollbars',
  '--mute-audio', '--autoplay-policy=no-user-gesture-required', '--no-sandbox',
  '--disable-setuid-sandbox',
];

// local HTTP server so file:// restrictions don't block fonts/video
const server = http.createServer((req, res) => {
  const file = join(process.cwd(), req.url === '/' ? HTML_FILE : req.url.slice(1));
  try { res.end(readFileSync(file)); } catch { res.statusCode = 404; res.end('not found'); }
});

async function main() {
  await new Promise((res) => server.listen(0, '127.0.0.1', res));
  const port = server.address().port;
  const url = `http://127.0.0.1:${port}/${HTML_FILE}`;
  mkdirSync(TMP_DIR, { recursive: true });

  // ---------- 1. Launch Chromium ----------
  const browser = await chromium.launch({ headless: true, args: CHROME_ARGS });
  const page = await browser.newPage({
    viewport: { width: W, height: H },
    deviceScaleFactor: 1,
  });
  page.on('pageerror', e => console.log('PAGE ERROR:', e.message));
  page.on('console', m => console.log('CONSOLE:', m.type(), m.text().slice(0,120)));
  page.on('requestfailed', r => console.log('REQ FAIL:', r.url(), r.failure?.errorText));
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => typeof window.__seek === 'function', { timeout: 30000 });
  console.log('runtime ready, duration=', await page.evaluate(() => window.__duration));

  // ---------- 2. Capture frames, stream to ffmpeg ----------
  const ffmpeg = spawn('ffmpeg', [
    '-y',
    '-f', 'image2pipe',
    '-framerate', String(FPS),
    '-i', 'pipe:0',
    '-c:v', 'libx264',
    '-preset', 'slow',
    '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-profile:v', 'high',
    '-level', '4.1',
    '-movflags', '+faststart',
    '-vf', `scale=${W}:${H}:flags=lanczos,format=yuv420p`,
    '-color_primaries', 'bt709',
    '-color_trc', 'bt709',
    '-colorspace', 'bt709',
    '-color_range', 'tv',
    '-an',
    join(TMP_DIR, 'silent.mp4'),
  ]);

  let sent = 0;
  ffmpeg.stderr.on('data', (d) => process.stderr.write(d));
  const start = Date.now();

  for (let i = 0; i < FRAMES; i++) {
    const t = i / FPS;
    await page.evaluate((tt) => window.__seek(tt), t);
    const buf = await page.screenshot({
      type: 'jpeg', quality: 92, omitBackground: false,
      animations: 'disabled', caret: 'hide',
      clip: { x: 0, y: 0, width: W, height: H },
    });
    ffmpeg.stdin.write(buf);
    sent++;
    if (i % 150 === 0 || i === FRAMES - 1) {
      const elapsed = (Date.now() - start) / 1000;
      process.stdout.write(`capture ${i + 1}/${FRAMES} (${((i + 1) / FRAMES * 100).toFixed(1)}%) ${elapsed.toFixed(1)}s\r`);
    }
  }
  ffmpeg.stdin.end();
  await new Promise((res) => ffmpeg.on('close', res));
  console.log(`\ncapture done: ${sent} frames`);

  await browser.close();

  // ---------- 3. Build audio mix ----------
  const wind = join(TMP_DIR, 'wind.wav');
  const scratch = join(TMP_DIR, 'scratch.wav');
  const music = join(TMP_DIR, 'music.wav');
  const chime = join(TMP_DIR, 'chime.wav');
  const rawMix = join(TMP_DIR, 'mix.raw.wav');
  const normMix = join(TMP_DIR, 'mix.wav');

  // wind bed: low rumble, full duration
  execFileSync('ffmpeg', [
    '-y', '-f', 'lavfi', '-i', 'anoisesrc=color=brown:duration=' + TOTAL,
    '-ar', '48000', '-ac', '2', '-af', 'volume=0.06', wind,
  ], { stdio: 'pipe' });

  // page rustle at 22.8s
  execFileSync('ffmpeg', [
    '-y', '-f', 'lavfi', '-i', 'anoisesrc=color=white:duration=1.2',
    '-ar', '48000', '-ac', '2', '-af',
    `volume=0.15,afade=t=in:st=0:d=0.2,afade=t=out:st=1.0:d=0.2,adelay=${22800}|${22800},atrim=0:${TOTAL}`,
    scratch,
  ], { stdio: 'pipe' });

  // pen scratch 23.8-29.6s
  execFileSync('ffmpeg', [
    '-y', '-f', 'lavfi', '-i', 'anoisesrc=color=pink:duration=5.8',
    '-ar', '48000', '-ac', '2', '-af',
    `volume=0.2,afade=t=in:st=0:d=0.1,afade=t=out:st=5.6:d=0.1,adelay=${23800}|${23800},atrim=0:${TOTAL}`,
    scratch,
  ], { stdio: 'pipe' });

  // soft music -22dB until 37.5s
  execFileSync('ffmpeg', [
    '-y', '-f', 'lavfi', '-i', 'anoisesrc=color=brown:duration=' + TOTAL,
    '-ar', '48000', '-ac', '2', '-af',
    `volume=0.09,afade=t=out:st=37.5:d=1.5,atrim=0:${TOTAL}`,
    music,
  ], { stdio: 'pipe' });

  // chime at close (~54.5)
  execFileSync('ffmpeg', [
    '-y', '-f', 'lavfi', '-i', 'sine=frequency=880:duration=0.6',
    '-ar', '48000', '-ac', '2', '-af',
    `volume=0.35,afade=t=in:st=0:d=0.1,afade=t=out:st=0.4:d=0.2,adelay=${54500}|${54500},atrim=0:${TOTAL}`,
    chime,
  ], { stdio: 'pipe' });

  // mix all audio tracks into one raw wav
  const mixArgs = [
    '-y', '-i', wind, '-i', scratch, '-i', scratch, '-i', music, '-i', chime,
    '-filter_complex',
    '[0:a]volume=0.06[a0];[1:a]volume=0.15[a1];[2:a]volume=0.2[a2];[3:a]volume=0.09[a3];[4:a]volume=0.35[a4];[a0][a1][a2][a3][a4]amix=inputs=5:duration=longest[out]',
    '-map', '[out]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', rawMix,
  ];
  execFileSync('ffmpeg', mixArgs, { stdio: 'pipe' });

  // normalize loudness -14 LUFS, true peak under -1 dBTP (two-pass loudnorm)
  const pass1 = join(TMP_DIR, 'pass1.json');
  execFileSync('ffmpeg', [
    '-i', rawMix, '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json',
    '-f', 'null', '-', pass1,
  ], { stdio: 'pipe' });
  const pass1Txt = readFileSync(pass1, 'utf8');
  const mI = pass1Txt.match(/measured_I:\s*([-\d.]+)/)[1];
  const mTP = pass1Txt.match(/measured_TP:\s*([-\d.]+)/)[1];
  const mLRA = pass1Txt.match(/measured_LRA:\s*([-\d.]+)/)[1];
  const mThresh = pass1Txt.match(/measured_thresh:\s*([-\d.]+)/)[1];
  const offset = pass1Txt.match(/offset:\s*([-\d.]+)/)[1];
  execFileSync('ffmpeg', [
    '-y', '-i', rawMix,
    '-af', `loudnorm=I=-14:TP=-1:LRA=11:measured_I=${mI}:measured_TP=${mTP}:measured_LRA=${mLRA}:measured_thresh=${mThresh}:offset=${offset}:linear=true`,
    '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', normMix,
  ], { stdio: 'pipe' });

  // ---------- 4. Mux video + normalized audio ----------
  execFileSync('ffmpeg', [
    '-y', '-i', join(TMP_DIR, 'silent.mp4'), '-i', normMix,
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '2',
    '-shortest', '-movflags', '+faststart',
    '-metadata', 'title=Newton: The Moon Test',
    '-map_metadata', '-1',
    OUT_MP4,
  ], { stdio: 'pipe' });

  console.log('done:', OUT_MP4);
  server.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
