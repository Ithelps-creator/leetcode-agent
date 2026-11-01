import os, re, requests
from playwright.sync_api import sync_playwright

def ask_model(problem_text):
    prompt = (
        "Solve this LeetCode problem in C. "
        "Use the exact function signature LeetCode expects for C, including any "
        "returnSize or returnColumnSizes pointer parameters, and allocate returned "
        "arrays with malloc. "
        "Return ONLY the code inside one ```c block, with no explanation.\n\n"
        + problem_text
    )
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json={"model": "openai/gpt-oss-120b",
              "messages": [{"role": "user", "content": prompt}]},
        timeout=90,
    )
    reply = r.json()["choices"][0]["message"]["content"]
    match = re.search(r"```(?:c)?\n(.*?)```", reply, re.S)
    return match.group(1).strip() if match else reply.strip()

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

    code = ask_model(text[:4000])
    print("Got solution, now switching language to C...")

    # Switch the editor language to C
    page.locator('button:has-text("Python3"), button:has-text("C++"), button:has-text("Java")').first.click()
    page.wait_for_timeout(1000)
    page.get_by_text("C", exact=True).first.click()
    page.wait_for_timeout(2000)

    # Clear the editor and paste the code
    page.locator(".monaco-editor").first.click()
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.evaluate("code => navigator.clipboard.writeText(code)", code)
    page.keyboard.press("Meta+V")
    page.wait_for_timeout(1000)

    input("Check the editor looks right, then press Enter here to submit...")

    # Submit
    page.locator('button[data-e2e-locator="console-submit-button"]').click()
    page.wait_for_timeout(10000)

    result = page.locator('[data-e2e-locator="submission-result"]').inner_text(timeout=30000)
    print("RESULT:", result)
