// Record tiktok/assets/outro/youtube-outro-anim.html into a 1920x1080, 30fps video, frame by frame.
// Usage: node tiktok/record_outro.js <html> <framesDir>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [html, dir] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.addInitScript(() => { window.__CAPTURE_MODE__ = true; });
  await page.goto('file://' + path.resolve(html));
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => { window.__born = new WeakMap(); });
  const FPS = 30, DUR = 8.0;
  for (let i = 0; i < FPS * DUR; i++) {
    const t = i / FPS;
    await page.evaluate((t) => {
      window.setAnimTime(t);
      // freeze every CSS transition/animation at the right point for time t
      for (const a of document.getAnimations()) {
        if (!window.__born.has(a)) window.__born.set(a, t);
        a.pause();
        a.currentTime = (t - window.__born.get(a)) * 1000;
      }
    }, t);
    await page.screenshot({ path: path.join(dir, `f${String(i).padStart(4, '0')}.png`) });
  }
  await browser.close();
})();
