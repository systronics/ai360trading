# AI360Trading — Master System Documentation

**Last Updated:** April 11, 2026 — Trading Bot v13.4 + AppScript v13.3
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 In Progress | Phase 4 (Dhan Live) Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
| --- | --- | --- |
| Video Ad Revenue | YouTube (Hindi — @ai360trading) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube (English) | USA, UK, Canada, Australia — 3–5x higher CPM |
| Video Ad Revenue | YouTube Kids (HerooQuest) | USA, UK, Canada, Australia — kids CPM growing |
| Shorts / Reels Bonus | YouTube, Facebook, Instagram | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| In-Stream Video Ads | Facebook Page + Facebook Kids Page (HerooQuest) | USA, UK, Brazil, India |
| Paid Signal Subscriptions | Telegram (Advance + Premium channels) | India, UAE, Global |

### Target Countries by Ad CPM Priority

1. 🇺🇸 USA — Highest CPM globally for finance + kids content
2. 🇬🇧 UK — Very high CPM, strong trading + kids audience
3. 🇦🇺 Australia — High CPM, growing retail base
4. 🇦🇪 UAE — High CPM, large NRI + Gulf investor audience
5. 🇨🇦 Canada — High CPM, similar to USA
6. 🇧🇷 Brazil — Large audience, fast-growing finance CPM
7. 🇮🇳 India — Largest volume, Nifty/stock focus

> **AI Rule:** Always optimise content topics, hooks, SEO tags, and posting times for these countries.
> USA/UK prime time = 11 PM–1 AM IST. Include global keywords in all titles, descriptions, and tags.
> All hooks and CTAs rotate from human\_touch.py — never hardcode them in generators.

---

## 2. Platform Status

| Platform | Status | Notes |
| --- | --- | --- |
| YouTube Hindi (@ai360trading) | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | 🔄 Building | Phase 3 — auto-translated separate channel |
| YouTube Kids (HerooQuest) | ✅ Auto | `kids-daily.yml` → `generate_kids_video.py` — 8:00 AM daily |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | `generate_community_post.py` — 12:00 PM daily |
| YouTube Reels (ZENO) | ✅ Auto | 8:30 PM reel working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel — **separate workflow** `daily-morning-reel.yml` |
| Facebook Page (@ai360trading) | ✅ Auto | Posts, reels, article shares all working |
| Facebook Kids Page (HerooQuest — ID 1021152881090398) | ✅ Auto | `upload_facebook.py --meta-prefix kids` |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 13 |
| Instagram (@ai360trading) | ⚠️ Partial | Upload chain built; verify `INSTAGRAM_ACCOUNT_ID` is live |
| Instagram Kids | ❌ Manual | Permanently removed from `kids-daily.yml` — upload manually from phone |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading — followers take manual entry) |

---

## 3. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at the start of every workflow and written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` environment variable — never hardcoded.

| Mode | When | Content Strategy |
| --- | --- | --- |
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu", holiday name shown |

