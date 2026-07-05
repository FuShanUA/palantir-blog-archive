const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto('https://fushanua.github.io/PBA/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(5000);

  const cards = await page.locator('.card').all();
  let websiteCards = 0, withDate = 0;
  for (const card of cards.slice(0, 30)) {
    const meta = await card.locator('.meta').textContent().catch(() => '');
    const badge = await card.locator('.source-badge').textContent().catch(() => '');
    if (badge && badge.includes('Website')) {
      websiteCards++;
      if (meta && !meta.includes('归档') && /\d{4}/.test(meta)) withDate++;
    }
  }
  console.log(`Website cards in first 30: ${websiteCards}, with real date: ${withDate}`);

  const imgs = await page.locator('.card .thumb img').all();
  let broken = 0;
  for (const img of imgs.slice(0, 20)) {
    const nw = await img.evaluate(el => el.naturalWidth).catch(() => 0);
    if (nw === 0) broken++;
  }
  console.log(`Thumbnails checked: ${Math.min(20, imgs.length)}, broken: ${broken}`);

  const newsroomHeader = page.locator('.acc-header').filter({ hasText: /新闻|Newsroom/ }).first();
  if (await newsroomHeader.count() > 0) {
    await newsroomHeader.click();
    await page.waitForTimeout(1000);
    const titles = await page.locator('.card .ttl').allTextContents();
    const hasQ1 = titles.some(t => /Q1 2024|2024.*一/.test(t));
    console.log(`After Newsroom click: ${titles.length} cards, has Q1 2024 letter: ${hasQ1}`);
  } else {
    console.log('Newsroom header not found');
  }

  await browser.close();
})().catch(e => { console.error(e.message); process.exit(1); });
