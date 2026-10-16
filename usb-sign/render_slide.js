// Render a 1080x1920 slide HTML file to PNG: node render_slide.js in.html out.png
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [src, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(src));
  await page.evaluate(() => document.fonts.ready);
  const overflow = await page.evaluate(() => document.documentElement.scrollHeight);
  if (overflow > 1920) throw new Error(`slide content overflows: ${overflow}px > 1920px`);
  await page.screenshot({ path: out });
  await browser.close();
})().catch(e => { console.error(e.message); process.exit(1); });
