const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-blink-features=AutomationControlled', '--no-sandbox']
  });
  const page = await browser.newPage();
  await page.route('**/cookielaw.org/**', r => r.abort());
  await page.route('**/onetrust.com/**', r => r.abort());
  page.on('response', resp => {
    const u = resp.url();
    const ct = resp.headers()['content-type'] || '';
    if (ct.includes('pdf') || u.endsWith('.pdf')) console.log('PDF: ' + u.substring(0, 200));
  });
  console.log('Loading page...');
  await page.goto('https://www.palantir.com/2025-ai-ds-ml-market-study/', { waitUntil: 'domcontentloaded', timeout: 20000 });
  console.log('Waiting for Marketo form...');
  for (let i = 0; i < 30; i++) {
    await page.waitForTimeout(1000);
    const ready = await page.evaluate(() => {
      return {
        form: !!document.querySelector('form.mktoForm, .mktoForm'),
        firstName: !!document.querySelector('#FirstName'),
        recaptcha: !!document.querySelector('iframe[src*="recaptcha"], .g-recaptcha, [data-sitekey]'),
        mktoScript: !!document.querySelector('script[src*="mktoweb"]'),
      };
    });
    if (i % 5 === 0) console.log('  ' + i + 's: ' + JSON.stringify(ready));
    if (ready.firstName || ready.recaptcha || ready.mktoScript) {
      console.log('  Form detected at ' + i + 's!');
      break;
    }
  }
  const info = await page.evaluate(() => {
    const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
    return {
      scriptCount: scripts.length,
      mktoScripts: scripts.filter(s => s.includes('mkto') || s.includes('market')),
      recaptchaIframes: Array.from(document.querySelectorAll('iframe')).map(f => f.src).filter(f => f.includes('recaptcha')),
      forms: Array.from(document.querySelectorAll('form')).map(f => f.className),
      bodyLen: document.body.innerHTML.length,
    };
  });
  console.log('Page info: ' + JSON.stringify(info, null, 2));
  await browser.close();
})();
