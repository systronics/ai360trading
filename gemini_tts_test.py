"""gemini_tts_test.py (2026-11-01) — CI-only test: can Gemini's FREE TTS speak Hinglish WITH emotion (style prompts)?
Writes a few wav files to output/voice/ for the owner to listen to. Uploads/posts nothing."""
import os, sys, json, base64, wave, time
import requests

KEY = os.environ.get("GEMINI_API_KEY", "")
OUT = "output/voice"
os.makedirs(OUT, exist_ok=True)

LINE1 = "आपका फ़ोन चार्ज करते टाइम इतना हॉट क्यों हो जाता है? चलो, अंदर देखते हैं।"
LINE2 = "फ़ोन की चिप के अंदर करंट बहुत पतले वायर से गुज़रता है, और वायर करंट को थोड़ा रोकते हैं। जैसे भीड़ वाली गली में धक्का-मुक्की होती है ना, वैसे ही करंट में फ़्रिक्शन होता है, और वही फ़्रिक्शन हीट बन जाता है।"
LINE5 = "तो धूप में चार्ज मत करो, मोटा कवर निकाल दो, और चार्जिंग के टाइम हैवी गेम मत खेलो। सीधी बात, हीट मतलब करंट की धक्का-मुक्की।"

TESTS = [
    ("hook_excited_fenrir", "Fenrir", "Say this like an energetic, curious young Indian YouTuber hooking viewers in the first seconds, fast and punchy, with surprise on 'हॉट':", LINE1),
    ("hook_excited_puck", "Puck", "Say this like an energetic, curious young Indian YouTuber hooking viewers in the first seconds, fast and punchy, with surprise on 'हॉट':", LINE1),
    ("explain_friendly_charon", "Charon", "Say this like a friendly teacher explaining to a friend, warm, clear, lively, slight smile, natural Hinglish pacing, stress on 'धक्का-मुक्की' and 'हीट':", LINE2),
    ("explain_friendly_fenrir", "Fenrir", "Say this like a friendly teacher explaining to a friend, warm, clear, lively, slight smile, natural Hinglish pacing, stress on 'धक्का-मुक्की' and 'हीट':", LINE2),
    ("tips_confident_kore", "Kore", "Say this like a confident, reassuring friend giving three quick tips, firm and upbeat:", LINE5),
]


def models():
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models", params={"key": KEY, "pageSize": 200}, timeout=30)
    r.raise_for_status()
    names = [m["name"].split("/")[-1] for m in r.json().get("models", []) if "tts" in m["name"].lower()]
    return names


def synth(model, voice, style, text):
    body = {"contents": [{"parts": [{"text": f"{style} {text}"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", params={"key": KEY}, json=body, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code} {r.text[:200]}")
    part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
    return base64.b64decode(part["data"])


def main():
    if not KEY:
        print("GEMINI_API_KEY missing")
        return 1
    ms = models()
    print("TTS models:", ms)
    if not ms:
        return 1
    # prefer newest flash TTS
    order = sorted(ms, key=lambda n: ("3.1" in n, "flash" in n, "preview" not in n), reverse=True)
    model = order[0]
    print("using", model)
    ok = 0
    for name, voice, style, text in TESTS:
        for attempt in range(3):
            try:
                pcm = synth(model, voice, style, text)
                with wave.open(f"{OUT}/{name}.wav", "wb") as w:
                    w.setnchannels(1)
                    w.setsampwidth(2)
                    w.setframerate(24000)
                    w.writeframes(pcm)
                print("OK", name, round(len(pcm) / 48000, 1), "s")
                ok += 1
                break
            except Exception as e:
                print("ERR", name, str(e)[:160])
                time.sleep(35)
        time.sleep(32)   # free tier is ~2 requests/minute
    print("done", ok, "of", len(TESTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
