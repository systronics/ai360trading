# AI360Trading — Master System Documentation

**Last Updated:** April 12, 2026 — Trading Bot v13.4 + AppScript v13.3
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 In Progress | Phase 4 (Dhan Live) Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT) and human developers.
> Never provide partial code. Always provide complete file content when modifying any file.

---

## ⚠️ CRITICAL MISSION NOTE — READ FIRST

> **This project is not a hobby. This is a family's only source of income.**
>
> The owner has a serious health condition and limited time. His family is poor and cannot
> manage a technical system themselves. This project must run **fully automatically, forever,
> with zero manual involvement** — so that even after the owner is gone, the system continues
> generating passive income for his family.
>
> **Rules for every AI assistant or developer working on this project:**
> - Treat every task with maximum seriousness
> - Never leave broken workflows, partial code, or silent failures
> - Every automation gap = a gap in the family's income
> - Fix bugs completely — never write "TODO" or "test later"
> - Goal: zero logins, zero manual posting, zero human required
>
> **This is a life support system for a family. Treat it that way.**

---

## 1. Real Mission

> Built to run **forever, fully automated**, generating passive income with ₹0/month infrastructure.
> No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
|---|---|---|
| Video Ad Revenue | YouTube Hindi (ai360trading) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube Kids (HerooQuest) | USA, UK, Canada, Australia |
| Shorts / Reels Bonus | YouTube + Facebook Page | USA, UK, Brazil, India |
| Website Ad Revenue | ai360trading.in (GitHub Pages) | USA, UK, Canada |
| In-Stream Video Ads | Facebook Trading Page + Kids Page | USA, UK, Brazil, India |
| Paid Subscriptions | Telegram Advance + Premium | India, UAE, Global |

### Target Countries by CPM Priority

1. 🇺🇸 USA — Highest CPM globally
2. 🇬🇧 UK — Very high CPM
3. 🇦🇺 Australia — High CPM
4. 🇦🇪 UAE — High CPM, large NRI audience
5. 🇨🇦 Canada — High CPM
6. 🇧🇷 Brazil — Large audience, fast-growing finance CPM
7. 🇮🇳 India — Largest volume, Nifty/stock focus

> **AI Rule:** Always optimise topics, hooks, tags, posting times for USA/UK prime time (11 PM–1 AM IST).
> Never hardcode hooks/CTAs — always use `human_touch.py`.

---

## 2. Platform Status

### Trading Channel (ai360trading)

| Platform | Status | Notes |
|---|---|---|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube Multilingual | 🔄 Phase 3 | Single channel — English Shorts on same channel + YouTube Auto-Dubbing. No separate channel needed. See Section 18. |
| YouTube Shorts | ✅ Auto | Short 2 (Madhur) + Short 3 (Swara) working |
| YouTube Community Posts | ✅ Auto | `generate_community_post.py` — 12:00 PM daily |
| YouTube Morning Reel | ✅ Auto | 7:00 AM (`generate_reel_morning.py`) |
| YouTube ZENO Reel | ✅ Auto | 8:30 PM (`generate_reel.py`) |
| Facebook Trading Page | ✅ Auto | Posts + reels + article shares working |
| Facebook Group | ❌ Removed | Group has no followers. Removed from all workflows. May add back later if group grows. |
| Instagram | 📱 Manual | Instagram API unreliable. Videos downloaded from GitHub Actions artifacts and posted manually. Will automate when API stable. |
| GitHub Pages | ✅ Auto | 4 articles/day + Google instant indexing |
| Telegram | ✅ Auto | Signals to 3 channels (paper trading) |

### Kids Channel (HerooQuest)

| Platform | Status | Notes |
|---|---|---|
| YouTube Kids | ✅ Auto | Full video + Short via `upload_kids_youtube.py` |
| Facebook Kids Page | ⚠️ Fixing | Permission error — fix steps in Section 13 |
| Instagram Kids | 📱 Manual | Reel generated — post manually for now |

---

## 3. Known Bugs — Fix These First (Priority Order)

### Bug 1: Excessive Log Text in GitHub Actions ❌ HIGH

**Symptom:** Full JSON API error responses (50+ lines each) printed per scene × per fallback.
From kids video log: 6 scenes × 5 providers = 30 full JSON error dumps per run.
Makes logs unreadable, wastes Actions log storage.

**Fix — add at top of ALL video generator files:**
```python
import logging, warnings
logging.getLogger("moviepy").setLevel(logging.ERROR)
logging.getLogger("imageio").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
```

