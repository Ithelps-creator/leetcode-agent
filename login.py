from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        "leetcode-profile",
        headless=False,
    )
    page = context.new_page()
    page.goto("https://leetcode.com/accounts/login/")
    input("Log in to LeetCode in the browser window, then come back here and press Enter...")
    context.close()
