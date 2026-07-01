# Palantir Blog Archive — Context Conservation Rules

## Problem
This project involves iterative UI development of a blog archive website. The agent
uses Playwright/browser screenshots to verify visual changes. Each full-page screenshot
is 500-800KB of base64 PNG (~150K-200K tokens). Sessions accumulate 25-45 screenshots,
causing per-request context to reach 700K+ out of the 950K window — triggering context
overflow within a few turns.

## Rules

### 1. Prefer DOM assertions over screenshots
- Use `page.evaluate()` to check text content, CSS properties, class names, computed styles.
- Use `page.locator()` / `element.textContent()` to verify content changes.
- Use `page.title()`, `page.url()`, DOM attribute checks for structural verification.
- Example: instead of screenshotting to check if text is Chinese, run:
  `page.evaluate(() => document.querySelector('.category-name').textContent)`

### 2. When screenshots are unavoidable
- Capture specific elements with `element.screenshot()`, NOT full-page `page.screenshot()`.
- Set a small viewport (e.g. 800x600) to reduce image size.
- Never take more than 1 screenshot per turn.
- Extract the relevant info (text, color, layout) from the screenshot immediately and
  state it in commentary — the goal is to not need the image again in future turns.

### 3. Never screenshot to re-check something already verified
- If you already verified an element's appearance in a previous turn, do not screenshot
  it again unless the user reports a visual regression.

### 4. Context budget awareness
- If per-request token count exceeds 400K, warn the user and suggest starting a new
  conversation before continuing.
- At 600K+, stop taking screenshots entirely for the rest of the session.
- Prefer starting a fresh conversation over fighting context pressure.

### 5. File reading
- This project has large JSON files (classified_articles.json 370KB, page_data.json 310KB,
  index.html 330KB). Do NOT read these files in full — use `jq`, `grep`, or `head`/`tail`
  to extract only the relevant fields.
- `INDEX.md` (48KB) is a summary table; reading it once per session is fine, but avoid
  re-reading it every turn.

### 6. Workflow
- For UI changes: make the edit, run a targeted DOM check (not a screenshot), report
  the result. Only screenshot if the user asks for visual confirmation or if layout
  breakage is suspected.
- For data/JSON changes: use `jq` to verify structure, never read the full file.