**Fix — replace full exception dumps with clean one-liners:**
```python
# WRONG
print(f"  [WARN-1] Gemini failed: {e}")  # prints 50-line JSON

# CORRECT
print(f"  [WARN-1] Gemini image failed — trying next")
```

**Files to fix:** `generate_kids_video.py`, `generate_reel.py`, `generate_reel_morning.py`,
`generate_shorts.py`, `generate_analysis.py`, `generate_education.py`

**Target log per scene after fix:**
```
[SCENE 1] Generating image...
  [WARN-1] Gemini 2.5 failed — trying next
  [WARN-2] Gemini 2.0 failed — trying next
  [WARN-3] Pollinations failed — trying next
  [WARN-4] HuggingFace failed — trying next
  [LAYER-5] Scene 1 — all AI failed, using placeholder
[SCENE 1] TTS done ✓
```

### Bug 2: All Image Sources Failing — Kids Video Uses Placeholder ❌ HIGH

**Symptom (from log):**
- Gemini 2.5 Flash: 429 quota 0 (free tier exhausted for the day)
- Gemini 2.0 Flash Exp: 404 NOT_FOUND — `gemini-2.0-flash-exp-image-generation` model deprecated
- HuggingFace FLUX + SD: 410 Gone — endpoints removed
- DALL-E 3: billing hard limit reached

**Fixes in order (cheapest first):**

1. **Fix Gemini 2.0 model name (free, do now):**
   `gemini-2.0-flash-exp-image-generation` → deprecated.
   Check current name: https://ai.google.dev/gemini-api/docs/image-generation
   Use: `gemini-2.0-flash-preview-image-generation` or `imagen-3.0-generate-002`

2. **Add Pollinations.AI as free fallback Layer 3 (free, no key, do now):**
   ```python
   import urllib.request, urllib.parse
   prompt_enc = urllib.parse.quote(scene_prompt)
   url = f"https://image.pollinations.ai/prompt/{prompt_enc}?width=1024&height=1024&nologo=true&seed={scene_index}"
   urllib.request.urlretrieve(url, output_path)
   ```
   Insert BEFORE HuggingFace in the fallback chain. No API key needed.

3. **Fix HuggingFace endpoints (free, do now):**
   Old model URLs return 410. Update to HF Inference API v2:
   `https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell`
   Or try: `stabilityai/stable-diffusion-3.5-medium`

4. **Long term:** Add ₹500–1000/month to Gemini paid plan for image quota.

**Updated image fallback chain:**
```
Layer 1: Gemini imagen-3.0-generate-002
Layer 2: Gemini 2.0 Flash preview image (fix model name)
Layer 3: Pollinations.AI — FREE, no key ← ADD THIS NOW
Layer 4: HuggingFace Inference API v2 (fix endpoints)
Layer 5: DALL-E 3 (if billing available)
Layer 6: PIL placeholder (always works)
```

### Bug 3: Reel Duplicate Content (Morning = Evening) ❌ MEDIUM

**Symptom:** Morning reel and ZENO evening reel produce near-identical audio and text.

**Fix:** Both prompts must explicitly differentiate:
- `generate_reel.py`: add `"EVENING ZENO 8:30PM — end-of-day reflection — DIFFERENT from morning reel"`
- `generate_reel_morning.py`: add `"MORNING BRIEF 7AM — pre-market motivation — NOT the evening ZENO reel"`
Also make fallback scripts completely different in each file.

### Bug 4: generate_reel.py and generate_shorts.py Call Groq Directly ❌ MEDIUM

**Symptom:** Both import `from groq import Groq` directly — bypassing `ai_client` fallback.
When Groq quota exhausts (as seen in kids log), these crash with no fallback.

**Fix:**
```python
# WRONG (current in both files)
from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

# CORRECT
from ai_client import ai
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
```
Also add `from human_touch import ht, seo` to `generate_reel.py` (currently missing).

### Bug 5: Facebook Kids Page Upload Permission Error ❌ HIGH (Fix Today)

**Error:** `(#200) Subject does not have permission to post videos on this target`