**Detection logic:** `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates

> **Kids channel** runs every day regardless of market mode. `kids_content_calendar.py` drives topic selection independently.

---

## 4. Daily Content Output (Fully Automated)

| # | Content | Time (IST) | Platform | Status |
| --- | --- | --- | --- | --- |
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB + Instagram | ✅ |
| 2 | HerooQuest Video (16:9) + Short (9:16) + Reel (9:16) | 8:00 AM | YouTube Kids + FB Kids Page | ✅ NEW |
| 3 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube Hindi | ✅ |
| 4 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube Hindi | ✅ |
| 5 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 6 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 7 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 8 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 9 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB + Instagram | ✅ |
| 10 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| **Total** | **~16+ pieces/day** | — | — | — |

---

## 5. GitHub Actions Workflows

> **Live status confirmed from GitHub Actions page — April 11, 2026. All 10 workflows healthy.**

| File | Name in Actions | Trigger (IST) | Purpose | Status |
| --- | --- | --- | --- | --- |
| `main.yml` | AlgoTradeBot | Every 5 min (Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Running (#1241+) |
| `daily-videos.yml` | Daily Videos | 7:30 AM weekday / 9:30 AM weekend | Part 1 + Part 2 videos | ✅ Running (#74) |
| `daily-shorts.yml` | Daily Shorts | 11:30 AM weekday / 1:30 PM weekend | Short 2 + Short 3 + Community Post | ✅ Running (#41) |
| `daily-morning-reel.yml` | AI360 Daily Morning Reel (7:00 AM IST) | 7:00 AM daily | Morning Reel only | ✅ Running (#6) |
| `daily_reel.yml` | AI360 Daily ZENO Reel + Social Posting | 8:30 PM daily | ZENO Reel + FB + Instagram | ✅ Running (#47) |
| `daily-articles.yml` | Daily AI Market Intelligence Report | 10:00 AM weekday / 11:30 AM weekend | 4 SEO articles → GitHub Pages | ✅ Running (#46) |
| `kids-daily.yml` | Kids Channel — Daily Video | 8:00 AM daily (`cron: 30 2 * * *`) | HerooQuest video → YouTube Kids + FB Kids Page | ✅ Running (#14) |
| `token_refresh.yml` | Auto Token Refresh | Every 50 days | Auto META token refresh | ✅ Scheduled |
| `keepalive.yml` | KeepAlive | Periodic | Prevents GitHub disabling workflows | ✅ Active |
| `pages-build-deployment` | pages-build-deployment | On push to master | GitHub Pages deploy | ✅ Auto (#1626) |

> **`kids-daily.yml` lang input:** `both` (default — Hindi + English combined), `hi`, `en`.
> On failure, debug artifacts saved as `kids-debug-{run_id}` from `output/`.
> All workflows support `workflow_dispatch`. Kids has `lang` dropdown; others have `content_mode`.

---

## 6. Complete File Map

### Core Infrastructure (Phase 1 — Complete)

| File | Role | Status |
| --- | --- | --- |
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation (Phase 2 — All Upgraded)

| File | Role | Key Tech | Status |
| --- | --- | --- | --- |
| `trading_bot.py` | Nifty200 signal monitor + TSL manager + Telegram alerts | gspread + Sheets + Telegram Bot API | ✅ v13.4 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ai\_client, human\_touch, Edge-TTS | ✅ |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai\_client, human\_touch, MoviePy | ✅ |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai\_client, human\_touch, MoviePy | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai\_client, human\_touch, MoviePy | ✅ |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai\_client, human\_touch, content\_calendar | ✅ |
| `generate_articles.py` | 4 SEO articles daily → Jekyll \_posts | ai\_client, human\_touch, Google Indexing | ✅ |
| `generate_community_post.py` | YouTube daily community text post — 12:00 PM | ai\_client, human\_touch | ✅ |
| `generate_kids_video.py` | HerooQuest full video + Short + Reel — 8:00 AM daily | ai\_client, kids\_content\_calendar, Edge-TTS, ffmpeg, 5-layer image chain | ✅ NEW |

### Upload & Distribution

| File | Role | Status |
| --- | --- | --- |
| `upload_youtube.py` | Uploads to Hindi channel; saves `youtube_video_id` + `public_video_url` to meta | ✅ |
| `upload_kids_youtube.py` | Uploads to HerooQuest YouTube Kids channel using `YOUTUBE_CREDENTIALS_KIDS` | ✅ NEW |
| `upload_youtube_english.py` | Uploads to English channel (separate credentials) | 🔄 Phase 3 |
| `upload_facebook.py` | Main FB upload. Accepts `--meta-prefix kids` to target FB Kids Page | ✅ |
| `upload_instagram.py` | Auto-uploads via Meta API using `public_video_url` from meta | ✅ |

### Infrastructure

| File | Role |
| --- | --- |
| `indian_holidays.py` | Mode detection — NSE API + fallback; shared by ALL workflows |
| `content_calendar.py` | Rotates Hindi channel topics: Options, Technical Analysis, Psychology |
| `kids_content_calendar.py` | Rotates HerooQuest topics — returns `hindi_title`, `english_title`, `category`, `seo_tags`, `target_countries` |

### Static Assets

| Path | Contents |
| --- | --- |
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 7. AI Fallback Chain

All content generation uses `ai_client.py`. **Never call Groq/Gemini/Claude/OpenAI directly in generators.**

```
Groq — llama-3.3-70b-versatile (primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash (secondary)
    ↓ fails
Anthropic Claude — claude-haiku-4-5 (tertiary)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary)
    ↓ all fail
