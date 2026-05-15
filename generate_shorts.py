"""
generate_shorts.py — AI360Trading v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v3.0 CHANGES:
- AlertLog connected: top stock by Priority Score auto-selected
- Nifty200 weekend mode: Base Prepared / Fundamental stocks
- ZENO emotion auto-selected based on sentiment + stock move
- Dual language: Hindi (Swara) + English (Jenny) from same data
- Video and Short have DIFFERENT scripts (short = hook + signal)
- Market Pulse shorts REMOVED — replaced by stock story format

ZENO EMOTIONS MAP:
  zeno_happy.png   → bullish, target hit, strong buy, +3%+
  zeno_greed.png   → breakout confirmed, momentum, strong move
  zeno_shocked.png → big gap up, surprise move, breakout alert
  zeno_thinking.png→ near breakout, base building, weekend analysis
  zeno_sad.png     → bearish, market down, caution
  zeno_fear.png    → high VIX, market crash, hard stop loss
  zeno_angry.png   → missed trade, FOMO warning, patience lesson

Short format (45-60 sec):
  0-3s  : ZENO emotion + big text hook (stock name + % move)
  4-40s : WHY it moved (FII, breakout, sector)
          Entry/SL/Target for advance subscribers
  41-55s: CTA → Telegram join
"""

import os
import json
import asyncio
import textwrap
from datetime import datetime
from pathlib import Path

import time
import requests
import edge_tts
import gspread
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from google.oauth2.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from human_touch import ht, seo
from ai_client import ai

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CONTENT_MODE = os.environ.get("CONTENT_MODE", "market").lower()
HOLIDAY_NAME = os.environ.get("HOLIDAY_NAME", "Indian Market Holiday")
LANG         = os.environ.get("SHORT_LANG", "hi")   # "hi" or "en"

print(f"[SHORTS v3.0] mode={CONTENT_MODE.upper()} lang={LANG.upper()}")

OUT        = Path("output")
IMAGE_DIR  = Path("public/image")
W, H       = 1080, 1920   # 9:16 vertical
FPS        = 30
VOICE_HI   = "hi-IN-SwaraNeural"
VOICE_EN   = "en-US-JennyNeural"
VOICE      = VOICE_HI if LANG == "hi" else VOICE_EN

SHEET_NAME = "Ai360tradingAlgo"

os.makedirs(OUT, exist_ok=True)

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.LANCZOS

# ─── FONTS ────────────────────────────────────────────────────────────────────
FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
]
FONT_REG_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ─── ZENO EMOTION SELECTOR ────────────────────────────────────────────────────
def get_zeno_emotion(sentiment: str, pct_change: float, stage: str) -> str:
    """
    Auto-select ZENO emotion PNG based on stock data.
    Returns filename (without path).
    """
    stage_upper = stage.upper()

    if sentiment == "bearish" or pct_change < -3:
        return "zeno_sad.png"
    if pct_change < -5 or "CRASH" in stage_upper:
        return "zeno_fear.png"
    if "BREAKOUT CONFIRMED" in stage_upper and pct_change > 3:
        return "zeno_greed.png"
    if "BREAKOUT ALERT" in stage_upper and pct_change > 2:
        return "zeno_happy.png"
    if pct_change > 5:
        return "zeno_greed.png"
    if pct_change > 2:
        return "zeno_happy.png"
    if "NEAR BREAKOUT" in stage_upper or "BUILDING MOMENTUM" in stage_upper:
        return "zeno_thinking.png"
    if "BASE" in stage_upper or "CORRECTION" in stage_upper:
        return "zeno_thinking.png"
    if sentiment == "bullish":
        return "zeno_happy.png"

    return "zeno_thinking.png"