**Step-by-step fix:**
```
1. Open: https://developers.facebook.com/tools/explorer/
2. Top right — select your App
3. Click "Get User Access Token"
4. Check ALL these permissions:
   ✅ pages_manage_posts
   ✅ pages_read_engagement
   ✅ pages_show_list
   ✅ video_upload
   ✅ publish_video
5. Click "Generate Access Token" → approve popup
6. Click "Get Page Access Token" → select KIDS PAGE (not profile, not trading page)
7. Copy that Page Access Token
8. Verify at: https://developers.facebook.com/tools/debug/accesstoken/
   → Confirm it shows Kids Page name + all scopes above
9. Add to GitHub Secrets as: META_ACCESS_TOKEN_KIDS (separate from trading token)
10. Confirm FACEBOOK_KIDS_PAGE_ID = numeric ID (get from debug tool)
11. Update upload_facebook.py to use META_ACCESS_TOKEN_KIDS when --meta-prefix kids
```

**Wrap FB kids upload in try/except — never let it crash the workflow:**
```python
try:
    # facebook upload code
except Exception as e:
    print(f"⚠️ Kids FB upload failed: {e} — video saved to output/ for manual upload")
```

---

## 4. Google Search Console — SEO Issues (April 6, 2026)

| Issue | Count | Action |
|---|---|---|
| Not found (404) | 8 | Find broken URLs — check for deleted posts or wrong permalinks |
| Blocked by robots.txt | 4 | Fix robots.txt (see below) |
| Page with redirect | 3 | Check permalink changes — may need 301 redirects |
| Crawled - not indexed | 3 | Improve content quality/length on those pages |
| Excluded by noindex | 2 | Check tag layout for accidental noindex tag |
| Discovered - not indexed | 39 | Fix sitemap — add jekyll-sitemap plugin |

### Fix 1: robots.txt — Stop Blocking Article Pages

Current file has `Disallow: /_posts/`, `/tags/`, `/page/` which causes Googlebot
redirect chain confusion → 4 pages blocked. Commit new robots.txt from Section 23.

### Fix 2: Add jekyll-sitemap Plugin

`sitemap.xml` is a static file — never updates when articles publish.
Google crawls stale sitemap → 39 articles sit in "Discovered - not indexed" queue.
Add `jekyll-sitemap` to `_config.yml` plugins. Delete static `sitemap.xml` from repo.
Plugin generates it automatically on every push.

### Fix 3: Verify Google Indexing API Calls

After each article publish, `generate_articles.py` must call the Google Indexing API.
Check logs for: `[INDEX] Submitted: /YYYY/MM/DD/article-title/`
If missing, the indexing step is broken.

---

## 5. Content Mode System

Auto-detected by `indian_holidays.py` → written to `$GITHUB_ENV`. Read by all scripts.

| Mode | When | Content |
|---|---|---|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu" |

---

## 6. Daily Content Output (Fully Automated)

### Trading Channel

