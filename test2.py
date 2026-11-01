import os, requests

key = os.environ["GEMINI_API_KEY"]
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={key}"
body = {"contents": [{"parts": [{"text": "Say hello"}]}]}

r = requests.post(url, json=body, timeout=30)
print(r.json()["candidates"][0]["content"]["parts"][0]["text"])