# ─── FETCH TOP STOCK FROM ALERTLOG / NIFTY200 ────────────────────────────────
def fetch_top_stock() -> dict:
    """
    Weekday: Get top WAITING/TRADED stock from AlertLog by Priority Score.
    Weekend: Get best Base Prepared / Near Breakout from Nifty200.
    Returns stock dict with symbol, cmp, sl, target, stage, sentiment, pct_change.
    """
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(os.environ.get("GCP_SERVICE_ACCOUNT_JSON")), scope
        )
        ss        = gspread.authorize(creds).open(SHEET_NAME)
        log_sheet = ss.worksheet("AlertLog")

        if CONTENT_MODE in ("weekend", "holiday"):
            # Weekend: scan Nifty200 for base-prepared stocks
            n200 = ss.worksheet("Nifty200")
            rows = n200.get_all_values()
            candidates = []
            for row in rows[2:]:   # skip header + Nifty row
                if len(row) < 35: continue
                sym   = str(row[0]).strip()
                cmp   = _to_f(row[2])
                pct   = _to_f(row[3])
                stage = str(row[22]).strip()
                score = _to_f(row[33])   # Master Score
                fii   = str(row[15]).strip()
                action= str(row[19]).strip()
                if not sym or cmp <= 0: continue
                if "AVOID" in action.upper(): continue
                if fii == "FII SELLING": continue
                if any(s in stage for s in ["Near Breakout", "Building Momentum", "Correction Base"]):
                    candidates.append({
                        "symbol":     sym,
                        "cmp":        cmp,
                        "pct_change": pct,
                        "stage":      stage,
                        "sl":         _to_f(row[7]) if len(row) > 7 else 0,
                        "target":     _to_f(row[8]) if len(row) > 8 else 0,
                        "sentiment":  "bullish",
                        "priority":   score,
                        "fii":        fii,
                        "sector":     str(row[1]).strip(),
                        "source":     "nifty200_weekend",
                    })
            if candidates:
                candidates.sort(key=lambda x: x["priority"], reverse=True)
                top = candidates[0]
                print(f"[STOCK] Weekend pick: {top['symbol']} | Stage: {top['stage']} | Score: {top['priority']}")
                return top

        else:
            # Weekday: get top from AlertLog
            all_data = log_sheet.get_all_values()
            candidates = []
            for row in all_data[1:22]:
                if len(row) < 20: continue
                status = str(row[10]).upper()
                sym    = str(row[1]).strip()
                if not sym: continue
                if "WAITING" not in status and "TRADED" not in status: continue
                if "EXITED" in status: continue
                cmp      = _to_f(row[2])
                priority = _to_f(row[3])
                sl       = _to_f(row[7])
                target   = _to_f(row[8])
                stage    = str(row[6]).strip()
                strat    = str(row[5]).strip()
                entry    = _to_f(row[11]) if _to_f(row[11]) > 0 else cmp
                pct      = ((cmp - entry) / entry * 100) if entry > 0 else 0
                sentiment= "bullish" if pct >= 0 else "bearish"
                if cmp <= 0 or priority <= 0: continue
                candidates.append({
                    "symbol":     sym,
                    "cmp":        cmp,
                    "pct_change": pct,
                    "stage":      stage,
                    "strategy":   strat,
                    "sl":         sl,
                    "target":     target,
                    "sentiment":  sentiment,
                    "priority":   priority,
                    "status":     status,
                    "source":     "alertlog",
                })
            if candidates:
                candidates.sort(key=lambda x: x["priority"], reverse=True)
                top = candidates[0]
                print(f"[STOCK] Weekday pick: {top['symbol']} | Priority: {top['priority']} | Stage: {top['stage']}")
                return top

    except Exception as e:
        print(f"⚠️ Sheet fetch error: {e}")

    # Fallback
    print("[STOCK] Using fallback stock data")
    return {
        "symbol":     "NSE:NIFTY50",
        "cmp":        0,
        "pct_change": 0,
        "stage":      "Market Analysis",
        "strategy":   "Education",
        "sl":         0,
        "target":     0,
        "sentiment":  "neutral",
        "priority":   0,
        "source":     "fallback",
    }

def _to_f(val) -> float:
    try: return float(str(val).replace(",","").replace("₹","").replace("%","").strip())
    except: return 0.0


