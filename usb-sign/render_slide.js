// Render a 1080x1920 slide HTML file to PNG: node render_slide.js in.html out.png [lit.png]
// With lit.png, also renders the page with <body class="lit"> and prints the
// [data-pulse] element's box as JSON, so build.py can make it glow.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [src, out, lit] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(src));
  await page.evaluate(() => document.fonts.ready);
  const overflow = await page.evaluate(() => document.documentElement.scrollHeight);
  if (overflow > 1920) throw new Error(`slide content overflows: ${overflow}px > 1920px`);
  await page.screenshot({ path: out });
  if (lit) {
    const box = await page.evaluate(() => {
      const r = document.querySelector('[data-pulse]').getBoundingClientRect();
      return { x: r.x, y: r.y, w: r.width, h: r.height };
    });
    await page.evaluate(() => document.body.classList.add('lit'));
    await page.screenshot({ path: lit });
    console.log(JSON.stringify(box));
  }
  await browser.close();
})().catch(e => { console.error(e.message); process.exit(1); });