Pre-generated templates in human_touch.py (always works — zero downtime)
```

**Import pattern in ALL generators — no exceptions:**

```python
from ai_client import ai, img_client
from human_touch import ht, seo
```

**Usage pattern:**

```python
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
clean    = ht.humanize(raw_output, lang="hi")
hook     = ht.get_hook(mode=CONTENT_MODE, lang="hi")
tags     = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
```

---

## 8. HerooQuest Kids Channel — Full Architecture

### Characters

| Character | Description |
| --- | --- |
| **Heroo** | Brave, confident 10-year-old Indian boy. Spiky jet-black hair, warm brown skin, big expressive brown eyes, bright red and blue superhero suit with golden **H** emblem on chest, golden flowing cape. Always smiling or curious. **Must be centered in EVERY scene — main character, no exceptions.** |
| **Arya** | Cheerful 8-year-old Indian girl. Big curious brown eyes, dark hair in two braids with golden star clips, bright orange kurta. Supporting character — she asks questions, Heroo explains. |

### Visual Style (applied to every image prompt)

```
3D CGI animation render, Pixar and Disney quality,
volumetric cinematic lighting, subsurface scattering skin,
ray-traced shadows, photorealistic textures, depth of field,
ultra-detailed background, vibrant saturated colors,
child-friendly magical atmosphere, 16:9 cinematic wide shot
```

### Script Structure

Generated as JSON with exactly **6 scenes**. Each scene:

```json
{
  "id": 1,
  "narration_hi": "4 simple Hindi sentences. ~15-20 seconds.",
  "narration_en": "4 simple English sentences. ~15-20 seconds.",
  "image_prompt": "Specific Heroo + Arya poses, expressions, background.",
  "emotion": "excited"
}
```

Also: `title_hi`, `title_en`, `moral_hi`, `moral_en`, `seo_description_en`

### Language Modes (`KIDS_LANG`)

| Mode | Narration | TTS Voice |
| --- | --- | --- |
| `hi` | Hindi only | `hi-IN-SwaraNeural` |
| `en` | English only | `en-US-JennyNeural` |
| `both` (default) | Hindi + English combined per scene | `hi-IN-SwaraNeural` |

### Image Generation — 5-Layer Fallback

```
Layer 1: Gemini 2.5 Flash Image     — 500 free/day
    ↓ fail (8s wait)
Layer 2: Gemini 2.0 Flash Exp       — older free model
    ↓ fail (8s wait)
Layer 3: Hugging Face FLUX.1-schnell → SDXL → SD-v1-5
         (requires HF_TOKEN secret — free at huggingface.co)
    ↓ fail (2s wait)
Layer 4: DALL-E 3 via OPENAI_API_KEY — paid, already available
    ↓ all fail
Layer 5: Heroo branded placeholder   — colored card + golden H
         NEVER crashes. Always produces output.
```

> Scene images are **cached** — if `output/kids_scene_NN.png` exists, generation is skipped. Safe to re-run after partial failures.

### Video Pipeline (Ken Burns + ffmpeg)

```
Per scene:
  ffprobe → measure TTS audio duration (min 15s enforced)
  ffmpeg  → Ken Burns zoom (1.05x→1.001x) + libx264 ultrafast CRF 28

Concat all clips → final 16:9 MP4 (kids_video_{date}.mp4)

Derivatives:
  kids_short_{date}.mp4  → crop 405:720@x=437, scale 1080×1920, max 60s
  kids_reel_{date}.mp4   → crop 405:720@x=437, scale 1080×1920, max 90s, 44.1kHz
```

### Output Files

```
output/
  kids_script_{date}.json
  kids_scene_01.png … 06.png        ← AI images (cached between runs)
  kids_tts_1.mp3 … 6.mp3           ← Edge-TTS per scene
  clip_00.mp4 … 05.mp4             ← individual clips
  kids_video_{date}.mp4             ← final 16:9 (YouTube Kids)
  kids_short_{date}.mp4             ← 9:16 YouTube Short
  kids_reel_{date}.mp4              ← 9:16 Instagram Reel (manual upload)
  kids_meta_{date}.json             ← metadata + IDs
