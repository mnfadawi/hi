import puppeteer from 'puppeteer';

const browser = await puppeteer.launch({
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
  headless: true
});
const page = await browser.newPage();
await page.setViewport({ width: 600, height: 1050 });
await page.goto('file:///home/user/hi/eid-al-adha-flyer.html', { waitUntil: 'networkidle0', timeout: 20000 });
await new Promise(r => setTimeout(r, 2000));
const flyer = await page.$('.flyer');
await flyer.screenshot({ path: '/home/user/hi/flyer-preview.png' });
await browser.close();
console.log('screenshot saved');
