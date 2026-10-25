"""
model_audit.py v1.0 (2026-10-25) — one-shot health check of every free AI/voice/image dependency.
Prints names and PASS/FAIL only (never keys). Run via the manual 'AI Model Audit' workflow; safe to run any time.
Answers: is any model retired or over quota, and does each fallback layer actually work with the real secrets?
"""
import os
import asyncio
import tempfile
import logging

logging.basicConfig(level=logging.WARNING)
import ai_client as ac

results = []


def rec(name, ok, note=""):
    results.append((name, ok, note))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")


client = ac.AIClient()
PROMPT, SYS = "Reply with exactly the single word: OK", "You are a test."

for prov, key in (("groq", client.groq_key), ("gemini", client.gemini_key), ("cloudflare", client.cf_account and client.cf_token)):
    if not key:
        rec(f"text:{prov}", False, "(secret not set)")
        continue
    try:
        out = client._try_provider(prov, PROMPT, SYS, 20, 0.0, False)
        rec(f"text:{prov}", bool(out), f"-> {str(out)[:30]!r}")
    except Exception as e:
        rec(f"text:{prov}", False, str(e)[:120])

try:
    print("Groq live (ranked):", ac.discover_groq_models(client.groq_key)[:6] if client.groq_key else "n/a")
    print("Gemini live (ranked):", ac.discover_gemini_models(client.gemini_key)[:6] if client.gemini_key else "n/a")
    if client.cf_account and client.cf_token:
        print("Cloudflare text live (ranked):", ac.discover_cf_text_models(client.cf_account, client.cf_token)[:6])
except Exception as e:
    print("discovery print failed:", e)

# images: every Cloudflare image model + Pollinations
try:
    import requests, base64
    acct, tok = os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""), os.environ.get("CLOUDFLARE_API_TOKEN", "")
    for model, body in (("@cf/black-forest-labs/flux-1-schnell", {"prompt": "a red apple, 3D render", "steps": 4}),
                        ("@cf/bytedance/stable-diffusion-xl-lightning", {"prompt": "a red apple, 3D render"}),
                        ("@cf/stabilityai/stable-diffusion-xl-base-1.0", {"prompt": "a red apple, 3D render"})):
        if not (acct and tok):
            rec(f"image:{model.split('/')[-1]}", False, "(secret not set)")
            continue
        try:
            r = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}",
                              headers={"Authorization": f"Bearer {tok}"}, json=body, timeout=120)
            rec(f"image:{model.split('/')[-1]}", r.status_code == 200, f"HTTP {r.status_code}")
        except Exception as e:
            rec(f"image:{model.split('/')[-1]}", False, str(e)[:80])
    try:
        r = requests.get("https://image.pollinations.ai/prompt/red%20apple?width=256&height=256&nologo=true", timeout=60)
        rec("image:pollinations", r.status_code == 200 and r.headers.get("content-type", "").startswith("image"), f"HTTP {r.status_code}")
    except Exception as e:
        rec("image:pollinations", False, str(e)[:80])
except Exception as e:
    print("image audit failed:", e)

# voice
try:
    import edge_tts
    p = os.path.join(tempfile.gettempdir(), "audit.mp3")
    asyncio.run(edge_tts.Communicate("नमस्ते, यह एक टेस्ट है", "hi-IN-MadhurNeural").save(p))
    rec("voice:edge-tts hi-IN-Madhur", os.path.getsize(p) > 1000, f"{os.path.getsize(p)} bytes")
except Exception as e:
    rec("voice:edge-tts hi-IN-Madhur", False, str(e)[:100])

bad = [n for n, ok, _ in results if not ok]
print(f"\nSUMMARY: {len(results) - len(bad)}/{len(results)} pass" + (f" | FAIL: {bad}" if bad else ""))