```

### Kids Upload Chain

```
generate_kids_video.py → kids_video + short + reel + meta

upload_kids_youtube.py
    └── YOUTUBE_CREDENTIALS_KIDS → HerooQuest YouTube channel

upload_facebook.py --meta-prefix kids
    └── META_ACCESS_TOKEN + FACEBOOK_KIDS_PAGE_ID (1021152881090398)

Instagram → MANUAL from phone (permanently removed from workflow)
    └── Download kids_reel_{date}.mp4 from GitHub Actions → Artifacts
```

### Phase 2 Upgrade Path

Current: PIL + ffmpeg Ken Burns (still images with zoom)
Next: swap `make_scene_clip()` in `generate_kids_video.py` for **Wan2.2 Colab clips** (real AI animation). No other files need changes — the function boundary is the upgrade point.

---

## 9. Trading Bot Architecture

### Overview

| Component | File | Role |
| --- | --- | --- |
| AppScript v13.3 | Google Sheets bound script | Scans Nifty200, applies 10-gate filter, writes WAITING to AlertLog, stores memory in T4 |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, WAITING→TRADED, TSL updates, exit logic, Telegram alerts |

**Status:** Paper trading. Dhan live integration planned for Phase 4.

### Google Sheets Structure

| Sheet | Purpose |
| --- | --- |
| `Nifty200` | Live data — CMP, DMAs, FII, signals, scores (34 cols) |
| `AlertLog` | Active + waiting trades (15 rows, 19 cols). T2=YES/NO switch. T4=memory |
| `History` | Closed trade log (18 cols A–R) |

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

**T2** = automation on/off (YES = enabled)
**T4** = memory string (key=value comma-separated — TSL, MAX, ATR, CAP, MODE, SEC, exit dates, daily flags)

### Nifty200 Column Map (0-based)

```
r[0]  NSE_SYMBOL          r[1]  SECTOR
r[2]  CMP                 r[3]  %Change (D)
r[4]  20_DMA              r[5]  50_DMA
r[6]  200_DMA             r[7]  SMA_Structure (H)
r[8]  52W_Low             r[9]  52W_High (J)
r[10] %up_52W_Low         r[11] %down_52W_High
r[12] %dist_20DMA (M)     r[13] Avg_Volume_20D
r[14] Volume_vs_Avg% (O)  r[15] FII_Buy_Zone (P)
r[16] FII_Rating (Q)      r[17] Leader_Type (R)
r[18] Signal_Score (S)    r[19] FINAL_ACTION (T)
r[20] RS (U)              r[21] Sector_Trend (V)
r[22] Breakout_Stage (W)  r[23] Retest% (X)
r[24] Trade_Type (Y)      r[25] Priority_Score (Z)
r[26] Pivot_Resistance(AA) r[27] VCP_Status (AB)
r[28] ATR14 (AC)          r[29] Days_Since_Low (AD)
r[30] 52W_Breakout_Score  r[31] Sector_Rotation_Score (AF)
r[32] FII_Buying_Signal(AG) r[33] Master_Score (AH)
```

### AppScript v13.3 — Key Logic

**Market Regime:** Nifty50 CMP vs 20DMA → Bullish or Bearish

**Bearish gate (all 4 required):** Leader\_Type="Sector Leader", AF≥5, Master\_Score≥22, FII≠CAUTION/SELLING

**10 scan gates:** FII SELLING skip → regime filter → late entry block → price validity → extension filter → pivot buffer → volume filter → ATH buffer → trade type → sector concentration (max 2/sector)

**Capital tiers:** ₹13,000 (Score≥28 AND AF≥10) / ₹10,000 (Score≥22 OR Accumulation) / ₹7,000 (standard)

**Trade modes:** VCP (AB<0.04 + pre-breakout) / MOM (Bull + RS≥6) / STD (default)

**Memory keys per stock:** `{sym}_CAP`, `{sym}_MODE`, `{sym}_SEC`

**Sort:** finalScore DESC, ATR% ASC tiebreaker within ±2 score (min SL preference)

### Python Bot v13.4 — Key Logic

**TSL Parameters:**

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

**TSL progression (STD):** <2% hold → 2–4% breakeven → 4–10% lock +2% → >10% ATR trail (2.5×) → >8% gap-up lock 50%

**Daily schedule:** 08:45 Good Morning → 09:15 Market open → 12:28 Mid-day pulse → 15:15 Close summary

**CE flag (v13.4):** Bullish + ATR%>1.5% → shown in Advance+Premium alerts (informational only — Dhan needed for execution)

**Hard exits:** Loss>5% immediate / min hold 2d swing 3d positional / 5-day cooldown same stock

### History Sheet (A–R)

```
A Symbol  B Entry Date  C Entry Price  D Exit Date  E Exit Price  F P/L%
G Result  H Strategy    I Exit Reason  J Trade Type K Initial SL  L TSL at Exit
M Max Price  N ATR at Entry  O Days Held  P Capital ₹  Q Profit/Loss ₹  R Options Note
```

---

## 10. Critical Upload Chains

### Evening ZENO Reel (8:30 PM) — `daily_reel.yml`

```
generate_reel.py → upload_youtube.py → upload_facebook.py → upload_instagram.py
```

### Morning Reel (7:00 AM) — `daily-morning-reel.yml` ← SEPARATE WORKFLOW

```
generate_reel_morning.py → upload_youtube.py → upload_facebook.py → upload_instagram.py
```

### Daily Videos (7:30 AM) — `daily-videos.yml`

```
generate_analysis.py (Part 1 → saves analysis_video_id.txt)
generate_education.py (Part 2 → reads Part 1 ID → links both)
```

### Kids HerooQuest (8:00 AM) — `kids-daily.yml`

```
generate_kids_video.py → upload_kids_youtube.py → upload_facebook.py --meta-prefix kids
(Instagram → MANUAL from phone)
```

---

## 11. Environment Variables & Secrets

### Dhan Trading API (Phase 4 — not connected yet)

| Secret | Status |
| --- | --- |
| `DHAN_API_KEY`, `DHAN_API_SECRET`, `DHAN_CLIENT_ID`, `DHAN_PIN`, `DHAN_TOTP_KEY` | ✅ Added — awaiting Phase 4 |

### Social Platforms

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook + Instagram (all pages) | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` / `META_APP_SECRET` | Token refresh | ✅ |
| `FACEBOOK_PAGE_ID` | Main trading FB Page | ✅ |
| `FACEBOOK_GROUP_ID` | FB Group (posting broken) | ✅ |
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest FB Page (1021152881090398) | ✅ NEW |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business numeric ID | ✅ |
| `YOUTUBE_CREDENTIALS` | Hindi channel (@ai360trading) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | English channel | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS` | HerooQuest Kids channel | ✅ NEW |

### AI Providers

| Secret | Role | Priority | Status |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Llama 3.3 70B | Primary | ✅ |
| `GEMINI_API_KEY` | Gemini 2.5/2.0 Flash + Image | Secondary + Kids Layer 1&2 | ✅ |
| `ANTHROPIC_API_KEY` | Claude Haiku | Tertiary | ✅ |
| `OPENAI_API_KEY` | GPT-4o-mini + DALL-E 3 (Kids Layer 4) | Quaternary | ✅ |
| `HF_TOKEN` | HuggingFace FLUX.1 (Kids Layer 3) | Kids only | ⚠️ Add if missing |

### Other

| Secret | Purpose |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot auth |
| `TELEGRAM_CHAT_ID` | Free channel |
| `CHAT_ID_ADVANCE` | Advance (₹499/mo) |
| `CHAT_ID_PREMIUM` | Premium (bundle) |
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console + gspread |
| `GH_TOKEN` | GitHub API |

---

## 12. Human Touch System (Anti-AI-Penalty)

All **trading/finance** content must pass through `human_touch.py`. **Never use raw AI output.**

| Technique | Method |
| --- | --- |
| 50+ rotating hooks | `ht.get_hook(mode, lang)` |
| Personal phrases | `ht.get_personal_phrase(lang)` |
| TTS speed variation | `ht.get_tts_speed()` — 0.95–1.05x |
| Humanize output | `ht.humanize(text, lang)` |
| Emoji rotation | `ht.get_emoji_set()` — day-seeded |
| SEO tags | `seo.get_video_tags(mode, lang)` |
| Connector variation + banned phrase removal | Internal to `humanize()` |

> **Kids channel exception:** `generate_kids_video.py` calls `ai.generate_json()` directly for structured script. TTS rate is fixed at `-10%` (slower for children) — `ht.get_tts_speed()` is NOT applied to kids narration.

---

## 13. Known Issues & Fixes

### Facebook Group Posting ❌

Missing `publish_to_groups` scope on `META_ACCESS_TOKEN`. Fix: developers.facebook.com → App → add scope → regenerate token → update secret. `token_refresh.yml` will then auto-maintain it.

### Instagram — Main Channel ⚠️

Verify `INSTAGRAM_ACCOUNT_ID` via:
```
https://graph.facebook.com/me/accounts?access_token=YOUR_META_TOKEN
```
Upload order is critical: YouTube → Facebook → Instagram.

### Instagram — Kids Channel ❌ Permanent

Permanently removed from `kids-daily.yml`. Always download `kids_reel_{date}.mp4` from GitHub Actions → Artifacts → upload manually from phone.

### YouTube Community Tab ⚠️

Requires 500+ subscribers. Below threshold: post text saved to `output/community_post_YYYYMMDD.txt`, workflow does not crash.

### HF\_TOKEN — Not Yet Added ⚠️

Kids image Layer 3 (FLUX.1) is skipped until `HF_TOKEN` is added. Get free token: huggingface.co → Settings → Access Tokens.

### Kids Scene Image Caching ✅

Existing `output/kids_scene_NN.png` files are reused. Safe to re-run after partial failure — only missing scenes regenerate.

---

## 14. Technical Standards

### The "Full Code" Rule

> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited.

```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the full code for any file you modify.
```

### AI Client Usage — No Exceptions

```python
from ai_client import ai, img_client
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang=LANG)
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
```

> **Kids image exception:** `generate_kids_video.py` uses its own 5-layer image chain directly. Phase 2 will consolidate via `img_client`.

### Human Touch — No Exceptions (finance generators)

```python
from human_touch import ht, seo
hook  = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
clean = ht.humanize(raw_script, lang=LANG)
tags  = seo.get_video_tags(mode=CONTENT_MODE, lang=LANG)
speed = ht.get_tts_speed()   # NOT used in kids generator
```

### Dependency Pins

| Package | Version | Reason |
| --- | --- | --- |
| `Pillow` | `>=10.3.0` | LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy crashes |
| `moviepy` | `==1.0.3` | Newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only |
| `PyNaCl` | Latest | GitHub Secret encryption |
| `google-genai` | Latest | Gemini 2.5/2.0 Flash Image (kids + fallback) |
| `anthropic` | Latest | Claude fallback |
| `openai` | Latest | GPT-4o-mini + DALL-E 3 (kids layer 4) |
| `gspread` | Latest | Google Sheets |
| `oauth2client` | Latest | GCP service account |
| `pytz` | Latest | IST timezone |
| `huggingface-hub` + `requests` | Latest | Kids HF image layer 3 |

> **Kids system deps (apt-get):** `ffmpeg`, `fonts-dejavu`, `fonts-liberation`

### Voice Assignments

| Voice | Gender | Used For |
| --- | --- | --- |
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education, Kids (hi/both) |
| `en-US-JennyNeural` | Female | English channel, Kids (en mode) |
| `en-US-GuyNeural` | Male | English Short 2 alternative |

### TTS Rate

```python
# Finance generators — variable via human_touch
rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
await edge_tts.Communicate(text, VOICE, rate=rate_str).save(path)