# ─── SCRIPT GENERATION ────────────────────────────────────────────────────────
def generate_short_script(stock: dict) -> dict:
    sym        = stock["symbol"].replace("NSE:", "")
    cmp        = stock["cmp"]
    pct        = stock["pct_change"]
    stage      = stock["stage"]
    sl         = stock["sl"]
    target     = stock["target"]
    sentiment  = stock["sentiment"]
    source     = stock["source"]
    today      = datetime.now().strftime("%d %b %Y")
    hook       = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
    cta        = ht.get_cta(lang=LANG)

    pct_str    = f"{pct:+.1f}%" if pct != 0 else ""
    sl_str     = f"₹{sl:.1f}" if sl > 0 else "as per chart"
    tgt_str    = f"₹{target:.1f}" if target > 0 else "next resistance"
    cmp_str    = f"₹{cmp:.1f}" if cmp > 0 else "live price"

    if LANG == "hi":
        lang_instruction = (
            "Write in Hinglish. Short, punchy sentences. Like a WhatsApp voice note to a friend. "
            "Maximum energy. Simple words. Technical terms in English."
        )
        tg_cta = "Telegram join karo — link bio mein hai! Free signals daily."
    else:
        lang_instruction = (
            "Write in simple energetic English. Like explaining to a friend over a call. "
            "Short punchy sentences. Global audience — explain Indian market context briefly."
        )
        tg_cta = "Join our Telegram for free daily signals — link in bio!"

    if source == "nifty200_weekend":
        context = (
            f"This is a WEEKEND fundamental analysis short about {sym}. "
            f"The stock is in '{stage}' stage — it's building a base before potential breakout. "
            f"FII is accumulating. Explain why this is a patient opportunity."
        )
    elif pct > 3:
        context = f"{sym} is up {pct_str} today — BREAKOUT in progress. Explain the setup with excitement."
    elif pct < -2:
        context = f"{sym} is down {pct_str} today. Explain whether this is a buying dip or a warning sign."
    else:
        context = f"{sym} is showing a {stage} setup. Explain why this stock is on the watchlist."

    prompt = f"""You are creating a 45-60 second YouTube Short script for AI360 Trading.

Today: {today}
Stock: {sym} | CMP: {cmp_str} | Move: {pct_str}
Stage: {stage} | Sentiment: {sentiment}
SL: {sl_str} | Target: {tgt_str}
Context: {context}
Language: {lang_instruction}

STRUCTURE (strict — this is a Short, not a long video):
- Hook (0-3 sec): Most shocking/exciting thing about this stock RIGHT NOW
- Body (4-40 sec): WHY — explain the setup, what FII/volume is doing, 1 key level
- Signal (41-50 sec): Entry near {cmp_str}, SL {sl_str}, Target {tgt_str}
- CTA (51-55 sec): "{tg_cta}"

Start with: "{hook}"
End with: "{cta}"

Generate as JSON:
{{
  "thumbnail_text_line1": "STOCK NAME or % move — max 8 chars, ALL CAPS",
  "thumbnail_text_line2": "Hook phrase — max 20 chars",
  "thumbnail_text_line3": "ai360trading | {today}",
  "zeno_emotion": "happy or greed or shocked or thinking or sad or fear or angry",
  "full_script": "Complete 45-60 second spoken script. Single paragraph. Natural speech.",
  "hook_line": "First 1 sentence only — the opening hook",
  "sentiment": "bullish or bearish or neutral"
}}"""

    print(f"🤖 Generating {LANG.upper()} short script for {sym}...")
    try:
        data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
        if data.get("full_script"):
            data["full_script"] = ht.humanize(data["full_script"], lang=LANG)
        print(f"✅ Short script ready: {data.get('thumbnail_text_line1','')} {data.get('thumbnail_text_line2','')}")
        return data
    except Exception as e:
        print(f"⚠️ Script error: {e}")
        return {
            "thumbnail_text_line1": sym[:8].upper(),
            "thumbnail_text_line2": "BREAKOUT TODAY!",
            "thumbnail_text_line3": f"ai360trading | {today}",
            "zeno_emotion": "happy",
            "full_script": f"Namaskar! Aaj {sym} ek important level pe hai. Subscribe karo aur Telegram join karo daily signals ke liye! ai360trading.in",
            "hook_line": f"{sym} aaj bahut important level pe hai!",
            "sentiment": sentiment,
        }


