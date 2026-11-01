import os, re, sys, requests
from playwright.sync_api import sync_playwright

MAX_TRIES = 3

def ask_model(problem_text, previous_code=None, error=None):
    prompt = (
        "Solve this LeetCode problem in C. "
        "Use the exact function signature LeetCode expects for C, including any "
        "returnSize or returnColumnSizes pointer parameters, and allocate returned "
        "arrays with malloc. "
        "Return ONLY the code inside one ```c block, with no explanation.\n\n"
        + problem_text
    )
    if previous_code:
        prompt += (
            "\n\nYour previous attempt failed.\nPrevious code:\n```c\n"
            + previous_code + "\n```\nLeetCode said:\n" + error[:1500]
            + "\n\nFix the code."
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

def read_problem(page, slug):
    page.goto(f"https://leetcode.com/problems/{slug}/")
    page.wait_for_timeout(5000)
    try:
        return page.locator('div[data-track-load="description_content"]').inner_text(timeout=10000)
    except Exception:
        return page.locator("body").inner_text()

def set_language_c(page):
    try:
        page.locator('button:has-text("Python3"), button:has-text("C++"), button:has-text("Java")').first.click(timeout=3000)
        page.wait_for_timeout(1000)
        page.get_by_text("C", exact=True).first.click()
        page.wait_for_timeout(2000)
    except Exception:
        pass  # probably already set to C

def put_code(page, code):
    page.locator(".monaco-editor").first.click()
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.evaluate("code => navigator.clipboard.writeText(code)", code)
    page.keyboard.press("Meta+V")
    page.wait_for_timeout(1000)

def submit(page):
    page.locator('button[data-e2e-locator="console-submit-button"]').click()
    page.wait_for_timeout(8000)  # let the judge start, so we don't read an old result
    statuses = ["Wrong Answer", "Compile Error", "Runtime Error",
                "Time Limit Exceeded", "Memory Limit Exceeded", "Output Limit Exceeded"]
    for _ in range(30):  # check for up to ~60 seconds
        text = page.locator("body").inner_text()
        lines = [l.strip() for l in text.splitlines()]
        for s in statuses:
            if s in lines:
                return s, text[text.index(s):][:1500]
        if "Accepted" in lines and "Runtime" in text:
            return "Accepted", text[text.index("Runtime"):][:300]
        page.wait_for_timeout(2000)
    page.screenshot(path="submit-debug.png")
    return "Unknown (no result found)", "No result panel found. See submit-debug.png"
slug = sys.argv[1] if len(sys.argv) > 1 else "two-sum"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    text = read_problem(page, slug)
    set_language_c(page)

    code, error = None, None
    for attempt in range(1, MAX_TRIES + 1):
        print(f"Attempt {attempt}: asking the model...")
        code = ask_model(text[:4000], code, error)
        put_code(page, code)
        status, details = submit(page)
        print("RESULT:", status)
        if "Accepted" in status:
            print("Solved!")
            break
        error = details
    else:
        print("Gave up after", MAX_TRIES, "attempts.")