# Kids generator — fixed slower rate
await edge_tts.Communicate(text, voice, rate="-10%").save(str(out_path))
```

### Video Formats

| Content | Ratio | Resolution | Platform |
| --- | --- | --- | --- |
| Analysis + Education | 16:9 | Standard | YouTube Hindi |
| Kids HerooQuest | 16:9 | 1280×720 | YouTube Kids |
| Kids Short | 9:16 | 1080×1920 (crop 405:720@x=437) | YouTube Shorts |
| Kids Reel | 9:16 | 1080×1920 (crop 405:720@x=437), 44.1kHz | Instagram (manual) |
| Short 2, Short 3, Morning Reel, ZENO Reel | 9:16 | Standard | YouTube Shorts / Reels / Instagram |

---

## 15. Disney 3D Reel Roadmap

### Main Channel (@ai360trading)

| Phase | Tool | Status |
| --- | --- | --- |
| 1 (Now) | PIL + MoviePy + ZENO PNG | ✅ Active |
| 2 | Gemini Veo API | Hooks in `img_client` |
| 3 | Stable Diffusion + AnimateDiff | Planned |
| 4 | Google Veo 2 / Sora | Planned |

### Kids Channel (HerooQuest)

| Phase | Tool | Status |
| --- | --- | --- |
| 1 (Now) | PIL + ffmpeg + Ken Burns zoom | ✅ Active |
| 2 | Wan2.2 Colab clips | Swap `make_scene_clip()` — no other changes |

---

## 16. Full Data Flow

```
Market hours Mon–Fri 9:15–3:30 IST
└── main.yml every 5 min → trading_bot.py → Sheets → TSL → Telegram