# ─── THUMBNAIL RENDERER ───────────────────────────────────────────────────────
def make_short_frame(script: dict, stock: dict, path: Path):
    """
    Single-frame thumbnail/video frame for the short.
    ZENO takes 60% of frame height — big, emotional, visible.
    Bold text takes remaining space.
    """
    sentiment = script.get("sentiment", stock.get("sentiment", "neutral"))
    pct       = stock.get("pct_change", 0)
    stage     = stock.get("stage", "")

    # Background theme based on sentiment
    if sentiment == "bullish":
        bg_top, bg_bot, accent = (5, 25, 15), (10, 55, 28), (0, 220, 110)
    elif sentiment == "bearish":
        bg_top, bg_bot, accent = (35, 8, 8), (70, 18, 18), (255, 60, 60)
    else:
        bg_top, bg_bot, accent = (10, 18, 45), (18, 40, 90), (0, 180, 255)

    img = Image.new("RGB", (W, H))
    px  = img.load()
    for y in range(H):
        c = lerp(bg_top, bg_bot, y / H)
        for x in range(W): px[x, y] = c

    draw = ImageDraw.Draw(img, "RGBA")

    # ── Load ZENO image ───────────────────────────────────────────────────────
    zeno_file = script.get("zeno_emotion", "thinking")
    # Map emotion name to filename
    emotion_map = {
        "happy":   "zeno_happy.png",
        "greed":   "zeno_greed.png",
        "shocked": "zeno_happy.png",   # fallback to happy if shocked missing
        "thinking":"zeno_thinking.png",
        "sad":     "zeno_sad.png",
        "fear":    "zeno_fear.png",
        "angry":   "zeno_angry.png",
    }
    zeno_filename = emotion_map.get(zeno_file, "zeno_thinking.png")
    zeno_path     = IMAGE_DIR / zeno_filename

    # Also try get_zeno_emotion as override
    auto_emotion  = get_zeno_emotion(sentiment, pct, stage)
    if not zeno_path.exists():
        zeno_path = IMAGE_DIR / auto_emotion

    zeno_loaded = False
    if zeno_path.exists():
        try:
            zeno_img = Image.open(str(zeno_path)).convert("RGBA")
            # ZENO takes full width, bottom 65% of frame
            zeno_h   = int(H * 0.65)
            zeno_w   = int(zeno_img.width * (zeno_h / zeno_img.height))
            zeno_img = zeno_img.resize((zeno_w, zeno_h), Image.LANCZOS)
            # Center horizontally, bottom-align
            zx = (W - zeno_w) // 2
            zy = H - zeno_h
            img.paste(zeno_img, (zx, zy), zeno_img)
            zeno_loaded = True
            print(f"[ZENO] Loaded: {zeno_filename}")
        except Exception as e:
            print(f"[ZENO] Load error: {e}")

    # ── Text overlay — top 35% of frame ──────────────────────────────────────
    line1 = script.get("thumbnail_text_line1", stock["symbol"].replace("NSE:",""))
    line2 = script.get("thumbnail_text_line2", "BREAKOUT!")
    line3 = script.get("thumbnail_text_line3", "ai360trading.in")

    # Top bar
    draw.rectangle([(0, 0), (W, 10)], fill=accent)

    # Line 1 — HUGE stock name / % move
    f1 = get_font(FONT_BOLD_PATHS, 160)
    # Shadow
    for dx, dy in [(-4, 0), (4, 0), (0, -4), (0, 4)]:
        draw.text((W//2 + dx, 120 + dy), line1, font=f1, fill=(0, 0, 0), anchor="mm")
    draw.text((W//2, 120), line1, font=f1, fill=(255, 220, 0), anchor="mm")

    # Line 2 — hook phrase
    f2 = get_font(FONT_BOLD_PATHS, 72)
    draw.text((W//2, 240), line2, font=f2, fill=(255, 255, 255), anchor="mm")

    # Accent divider
    draw.rectangle([(80, 290), (W - 80, 296)], fill=accent)

    # Line 3 — channel/date — small
    f3 = get_font(FONT_REG_PATHS, 36)
    draw.text((W//2, 335), line3, font=f3, fill=(*[180, 210, 230], 200), anchor="mm")

    # % badge if significant move
    if abs(pct) >= 1.5:
        pct_color = (0, 220, 110) if pct > 0 else (255, 60, 60)
        pct_str   = f"{pct:+.1f}%"
        fbadge    = get_font(FONT_BOLD_PATHS, 56)
        # Badge background
        draw.rounded_rectangle([(W//2 - 120, 360), (W//2 + 120, 420)],
                                radius=20, fill=(*pct_color, 200))
        draw.text((W//2, 390), pct_str, font=fbadge, fill=(255,255,255), anchor="mm")

    # Bottom bar
    draw.rectangle([(0, H - 10), (W, H)], fill=accent)

    img.save(str(path), quality=95)
    return img


# ─── VOICE ────────────────────────────────────────────────────────────────────
async def gen_voice(text: str, path: Path):
    # Shorts use slightly faster speed — feels more energetic
    rate_str = "+5%"
    await edge_tts.Communicate(text, VOICE, rate=rate_str).save(str(path))


# ─── YOUTUBE SHORTS UPLOAD ────────────────────────────────────────────────────
def get_youtube_service():
    try:
        creds_key  = "YOUTUBE_CREDENTIALS_EN" if LANG == "en" else "YOUTUBE_CREDENTIALS"
        creds_json = os.environ.get(creds_key)
        if not creds_json and os.path.exists("token.json"):
            with open("token.json") as f: creds_json = f.read()
        if not creds_json: return None
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        return build("youtube", "v3", credentials=creds)
    except Exception:
        return None


def upload_short(video_path: Path, title: str, description: str, tags: list):
    youtube = get_youtube_service()
    if not youtube:
        print(f"❌ YouTube unavailable [{LANG}] — skipping short upload")
        return None
    body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        tags[:30],
            "categoryId":  "27"
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    print(f"🚀 Uploading Short [{LANG.upper()}]: {title[:60]}...")
    try:
        request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"  {int(status.progress() * 100)}%")
        vid_id = response["id"]
        print(f"✅ Short uploaded [{LANG.upper()}]: https://youtube.com/shorts/{vid_id}")
        return vid_id
    except Exception as e:
        print(f"❌ Short upload failed: {e}")
        return None


# ─── FACEBOOK SHARE (Hindi only — page token fix) ────────────────────────────
FB_RETRY      = 2
FB_RETRY_WAIT = 5


def get_fb_page_token(user_token: str, page_id: str) -> str:
    """Exchange user token for page token — required for page posts. Fixes #200 error."""
    try:
        resp = requests.get(
            "https://graph.facebook.com/v21.0/me/accounts",
            params={"access_token": user_token, "limit": 20},
            timeout=15
        )
        if resp.ok:
            for page in resp.json().get("data", []):
                if str(page.get("id")) == str(page_id):
                    return page.get("access_token", user_token)
    except Exception:
        pass
    return user_token


def share_to_facebook(short_url: str, stock: dict, script: dict):
    """
    Share YouTube Short link to Facebook Page.
    Hindi only — English has no FB page yet.
    Only runs when META_ACCESS_TOKEN + FACEBOOK_PAGE_ID are set.
    """
    user_token = os.environ.get("META_ACCESS_TOKEN", "")
    page_id    = os.environ.get("FACEBOOK_PAGE_ID", "")
    if not user_token or not page_id or not short_url:
        print("⚠️ Facebook credentials missing or no short URL — skipping")
        return

    token  = get_fb_page_token(user_token, page_id)
    sym    = stock.get("symbol", "").replace("NSE:", "")
    pct    = stock.get("pct_change", 0)
    stage  = stock.get("stage", "")
    sl     = stock.get("sl", 0)
    target = stock.get("target", 0)
    tags   = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    htags  = " ".join([f"#{t}" for t in tags[:8]])

    pct_str = f"{pct:+.1f}%" if pct != 0 else ""
    msg = (
        f"📊 {sym} {pct_str} — {stage} 🔥\n\n"
        f"🎯 Entry: ₹{stock.get('cmp',0):.1f}\n"
        f"🛑 SL: ₹{sl:.1f}\n" if sl > 0 else ""
        f"🎯 Target: ₹{target:.1f}\n\n" if target > 0 else "\n"
        f"📱 Daily signals: https://t.me/ai360trading\n"
        f"🌐 https://ai360trading.in\n\n"
        f"⚠️ Educational only. Not SEBI advice.\n\n"
        f"{htags} #ai360trading #{sym.replace('-','')}\n\n"
        f"▶️ Watch: {short_url}"
    )

    for attempt in range(1, FB_RETRY + 1):
        try:
            resp   = requests.post(
                f"https://graph.facebook.com/v21.0/{page_id}/feed",
                data={"message": msg, "access_token": token},
                timeout=30
            )
            result = resp.json()
            if "id" in result:
                print(f"  ✅ Facebook Page shared — Post ID: {result['id']}")
                return
            else:
                error = result.get("error", {})
                print(f"  ❌ Facebook failed (attempt {attempt}): {error.get('message','unknown')}")
                if error.get("code") in [200, 190]:
                    break  # Auth error — no point retrying
        except Exception as e:
            print(f"  ⚠️ Facebook error (attempt {attempt}): {e}")
        if attempt < FB_RETRY:
            time.sleep(FB_RETRY_WAIT)
    print("  ✗ Facebook share failed — all attempts done.")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
async def run():
    today_str = datetime.now().strftime("%d %b %Y")
    today_fn  = datetime.now().strftime("%Y%m%d")

    # Fetch top stock
    stock  = fetch_top_stock()
    sym    = stock["symbol"].replace("NSE:", "")
    pct    = stock["pct_change"]
    stage  = stock["stage"]
    source = stock["source"]

    print(f"📊 Stock: {sym} | {pct:+.1f}% | {stage} | Source: {source}")

    # Generate script
    script = generate_short_script(stock)

    # Build title + description
    tags        = seo.get_video_tags(mode=CONTENT_MODE, is_short=True)
    hashtag_str = " ".join([f"#{t}" for t in tags[:12]])
    pct_str     = f"{pct:+.1f}%" if pct != 0 else ""

    if LANG == "hi":
        title = f"{sym} {pct_str} — {script.get('thumbnail_text_line2','')} | AI360 Trading #Shorts"[:100]
        desc  = (
            f"📊 {sym} aaj {stage} stage mein hai.\n"
            f"🎯 Full analysis aur signals ke liye Telegram join karo!\n"
            f"📱 https://t.me/ai360trading\n"
            f"🌐 https://ai360trading.in\n"
            f"⚠️ Educational only. Not SEBI advice.\n\n"
            f"#ai360trading #{sym.replace('-','')} {hashtag_str}"
        )
    else:
        title = f"{sym} {pct_str} — {script.get('thumbnail_text_line2','')} | AI360 Trading #Shorts"[:100]
        desc  = (
            f"📊 {sym} is showing a {stage} setup today.\n"
            f"🎯 Join our free Telegram for daily signals!\n"
            f"📱 https://t.me/ai360trading\n"
            f"🌐 https://ai360trading.in\n"
            f"⚠️ Educational content only. Not financial advice.\n\n"
            f"#ai360trading #{sym.replace('-','')} {hashtag_str}"
        )

    # ── Render frame + voice ──────────────────────────────────────────────────
    img_path   = OUT / f"short_{LANG}_{today_fn}.png"
    audio_path = OUT / f"short_{LANG}_{today_fn}.mp3"

    make_short_frame(script, stock, img_path)
    await gen_voice(script.get("full_script", ""), audio_path)

    voice_clip = AudioFileClip(str(audio_path))
    duration   = min(voice_clip.duration + 0.5, 59.0)   # YouTube Shorts max 60 sec
    clip       = ImageClip(str(img_path)).set_duration(duration).set_audio(voice_clip)

    # ── Render video ──────────────────────────────────────────────────────────
    video_path = OUT / f"short_{LANG}_{today_fn}.mp4"
    clip.write_videofile(
        str(video_path), fps=FPS, codec="libx264", audio_codec="aac",
        remove_temp=True, logger=None
    )
    print(f"✅ Short rendered [{LANG.upper()}]: {video_path.name} | {duration:.1f}s")

    # ── Upload ────────────────────────────────────────────────────────────────
    youtube_tags = [t for t in tags if t.isascii()]
    video_id     = upload_short(video_path, title, desc, youtube_tags)

    # ── Save meta ─────────────────────────────────────────────────────────────
    meta = {
        "title":       title,
        "description": desc,
        "tags":        tags,
        "stock":       sym,
        "pct_change":  pct,
        "stage":       stage,
        "lang":        LANG,
        "zeno_emotion":script.get("zeno_emotion", "thinking"),
        "source":      source,
        "duration_sec":round(duration, 1),
        "youtube_video_id": video_id or "",
        "youtube_short_url": f"https://youtube.com/shorts/{video_id}" if video_id else "",
    }
    meta_path = OUT / f"short_meta_{today_fn}_{LANG}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved: {meta_path.name}")

    # ── Facebook share (Hindi only) ───────────────────────────────────────────
    if LANG == "hi" and video_id:
        short_url = f"https://youtube.com/shorts/{video_id}"
        share_to_facebook(short_url, stock, script)

    print(f"\n{'='*55}")
    print(f"✅ SHORT DONE — {sym} | {LANG.upper()} | {today_str}")
    print(f"   ZENO    : {script.get('zeno_emotion','thinking')}")
    print(f"   Duration: {duration:.1f}s")
    print(f"   Video ID: {video_id or 'FAILED'}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    asyncio.run(run())
