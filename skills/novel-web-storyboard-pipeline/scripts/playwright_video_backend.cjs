const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');

const playwrightPath = process.env.CODEX_PLAYWRIGHT_PATH
  || 'C:\\Users\\Y\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\playwright';
const { chromium } = require(playwrightPath);

async function loadVideo(page, input) {
  await page.goto(pathToFileURL(path.resolve(input)).href, { waitUntil: 'commit', timeout: 15000 });
  await page.waitForSelector('video', { timeout: 15000 });
  return page.evaluate(async () => {
    const video = document.querySelector('video');
    video.muted = true;
    if (video.readyState < 1) {
      await new Promise((resolve, reject) => {
        video.addEventListener('loadedmetadata', resolve, { once: true });
        video.addEventListener('error', () => reject(new Error('video metadata load failed')), { once: true });
      });
    }
    return { duration: video.duration, width: video.videoWidth, height: video.videoHeight };
  });
}

async function main() {
  const [mode, input, output] = process.argv.slice(2);
  if (!['inspect', 'extract-tail'].includes(mode) || !input || (mode === 'extract-tail' && !output)) {
    throw new Error('usage: node playwright_video_backend.cjs <inspect|extract-tail> <input.mp4> [output.png]');
  }
  const browser = await chromium.launch({
    channel: 'msedge',
    headless: true,
    args: ['--allow-file-access-from-files', '--autoplay-policy=no-user-gesture-required'],
  });
  try {
    const page = await browser.newPage();
    const meta = await loadVideo(page, input);
    if (mode === 'inspect') {
      process.stdout.write(JSON.stringify({
        path: path.resolve(input), readable: true, size_bytes: fs.statSync(input).size,
        frames: null, fps: null, duration_seconds: meta.duration,
        width: meta.width, height: meta.height, backend: 'playwright-msedge',
      }));
      return;
    }
    const dataUrl = await page.evaluate(async () => {
      const video = document.querySelector('video');
      const frameStep = 1 / 24;
      await new Promise((resolve, reject) => {
        video.addEventListener('seeked', resolve, { once: true });
        video.addEventListener('error', () => reject(new Error('video seek failed')), { once: true });
        video.currentTime = Math.max(0, video.duration - frameStep);
        setTimeout(() => reject(new Error('video seek timed out')), 10000);
      });
      await new Promise(resolve => setTimeout(resolve, 250));
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL('image/png');
    });
    const png = Buffer.from(dataUrl.split(',')[1], 'base64');
    fs.writeFileSync(output, png);
    process.stdout.write(JSON.stringify({ ok: true, input: path.resolve(input), output: path.resolve(output), backend: 'playwright-msedge', bytes: png.length }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { process.stderr.write(error.stack || String(error)); process.exit(1); });