AppScript v13.3 (manual or scheduled)
└── 10-gate scan → AlertLog → T4 memory → Telegram bearish alert

7:00 AM daily — daily-morning-reel.yml (SEPARATE workflow)
└── generate_reel_morning.py → upload chain

8:00 AM daily — kids-daily.yml
└── generate_kids_video.py
    └── kids_content_calendar.get_today_topic()
    └── ai.generate_json() → 6-scene script
    └── 5-layer image chain (Gemini 2.5 → 2.0 → HF → DALL-E → placeholder)
    └── edge_tts rate="-10%" per scene (8s delay between API calls)
    └── ffmpeg Ken Burns → clips → concat → video + short + reel
└── upload_kids_youtube.py (YOUTUBE_CREDENTIALS_KIDS)
└── upload_facebook.py --meta-prefix kids (FACEBOOK_KIDS_PAGE_ID)
└── Instagram → MANUAL from phone

7:30 AM / 9:30 AM — daily-videos.yml
└── generate_analysis.py (Part 1) → generate_education.py (Part 2) → YouTube

10:00 AM / 11:30 AM — daily-articles.yml
└── generate_articles.py → 4 articles → GitHub Pages + Facebook

11:30 AM / 1:30 PM — daily-shorts.yml
└── generate_shorts.py → Short 2 + Short 3
└── generate_community_post.py → Community Tab