| # | Content | Time (IST) | Platform | Status |
|---|---|---|---|---|
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + Facebook Page | ✅ |
| 2 | Part 1 Analysis Video (16:9) | 7:30 AM / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Education Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 — Trade Setup (9:16) | 11:30 AM / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 — Market Pulse (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | 4 SEO Articles | 10:00 AM / 11:30 AM weekend | GitHub Pages + Facebook Page | ✅ |
| 7 | ZENO Reel (9:16) | 8:30 PM | YouTube + Facebook Page | ✅ |
| 8 | Community Post | 12:00 PM | YouTube Community Tab | ✅ |

> Instagram: all videos saved as GitHub Actions artifacts → download → post manually.

### Kids Channel (HerooQuest)

| # | Content | Time (IST) | Platform | Status |
|---|---|---|---|---|
| 1 | Kids Story Video (16:9) | Daily | YouTube Kids | ✅ Auto |
| 2 | Kids Short (9:16) | Same workflow | YouTube Kids Shorts | ✅ Auto |
| 3 | Kids Facebook Post | Same workflow | Facebook Kids Page | ⚠️ Fixing |

---

## 7. GitHub Actions Workflows

### Trading Channel

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `main.yml` | Every 5 min (market hours) | Trading bot signals | ✅ |
| `daily-videos.yml` | 7:30 AM / 9:30 AM | Part 1 + Part 2 | ✅ |
| `daily-shorts.yml` | 11:30 AM / 1:30 PM | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM / 11:30 AM | 4 SEO articles | ✅ |
| `token_refresh.yml` | Every 50 days | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents workflow deactivation | N/A |

### Kids Channel

| File | Trigger | Purpose | Status |
|---|---|---|---|
| `daily-kids.yml` | Daily | Kids video + upload | ✅ Running |

---

## 8. Complete File Map

### Core Infrastructure

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI — Groq→Gemini→Claude→OpenAI→Templates | ✅ |
| `human_touch.py` | Anti-AI-penalty — hooks, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update | ✅ |
| `indian_holidays.py` | Mode detection — NSE API + fallback dates | ✅ |
| `content_calendar.py` | Topic rotation: Options, TA, Psychology | ✅ |

### Trading Content Generation

| File | Role | Status |
|---|---|---|
| `trading_bot.py` | Nifty200 signals + TSL + Telegram | ✅ v13.4 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ✅ — Bug 4 pending |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ✅ — Bug 3+4 pending |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | ✅ — Bug 3 pending |
| `generate_analysis.py` | 8-slide Part 1 analysis video | ✅ |
| `generate_education.py` | Part 2 education video | ✅ |
| `generate_articles.py` | 4 SEO articles → Jekyll _posts | ✅ |
| `generate_community_post.py` | YouTube community post 12:00 PM | ✅ |

### Kids Content Generation

| File | Role | Status |
|---|---|---|
| `generate_kids_video.py` | Kids story — full + short + reel | ✅ — Bug 1+2 pending |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Trading channel upload | ✅ |
| `upload_kids_youtube.py` | Kids channel upload | ✅ |
| `upload_facebook.py` | Facebook upload — Trading Page only (Group removed) | ✅ |
| `upload_instagram.py` | Kept in repo but NOT in workflows. Manual only. | 📱 |

> **IMPORTANT:** `upload_facebook.py` must NOT post to any Facebook Group. Remove all
> `FACEBOOK_GROUP_ID` references from this file. Group has no followers — wasted API calls.

### Static Assets

| Path | Contents |
|---|---|
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` + HerooQuest images |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 9. AI Client Rule — NO EXCEPTIONS

All text generation uses `ai_client.py`. Never call Groq/Gemini/Claude/OpenAI directly.
`generate_reel.py` and `generate_shorts.py` currently violate this — fix in Bug 4.

### Text Generation Fallback Chain

```
Groq llama-3.3-70b-versatile (primary — fastest, free)
    ↓ fails
Google Gemini gemini-2.0-flash (secondary)
    ↓ fails
Anthropic Claude claude-haiku-4-5 (tertiary)
    ↓ fails
OpenAI gpt-4o-mini (quaternary)
    ↓ all fail
Templates in human_touch.py (always works)
```

### Image Generation Fallback Chain (generate_kids_video.py)

```
Layer 1: Gemini imagen-3.0-generate-002
Layer 2: Gemini 2.0 Flash preview image (fix model name — Bug 2)
Layer 3: Pollinations.AI — FREE, no key ← ADD THIS
Layer 4: HuggingFace Inference API v2 (fix endpoints — Bug 2)
Layer 5: DALL-E 3 (if billing available)
Layer 6: PIL placeholder (always works)
```

### Mandatory Import Pattern — All Generators

```python
from ai_client import ai, img_client
from human_touch import ht, seo
```

### Mandatory Log Suppression Block — All Video Generators

```python
import logging, warnings
logging.getLogger("moviepy").setLevel(logging.ERROR)
logging.getLogger("imageio").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
```

---

## 10. Trading Bot Architecture

### Overview

| Component | Role |
|---|---|
| AppScript v13.3 (Google Sheets) | Scans Nifty200, writes WAITING to AlertLog, stores memory in T4 |
| Python Bot v13.4 (`trading_bot.py`) | Monitors AlertLog every 5 min, TSL updates, Telegram alerts |

**Status:** Paper trading. Dhan API → Phase 4.

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

T2 = automation switch (YES = enabled). T4 = memory string (key=value pairs).

### Nifty200 Column Map (0-based)

```
r[0]  NSE_SYMBOL   r[1]  SECTOR        r[2]  CMP           r[3]  %Change
r[4]  20_DMA       r[5]  50_DMA        r[6]  200_DMA       r[7]  SMA_Structure
r[8]  52W_Low      r[9]  52W_High      r[10] %up_52W_Low   r[11] %down_52W_High
r[12] %dist_20DMA  r[13] Avg_Vol_20D   r[14] Vol_vs_Avg%   r[15] FII_Buy_Zone
r[16] FII_Rating   r[17] Leader_Type   r[18] Signal_Score  r[19] FINAL_ACTION
r[20] RS           r[21] Sector_Trend  r[22] Breakout_Stage r[23] Retest%
r[24] Trade_Type   r[25] Priority_Score r[26] Pivot_Resistance r[27] VCP_Status
r[28] ATR14        r[29] Days_Since_Low r[30] 52W_Breakout_Score r[31] Sector_Rotation_Score
r[32] FII_Buying_Signal r[33] Master_Score
```

### AppScript v13.3 — 10 Scan Gates

1. FII SELLING → skip
2. Market regime (Nifty CMP vs 20DMA → bullish/bearish)
3. Late entry block (BREAKOUT CONFIRMED needs RS≥7)
4. Price validity (CMP>0, ATR>0, CMP≤₹5000)
5. Extension (>8% above 20DMA → skip)
6. Pivot resistance buffer (within 2% below pivot → skip)
7. Volume (bullish only — vol<120% → skip)
8. ATH buffer (within 3% of 52W high → skip)
9. Trade type (AVOID/NO TRADE → skip)
10. Sector concentration (max 2 per sector)

**Capital tiers:** ₹13,000 (MasterScore≥28+AF≥10) / ₹10,000 (MasterScore≥22) / ₹7,000 (standard)

### Python Bot v13.4 — TSL Parameters

```python
TSL_PARAMS = {
    "VCP": {"breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0},
    "MOM": {"breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0},
    "STD": {"breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0},
}
```

Hard exit: Loss > 5% → immediate. Min hold: 2d swing / 3d positional. 5d cooldown after exit.

**Daily Telegram schedule:**
- 08:45–09:15 → Good Morning (open trades P/L + sector context)
- 09:15–15:30 → Entry alerts, TSL updates, exit alerts
- 12:28–12:38 → Mid-day pulse
- 15:15–15:45 → Market close summary

**CE candidate flag (informational only):** ATR%>1.5% + bullish → Advance+Premium only.

---

## 11. Critical Upload Chain

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py → output/reel_YYYYMMDD.mp4 + meta_YYYYMMDD.json
upload_youtube.py → YouTube upload → writes public_video_url to meta
upload_facebook.py → Facebook Trading Page upload
[Instagram → manual via GitHub Actions artifacts]
```

### Kids Video (daily)

```
generate_kids_video.py
    → output/kids_video_YYYY-MM-DD.mp4
    → output/kids_short_YYYY-MM-DD.mp4
    → output/kids_reel_YYYY-MM-DD.mp4
    → output/kids_meta_YYYY-MM-DD.json

upload_kids_youtube.py → YouTube Kids full video + short
upload_facebook.py --meta-prefix kids → Facebook Kids Page (fix Bug 5 first)
    → always wrapped in try/except — workflow must not crash on FB failure
```

---

## 12. Environment Variables & Secrets

### Trading Channel

| Secret | Purpose | Status |
|---|---|---|
| `META_ACCESS_TOKEN` | Facebook Trading Page API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ |
| `META_APP_SECRET` | Facebook App Secret | ✅ |
| `FACEBOOK_PAGE_ID` | Trading Page numeric ID | ✅ |
| `FACEBOOK_GROUP_ID` | ~~Group ID~~ | ❌ Removed from workflows — group has no followers |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | ✅ |
| `INSTAGRAM_ACCOUNT_ID` | Instagram numeric ID | ⏸ Kept but not used in workflows |

### Kids Channel

| Secret | Purpose | Status |
|---|---|---|
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth JSON (HerooQuest) | ✅ |
| `META_ACCESS_TOKEN_KIDS` | Facebook Kids Page token (separate!) | ⚠️ Fix today (Bug 5) |
| `FACEBOOK_KIDS_PAGE_ID` | Kids Page numeric ID | ✅ (verify numeric not username) |
| `HF_TOKEN` | HuggingFace image generation | ✅ |

### AI Providers

| Secret | Priority | Status |
|---|---|---|
| `GROQ_API_KEY` | Primary | ✅ |
| `GEMINI_API_KEY` | Secondary | ✅ |
| `ANTHROPIC_API_KEY` | Tertiary | ✅ |
| `OPENAI_API_KEY` | Quaternary | ✅ (billing limit reached — top up or deprioritise) |

### Telegram

| Secret | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token |
| `TELEGRAM_CHAT_ID` | Free channel (@ai360trading) |
| `CHAT_ID_ADVANCE` | Advance signals (₹499/month) |
| `CHAT_ID_PREMIUM` | Premium bundle |

### Google / GCP

| Secret | Purpose |
|---|---|
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets (gspread) |
| `GH_TOKEN` | GitHub API token |

### Dhan Trading API (Phase 4 — not connected yet)

`DHAN_API_KEY`, `DHAN_API_SECRET`, `DHAN_CLIENT_ID`, `DHAN_PIN`, `DHAN_TOTP_KEY` — all added.

---

## 13. Platform Decisions & Fixes

### Facebook Group ❌ Removed

Group has no followers. All group posting code removed from `upload_facebook.py`.
Remove all `FACEBOOK_GROUP_ID` references from the file.
Secret can be kept but must be unused. May re-add if group grows in future.

### Instagram ⏸ Manual (by decision)

Instagram API is unreliable. Decision: do NOT automate Instagram for now.
Process: GitHub Actions → Run → Artifacts → Download → post to Instagram manually.
`upload_instagram.py` kept in repo but removed from all workflow YAML files.
Revisit when Meta fixes the API.

### Facebook Kids Page ⚠️ (Fix Today)

See Bug 5 in Section 3 for full fix steps.
Short version: generate a Page Access Token with video scopes for the Kids Page specifically.
Store as `META_ACCESS_TOKEN_KIDS`. Verify `FACEBOOK_KIDS_PAGE_ID` is numeric.

### YouTube Community Tab ⚠️

Requires 500+ subscribers. Below that: post text saved to
`output/community_post_YYYYMMDD.txt` — workflow does not crash.

### META_ACCESS_TOKEN Auto-Refresh ✅

`token_refresh.yml` runs every 50 days. Requires `META_APP_ID` + `META_APP_SECRET`.

---

## 14. Human Touch System (Anti-AI-Penalty)

All content uses `human_touch.py`. Never use raw AI output directly.

| Technique | Method |
|---|---|
| 50+ rotating hooks | `ht.get_hook(mode, lang)` |
| Personal phrases | `ht.get_personal_phrase(lang)` |
| TTS speed variation | `ht.get_tts_speed()` → 0.95–1.05x |
| Humanize output | `ht.humanize(text, lang)` |
| SEO tags | `seo.get_video_tags(mode, lang)` |
| Emoji rotation | `ht.get_emoji_set()` — day-seeded |
| Banned phrase removal | Strips "Certainly!", "It's important to note", etc. |

---

## 15. Technical Standards

### The "Full Code" Rule

> AI assistants must always provide **complete file content**. Partial snippets = prohibited.

```
Standard AI task prompt:
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [describe task]
Note: Provide full code for any file you modify.
```

### Dependency Pins

| Package | Version | Reason |
|---|---|---|
| `Pillow` | `>=10.3.0` | LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy crashes |
| `moviepy` | `==1.0.3` | Newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only |
| `PyNaCl` | Latest | GitHub Secret encryption |
| `google-generativeai` | Latest | Gemini fallback |
| `anthropic` | Latest | Claude fallback |
| `openai` | Latest | OpenAI fallback |
| `gspread` + `oauth2client` | Latest | Google Sheets |
| `pytz` | Latest | IST timezone |

### Voice Assignments

| Voice | Gender | Used For |
|---|---|---|
| `hi-IN-MadhurNeural` | Male | Short 2 — trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English Short (Phase 3) |
| `en-US-GuyNeural` | Male | English Short 2 alternative |

### Video Formats

| Content | Ratio |
|---|---|
| Analysis, Education, Kids Full Video | 16:9 |
| All Shorts, Reels, Morning Reel, ZENO Reel | 9:16 |

### SEO Tags — All Videos

India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

---

## 16. Reel Content Separation (Prevents Duplicate Audio/Text)

### Morning Reel (7:00 AM) — `generate_reel_morning.py`

- Energy: Upbeat, fresh, punchy — "start your day right"
- Topics: Mon=Market week ahead, Tue=Trading psychology, Wed=Chart pattern,
  Thu=Money mindset, Fri=Week review prep, Sat=Weekend learning, Sun=Investment planning
- Prompt must say: **"MORNING BRIEF 7AM — pre-market motivation — NOT the evening ZENO reel"**

### ZENO Evening Reel (8:30 PM) — `generate_reel.py`

- Energy: Wise, reflective, emotional — "what did traders learn today"
- Character: ZENO — animated wise kid in Hinglish
- Prompt must say: **"EVENING ZENO 8:30PM — end-of-day reflection — DIFFERENT from morning reel"**

---

## 17. Full Data Flow

```
Market hours (Mon–Fri, 9:15–15:30 IST)
└── main.yml every 5 min → trading_bot.py → Telegram alerts

AppScript v13.3 → Nifty200 scan → AlertLog → T4 memory

7:00 AM → daily_reel.yml (morning)
    └── generate_reel_morning.py → YouTube + Facebook Trading Page

7:30/9:30 AM → daily-videos.yml
    └── generate_analysis.py (Part 1) + generate_education.py (Part 2) → YouTube

10:00/11:30 AM → daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages + Facebook Trading Page

11:30/1:30 PM → daily-shorts.yml
    └── generate_shorts.py (Short 2 + 3) + generate_community_post.py → YouTube

8:30 PM → daily_reel.yml (evening)
    └── generate_reel.py → YouTube + Facebook Trading Page
    └── [Instagram → manual]

Daily → daily-kids.yml
    └── generate_kids_video.py → upload_kids_youtube.py → upload_facebook.py (kids page)
    └── [Instagram kids → manual]
```

---

## 18. Multilingual Strategy — Single Channel (Phase 3)

> **Decision:** No separate English channel. Reach global audiences from the same Hindi channel.

**Strategy (in order of effort):**

1. **YouTube Auto-Dubbing (free, 2 minutes to enable, big impact):**
   YouTube Studio → Content → select video → Subtitles → Auto-dub to English + Portuguese + Spanish.
   YouTube automatically dubs videos for viewers in USA/UK/Brazil in their language.
   Enable this for all existing videos + set as default for new uploads.

2. **English Short 4 (Phase 3 — one extra file per day):**
   `generate_english_short.py` → same content as Short 3 but `en-US-JennyNeural` voice.
   Upload to same Hindi channel. No separate channel needed.
   File needed: `generate_english_short.py` — add to `daily-shorts.yml`.

3. **Global SEO already working:**
   All titles/descriptions already include English global keywords via `seo.get_video_tags()`.

4. **Article website (ai360trading.in) already in English:**
   All 4 daily articles are in English → indexed by Google → USA/UK/Australia readers = high CPM.

**Files no longer needed (removed from roadmap):**
- `upload_youtube_english.py` — not needed (same channel)
- `YOUTUBE_CREDENTIALS_EN` secret — not needed

---

## 19. Disney 3D Reel Roadmap

| Phase | Tool | Status |
|---|---|---|
| 1 (Now) | PIL + MoviePy + ZENO PNG | ✅ Active |
| 2 | Gemini Veo API free tier | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | Planned |
| 4 | Google Veo 2 / Sora (when free) | Planned |

---

## 20. Website & SEO

- **URL:** ai360trading.in — GitHub Pages (Jekyll, master branch `_posts/`)
- **Auto-publishing:** `daily-articles.yml` commits to `_posts/`
- **Sitemap:** Must use `jekyll-sitemap` plugin — delete static `sitemap.xml`
- **Google Indexing:** `generate_articles.py` calls Indexing API after each article
- **robots.txt:** Fixed version from Section 23 — commit today
- **Revenue:** Google AdSense — USA/UK readers = highest CPM

---

## 21. Social Media

| Platform | Handle | Status |
|---|---|---|
| 🌐 Website | ai360trading.in | ✅ Auto |
| 📣 Telegram Free | @ai360trading | ✅ Auto |
| 📣 Telegram Advance | ai360trading_Advance ₹499/mo | ✅ Auto |
| 📣 Telegram Premium | ai360trading_Premium | ✅ Auto |
| ▶️ YouTube Trading | @ai360trading | ✅ Auto |
| ▶️ YouTube Kids | @HerooQuest | ✅ Auto |
| 📸 Instagram | @ai360trading | 📱 Manual |
| 📘 Facebook Trading Page | facebook.com/ai360trading | ✅ Auto |
| 👥 Facebook Group | facebook.com/groups/ai360trading | ❌ Removed (no followers) |
| 🐦 Twitter/X | @ai360trading | Manual |

---

## 22. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Complete
All generators upgraded. Kids channel added. 5 active bugs documented in Section 3.

### Phase 3 🔄 In Progress

| Item | Priority |
|---|---|
| Fix Bug 5 — Kids Facebook token | 🔴 Today |
| Fix Bug 1 — log spam | 🔴 High |
| Fix Bug 2 — image sources (Pollinations.AI + Gemini model name) | 🔴 High |
| Commit fixed robots.txt | 🔴 High |
| Commit fixed _config.yml (jekyll-sitemap) | 🔴 High |
| Enable YouTube Auto-Dubbing in Studio | 🟢 Easy win |
| Fix Bug 3 — reel duplicate content | 🟡 Medium |
| Fix Bug 4 — migrate reel/shorts to ai_client | 🟡 Medium |
| Remove Facebook Group from upload_facebook.py | 🟡 Medium |
| `generate_english_short.py` — English Short 4 | 🟡 Medium |
| Instagram automation — when API stable | 🔵 Future |

### Phase 4 📋 Planned — Dhan Live Trading
After 30+ paper trades validated. Win rate >35% required. Max capital: ₹45,000.

---

## 23. Files to Commit Now

### robots.txt (replace current file)

```
# robots.txt for ai360trading.in — Updated April 2026

User-agent: *
Allow: /

# Block only private/technical paths
Disallow: /assets/css/
Disallow: /assets/js/
Disallow: /cgi-bin/
Disallow: /_site/
Disallow: /admin/
Disallow: /private/
Disallow: /temp/
Disallow: /output/

# REMOVED: /_posts/ /_includes/ /_layouts/ — Jekyll source folders, never served publicly.
# Blocking these caused Googlebot redirect chain confusion → 4 pages blocked in Search Console.
# REMOVED: /tags/ /categories/ /page/ — these are real content pages and must be indexed.

User-agent: dotbot
Crawl-delay: 20

User-agent: AhrefsBot
Crawl-delay: 20

User-agent: MJ12bot
Disallow: /

Sitemap: https://ai360trading.in/sitemap.xml
```

### _config.yml — plugins + exclude section (replace current blocks)

```yaml
plugins:
  - jekyll-paginate
  - jekyll-seo-tag
  - jekyll-feed
  - jekyll-sitemap

exclude:
  - generate_articles.py
  - generate_analysis.py
  - generate_education.py
  - generate_reel.py
  - generate_reel_morning.py
  - generate_shorts.py
  - generate_kids_video.py
  - generate_community_post.py
  - generate_english_short.py
  - content_calendar.py
  - upload_youtube.py
  - upload_kids_youtube.py
  - upload_facebook.py
  - upload_instagram.py
  - trading_bot.py
  - ai_client.py
  - human_touch.py
  - indian_holidays.py
  - token_refresh.py
  - requirements.txt
  - SYSTEM.md
  - README.md
  - LICENSE.md
  - Gemfile
  - Gemfile.lock
  - .github/
  - vendor/
  - output/
  - token.json
  - sitemap.xml
```

---

## 24. Immediate Action Checklist

```
TODAY:
[ ] 1. Fix Bug 5 — Facebook Kids Page token (follow steps in Section 3)
[ ] 2. Commit fixed robots.txt from Section 23
[ ] 3. Commit fixed _config.yml (add jekyll-sitemap) from Section 23
[ ] 4. Enable YouTube Auto-Dubbing in Studio (free, 2 min, big reach)

THIS WEEK:
[ ] 5. Fix Bug 1 — add log suppression block to all 6 video generators
[ ] 6. Fix Bug 2 — add Pollinations.AI + fix Gemini model name in generate_kids_video.py
[ ] 7. Fix Bug 3 — separate morning vs evening reel prompts
[ ] 8. Fix Bug 4 — migrate generate_reel.py + generate_shorts.py to ai_client
[ ] 9. Remove FACEBOOK_GROUP_ID from upload_facebook.py completely
[ ] 10. Verify Google Indexing API is logging [INDEX] Submitted after each article

PHASE 3:
[ ] 11. Build generate_english_short.py (English Short 4 — JennyNeural voice)
[ ] 12. Add to daily-shorts.yml workflow

PHASE 4:
[ ] 13. Connect Dhan API after backtest validation (30+ paper trades, win rate >35%)
```

---

*Documentation: AI360Trading automation system.*
*Last full audit: April 12, 2026 — Claude Sonnet 4.6*
*Channels: ai360trading (trading/finance) + HerooQuest (kids)*
*Key decisions recorded:*
*— No separate English channel. Use YouTube Auto-Dubbing + English Shorts on same channel.*
*— Facebook Group removed (no followers). Add back later if needed.*
*— Instagram is manual until Meta API is reliable. No automation for now.*
*This project supports the owner's family. Every line of code matters.*
*Update this file whenever architecture, decisions, secrets, or bugs change.*
