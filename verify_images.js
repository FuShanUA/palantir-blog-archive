const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto('https://fushanua.github.io/PBA/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(5000);

  // Get all card image sources and check which are broken
  const imgData = await page.evaluate(() => {
    const imgs = document.querySelectorAll('.card .thumb img');
    return Array.from(imgs).slice(0, 30).map(img => ({
      src: img.src,
      naturalWidth: img.naturalWidth,
      ok: img.naturalWidth > 0
    }));
  });
  
  const broken = imgData.filter(d => !d.ok);
  console.log(`Total checked: ${imgData.length}, broken: ${broken.length}`);
  broken.forEach(d => console.log(`  BROKEN: ${d.src.substring(0, 100)}`));

  await browser.close();
})().catch(e => { console.error(e.message); process.exit(1); });