8:30 PM — daily_reel.yml
└── generate_reel.py → ZENO reel
└── upload_youtube.py → upload_facebook.py → upload_instagram.py
```

---

## 17. Website

* **URL:** `ai360trading.in` — GitHub Pages (Jekyll, `master` / `_posts/`)
* **Publishing:** Auto-commit by `daily-articles.yml`
* **SEO:** Instant indexing via `GCP_SERVICE_ACCOUNT_JSON`
* **Revenue:** Google AdSense (USA/UK = highest CPM)
* **Pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading
* **Markets:** India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto

---

## 18. Social Media Links

| Platform | Handle/Link |
| --- | --- |
| 🌐 Website | ai360trading.in |
| 📣 Telegram (Free) | @ai360trading |
| 📣 Telegram (Advance) | ai360trading\_Advance — ₹499/month |
| 📣 Telegram (Premium) | ai360trading\_Premium — bundle |
| ▶️ YouTube (Trading) | @ai360trading |
| ▶️ YouTube (Kids) | HerooQuest channel |
| 📸 Instagram | @ai360trading |
| 👥 Facebook Group | facebook.com/groups/ai360trading |
| 📘 Facebook Page (Trading) | facebook.com/ai360trading |
| 📘 Facebook Page (Kids) | HerooQuest — ID 1021152881090398 |
| 🐦 Twitter/X | @ai360trading |

---

## 19. Phase Roadmap

### Phase 1 ✅ Complete

`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Complete

All `generate_*.py` + `kids_content_calendar.py` + `upload_kids_youtube.py` — upgraded to ai\_client + human\_touch. HerooQuest Kids channel fully live.

