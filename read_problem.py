from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://leetcode.com/problems/two-sum/")
    page.wait_for_timeout(5000)
    try:
        text = page.locator('div[data-track-load="description_content"]').inner_text(timeout=10000)
    except Exception:
        text = page.locator("body").inner_text()
    print(text[:1500])
