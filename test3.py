import os, requests

key = os.environ["GROQ_API_KEY"]
r = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": "Say hello"}]},
    timeout=30,
)
print(r.json()["choices"][0]["message"]["content"])