### Phase 3 🔄 In Progress

| Item | Priority |
| --- | --- |
| Fix Facebook Group token (`publish_to_groups` scope) | 🔴 High |
| Verify Instagram main channel live end-to-end | 🔴 High |
| Add `HF_TOKEN` secret for Kids image Layer 3 | 🟡 Medium |
| English channel — `generate_english.py` + `upload_youtube_english.py` | 🟡 Medium |
| Kids Phase 2 — Wan2.2 animation (swap `make_scene_clip()`) | 🔵 Future |
| Disney 3D main reel — `img_client` Phase 2 | 🔵 Future |

### Phase 4 📋 Planned — Dhan Live Trading

Backtest validation (30–40 paper trades, win rate >35%) → Dhan API connection → Options CE execution → Live ₹45,000 capital deployment (₹5k buffer)

---

## 20. How to Test Everything

### Workflow manual trigger

GitHub Actions → select workflow → **Run workflow** → set dropdown.

### Kids channel test

```
workflow_dispatch → kids-daily.yml → lang = both
```
Check logs for: `[IMG-1] Scene N via Gemini 2.5 Flash Image ✓` or `[LAYER-5]` if all AI fails.
On failure: download `kids-debug-{run_id}` artifact from Actions → Artifacts.

### Trading bot logs (main.yml)

```
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[TSL] NSE:ONGC [STD]: ₹280.60→₹285.20
[DONE] 15:20:01 IST | mem=842 chars
```

### AppScript test

Google Sheet → AI360 TRADING menu → MANUAL SYNC → Logger:
```
[CAND] NSE:ADANIPOWER | Score=24 | ₹10000 | STD | AF=8.2 | Qty=64
```

### Force content modes

```
workflow_dispatch → content_mode = market / weekend / holiday
workflow_dispatch (kids) → lang = both / hi / en
```

### Automation switch

Google Sheet → AlertLog → cell T2 → `YES` to enable.

---

## 21. Workflow Health Summary (April 11, 2026)

| Workflow | File | Run # | Status |
| --- | --- | --- | --- |
| AlgoTradeBot | `main.yml` | #1241+ | ✅ Healthy |
| Daily Videos | `daily-videos.yml` | #74 | ✅ Healthy |
| Daily Shorts | `daily-shorts.yml` | #41 | ✅ Healthy |
| AI360 Daily Morning Reel | `daily-morning-reel.yml` | #6 | ✅ Healthy |
| AI360 Daily ZENO Reel | `daily_reel.yml` | #47 | ✅ Healthy |
| Daily AI Market Intelligence | `daily-articles.yml` | #46 | ✅ Healthy |
| Kids Channel — HerooQuest | `kids-daily.yml` | #14 | ✅ Healthy |
| Auto Token Refresh | `token_refresh.yml` | — | ✅ Scheduled |
| KeepAlive | `keepalive.yml` | — | ✅ Active |
| pages-build-deployment | Auto | #1626 | ✅ Healthy |

**Overall: 🟢 ALL SYSTEMS OPERATIONAL**

---

*Documentation maintained by AI360Trading automation.*
*Full audit: April 11, 2026 — Claude Sonnet 4.6*
*Phase 1 + 2 complete. HerooQuest Kids channel fully live and documented.*
*Phase 3: FB Group fix, Instagram verify, HF\_TOKEN, English channel, Kids Wan2.2*
*Phase 4: Dhan live trading after backtest validation*
*Key corrections from April 3 version:*
*— daily-morning-reel.yml is a SEPARATE workflow from daily\_reel.yml*
*— kids-daily.yml was entirely missing — now fully documented: HerooQuest characters, 5-layer image chain, Ken Burns ffmpeg pipeline, generate\_kids\_video.py, upload\_kids\_youtube.py, kids\_content\_calendar.py, FB Kids Page ID 1021152881090398, Instagram permanently manual*
*— FACEBOOK\_KIDS\_PAGE\_ID, YOUTUBE\_CREDENTIALS\_KIDS, HF\_TOKEN added to secrets table*
*— Section 21 (Workflow Health) added with live run counts*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
