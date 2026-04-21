# AI360Trading — Master System Documentation

**Last Updated:** April 21, 2026 — Trading Bot v13.4 + AppScript v13.3
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 In Progress | Phase 4 (Dhan Live) 📋 Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
| --- | --- | --- |
| Video Ad Revenue | YouTube (Hindi) — @ai360trading | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube (English) — Phase 3 | USA, UK, Canada, Australia — 3–5x higher CPM |
| Video Ad Revenue | YouTube Kids — @HerooQuest | USA, UK, Canada, Australia |
| Shorts / Reels Bonus | YouTube, Facebook, Instagram | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| In-Stream Video Ads | Facebook Page | USA, UK, Brazil, India |
| Paid Signal Subscriptions | Telegram (Advance + Premium channels) | India, UAE, Global |
| Affiliate Commissions | PolicyBazaar (IN), Policygenius (US), CompareTheMarket (UK) | India, USA, UK |
| Affiliate Commissions | Zerodha (IN), Webull (US), Trading212 (UK) | India, USA, UK |

### Target Countries by Ad CPM Priority

1. 🇺🇸 USA — Highest CPM globally for finance content
2. 🇬🇧 UK — Very high CPM, strong trading audience
3. 🇦🇺 Australia — High CPM, growing retail base
4. 🇦🇪 UAE — High CPM, large NRI + Gulf investor audience
5. 🇨🇦 Canada — High CPM, similar to USA
6. 🇧🇷 Brazil — Large audience, fast-growing finance CPM
7. 🇮🇳 India — Largest volume, Nifty/stock focus

> **AI Rule:** Always optimise content topics, hooks, SEO tags, and posting times for these countries.
> USA/UK prime time = 11 PM–1 AM IST. Include global keywords in all titles, descriptions, and tags.
> All hooks and CTAs rotate from human_touch.py — never hardcode them in generators.

---

## 2. Platform Status

| Platform | Status | Notes |
| --- | --- | --- |
| YouTube Hindi (@ai360trading) | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | 🔄 Building | Phase 3 — separate channel, auto-translated |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily — requires 500+ subs |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate_reel_morning.py) working |
| YouTube Kids (@HerooQuest) | ✅ Auto | kids-daily.yml — 8:00 AM IST daily — Hindi + English |
| Facebook Page (ai360trading) | ✅ Auto | Posts, reels, article shares working |
| Facebook Kids Page (HerooQuest) | ✅ Auto | upload_facebook.py --meta-prefix kids |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 14 |
| Instagram (@ai360trading) | ⚠️ Partial | Upload chain built; verify live |
| Instagram (HerooQuest Kids) | ❌ Manual | No auto-upload — post manually from phone after YouTube goes live |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading) |

---

## 3. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` and written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` — never hardcoded.

| Mode | When | Content Strategy |
| --- | --- | --- |
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu", holiday name shown |

**Detection logic:** `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates

> **Kids Channel** does not use CONTENT_MODE. It runs independently via `KIDS_LANG` env var (`both` / `hi` / `en`).

---

## 4. Daily Content Output (Fully Automated)

| # | Content | Time (IST) | Platform | Status |
| --- | --- | --- | --- | --- |
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB + Instagram | ✅ |
| 2 | HerooQuest Kids Video | 8:00 AM | YouTube Kids + FB Kids | ✅ |
| 3 | Part 1 Analysis Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 4 | Part 2 Education Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 5 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 6 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 7 | Short 4 English (9:16) | 11:30 AM (same workflow) | YouTube English Shorts | 🔄 Phase 3 |
| 8 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 9 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB + Instagram | ✅ |
| 10 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| **Total** | **12–13 pieces/day** | — | — | — |

> **USA/UK prime time:** Videos upload at IST times but SEO metadata targets 11 PM–1 AM IST keywords for US/UK peak discovery. See Section 9 for optimal scheduling.

---

## 5. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware | Status |
| --- | --- | --- | --- | --- |
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ | ✅ Running |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 + Part 2 | ✅ | ✅ Running |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post | ✅ | ✅ Running |
| `daily-morning-reel.yml` | 7:00 AM daily | Morning Reel (separate from daily_reel.yml) | ✅ | ✅ Running |
| `daily_reel.yml` | 8:30 PM daily | ZENO Reel + Social Posting | ✅ | ✅ Running |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ | ✅ Running |
| `kids-daily.yml` | 8:00 AM daily (2:30 UTC) | HerooQuest video + YouTube Kids + FB Kids | ❌ (independent) | ✅ Running |
| `token_refresh.yml` | Every 50 days (1st + 20th of month) | Auto META token refresh | N/A | ✅ |
| `keepalive.yml` | Periodic | Prevents GitHub disabling workflows | N/A | ✅ |

All content workflows support `workflow_dispatch` with `content_mode` dropdown. Kids workflow supports `lang` dropdown (`both` / `hi` / `en`).

---

## 6. Complete File Map

### Core Infrastructure (Phase 1 — Complete)

| File | Role | Status |
| --- | --- | --- |
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation (Phase 2)

| File | Role | ai_client? | Status |
| --- | --- | --- | --- |
| `trading_bot.py` | Nifty200 signals + TSL manager + Telegram alerts | N/A | ✅ v13.4 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ✅ | ✅ |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ✅ fixed April 2026 | ✅ |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | ✅ | ✅ |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ✅ | ✅ |
| `generate_education.py` | Educational deep-dive video (Part 2) | ✅ | ✅ |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | ❌ Groq direct | ⚠️ P1 fix |
| `generate_community_post.py` | YouTube community text post — 12:00 PM | ✅ | ✅ |
| `generate_kids_video.py` | HerooQuest kids video (Hindi + English) | Separate AI stack | ✅ |

> ⚠️ **`generate_articles.py` is the last remaining ai_client violation.** It has two direct Groq calls — the AI title generator and the article body generator. Both need refactoring to use `ai_client.py`. See Section 14 for exact fix.

### Upload & Distribution

| File | Role | Status |
| --- | --- | --- |
| `upload_youtube.py` | Hindi channel upload + meta file write | ✅ |
| `upload_youtube_english.py` | English channel upload | 🔄 Phase 3 |
| `upload_kids_youtube.py` | HerooQuest Kids channel upload | ✅ |
| `upload_facebook.py` | FB Page reels + articles; supports `--meta-prefix kids` flag | ✅ |
| `upload_instagram.py` | Meta API upload via public_video_url from meta file | ⚠️ Verify |

### Infrastructure

| File | Role |
| --- | --- |
| `indian_holidays.py` | Mode detection — NSE API + fallback; shared by all workflows |
| `content_calendar.py` | Topic rotation + `get_article_seo_seeds()` for long-tail keyword strategy |

### Static Assets

| Path | Contents |
| --- | --- |
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 7. AI Fallback Chain

All main trading/finance generators use `ai_client.py`. **Never call AI APIs directly in generators.**

```
Groq — llama-3.3-70b-versatile (primary — fastest, free tier)
    ↓ fails
Google Gemini — gemini-2.0-flash (secondary — free tier, 1,500 req/day)
    ↓ fails
Anthropic Claude — claude-haiku-4-5 (tertiary — pay-as-you-go)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary — pay-as-you-go)
    ↓ all fail
Pre-generated templates in human_touch.py (always works — zero downtime)
```

**Import pattern in ALL main generators — no exceptions:**

```python
from ai_client import ai, img_client
from human_touch import ht, seo
```

**Usage:**

```python
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
clean    = ht.humanize(raw_output, lang="hi")
hook     = ht.get_hook(mode=CONTENT_MODE, lang="hi")
tags     = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
```

> **Kids Channel exception:** `generate_kids_video.py` has its own AI stack (Gemini primary via `google-genai`). This is intentional — it is a standalone system that does not share the finance content pipeline.

---

## 8. Free Tier Limits — Critical Awareness

| Service | Free Tier | Est. Daily Usage | Risk |
| --- | --- | --- | --- |
| **GitHub Actions** | Unlimited (public repo) | All workflows | ✅ Safe |
| **Groq API** | llama-3.3-70b: ~14,400 req/day; 6,000 tok/min | Articles (~2 req) + Kids fallback = ~5 req/day | ✅ Safe |
| **Gemini API** | gemini-2.0-flash: 1,500 req/day | Kids primary + finance fallback | ✅ Safe, monitor |
| **Claude API** | Pay-as-you-go — NO free tier | Tertiary fallback only | ⚠️ Cost if Groq+Gemini fail |
| **OpenAI API** | Pay-as-you-go — NO free tier | Quaternary fallback only | ⚠️ Cost as last resort |
| **YouTube Data API** | 10,000 units/day | ~4–5 uploads + community post ≈ 900 units | ✅ Safe |
| **Meta Graph API** | Rate limited per token | 2 reels + articles/day | ✅ Safe |
| **Google Indexing API** | 200 req/day | 4 articles/day | ✅ Safe |
| **Yahoo Finance** | Unofficial — no hard limit | ~21 symbols per articles run | ⚠️ Use `fast_info` only |
| **Google Trends** | Unofficial — no hard limit | 4 regions per run | ⚠️ Rotate gently |
| **edge-tts** | Genuinely free (Microsoft) | All Hindi/English audio | ✅ Safe |
| **GitHub Pages** | 1 GB storage, 100 GB bandwidth/month | MAX_POSTS=120 ≈ 1.2 MB | ✅ Safe |

> **Key risk:** Claude and OpenAI are NOT free. Gemini is now dual-purpose (Kids primary + finance fallback) — watch daily usage if Kids Channel scales up content volume.

---

## 9. Optimal Posting Times for Maximum CPM

| Market | Best IST Posting Time | Reason |
| --- | --- | --- |
| 🇺🇸 USA (EST) | 11:00 PM – 1:00 AM IST | Lunch break peak (12:30–3:30 PM EST) |
| 🇺🇸 USA (PST) | 1:00 AM – 3:00 AM IST | Lunch break peak PST |
| 🇬🇧 UK | 3:30 PM – 7:30 PM IST | Working hours (11 AM–3 PM GMT) |
| 🇦🇺 Australia | 4:30 AM – 9:30 AM IST | Morning peak AEDT |
| 🇧🇷 Brazil | 9:00 PM – 12:00 AM IST | Lunch peak BRT |
| 🇮🇳 India | 7:30 AM – 10:00 AM IST | Pre-market + morning |
| 👶 Kids (global) | 8:00 AM IST — keep | India morning; aligns with after-school US/UK on same day |

> **Action:** Add `publishAt` timestamp to `upload_youtube.py`. Best single time to maximise combined USA + UK + India reach: **8:30 PM IST** — ZENO reel already uses this naturally. Apply to other uploads.

---

## 10. Video SEO — Auto Translate, Transcript, Subtitles

### What Is Working

| Feature | Status |
| --- | --- |
| SEO hashtags in videos | ✅ `seo.get_video_tags()` wired in `generate_reel.py` |
| YouTube auto-captions | ✅ YouTube generates automatically |
| Article SEO URL slugs | ✅ Clean slugs + HHMM uniqueness suffix |
| Article JSON-LD schema | ✅ Article + BreadcrumbList on all posts |
| Article live price strip | ✅ `nifty_level`, `sp500_level`, `bitcoin_level`, `gold_level` in front matter |
| Long-tail keyword seeds | ✅ `content_calendar.get_article_seo_seeds()` in articles |
| Google de-indexing on delete | ✅ `notify_google_url_deleted()` in cleanup |

### Still Missing (High Revenue Impact)

| Feature | Free Method | Effort |
| --- | --- | --- |
| English title + description on YouTube | Add `localizations` in upload body | 2 hours |
| Hindi SRT subtitles | Script text + duration → `.srt` → `captions.insert` API | 3 hours |
| Scheduled publish time | Add `publishAt` to upload body | 1 hour |

**English localizations in `upload_youtube.py`:**
```python
"localizations": {
    "en": {
        "title": ai.generate(f"Translate to concise English title: {hindi_title}", lang="en"),
        "description": ai.generate(f"Translate to English: {hindi_desc[:500]}", lang="en")
    }
}
```

---

## 11. HerooQuest Kids Channel

**Brand:** HerooQuest
**YouTube:** @HerooQuest (separate Kids channel)
**Facebook Page:** HerooQuest (ID: 1021152881090398)
**Instagram:** Manual upload only — no automation

### Workflow: `kids-daily.yml`

| Item | Value |
| --- | --- |
| Schedule | 8:00 AM IST daily (`cron: '30 2 * * *'`) |
| Language | `KIDS_LANG` env var — default `both`; force `hi` or `en` via dispatch |
| Generator | `generate_kids_video.py` |
| YouTube upload | `upload_kids_youtube.py` |
| Facebook upload | `upload_facebook.py --meta-prefix kids` |
| Instagram | ❌ Manual — upload from phone after YouTube goes live |
| Debug artifacts | Saved on failure as `kids-debug-{run_id}` |

### Kids AI Stack (independent from main system)

```
Google Gemini (google-genai) — primary
Groq (llama-3.3-70b) — fallback 1
Anthropic Claude — fallback 2
OpenAI GPT — fallback 3
```

Kids workflow installs its own packages directly in the workflow step — not from `requirements.txt`.

### Kids-Specific Secrets

| Secret | Purpose |
| --- | --- |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth for HerooQuest channel |
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest Facebook Page ID |
| `HF_TOKEN` | HuggingFace token (image generation) |
| `GEMINI_API_KEY` | Shared with main system |
| `GROQ_API_KEY` | Shared with main system |
| `ANTHROPIC_API_KEY` | Shared with main system |
| `OPENAI_API_KEY` | Shared with main system |
| `META_ACCESS_TOKEN` | Shared with main system |

---

## 12. Trading Bot Architecture

### Overview

| Component | File | Role |
| --- | --- | --- |
| AppScript v13.3 | Google Sheets bound script | Scans Nifty200, filters, writes WAITING to AlertLog, stores memory in T4 |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, WAITING→TRADED, TSL, exits, Telegram |

**Current status:** Paper trading. Followers take manual entry from Telegram signals. Dhan Phase 4 planned.

### Google Sheets Structure

| Sheet | Purpose |
| --- | --- |
| `Nifty200` | Live data for all 200 stocks — CMP, DMAs, FII data, signals, scores (34 cols) |
| `AlertLog` | Active + waiting trades — 15 rows, 19 cols. T2=YES/NO switch. T4=memory string |
| `History` | Closed trade log — 18 cols A–R |

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

**T2** = automation switch (`YES` to enable)
**T4** = memory string — `{sym}_CAP`, `{sym}_MODE`, `{sym}_SEC`, TSL/MAX/ATR values, exit dates, daily flags

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

**Market Regime:** Nifty50 CMP vs 20DMA → Bullish or Bearish.

**Bearish gate (4 conditions all required):**
- Leader_Type = "Sector Leader"
- AF ≥ 5 (RS≥2.5 with sector tailwind)
- Master_Score ≥ 22
- FII signal ≠ "FII CAUTION" or "FII SELLING"

**10 scan gates (in order):**
1. FII SELLING → skip always
2. Market regime filter (bullish vs bearish path)
3. Late entry block (BREAKOUT CONFIRMED needs RS≥7)
4. Price validity (CMP>0, ATR>0, CMP≤₹5000)
5. Extension filter (>8% above 20DMA → skip)
6. Pivot resistance buffer (within 2% below pivot → skip)
7. Volume filter (bullish only — vol<120% → skip)
8. ATH buffer (within 3% of 52W high → skip)
9. Trade type (AVOID/NO TRADE → skip)
10. Sector concentration (max 2 per sector)

**Capital tiers:**
- ₹13,000 — MasterScore≥28 AND AF≥10
- ₹10,000 — MasterScore≥22 OR Accumulation Zone
- ₹7,000 — standard

**Trade modes:** VCP (AB<0.04 + pre-breakout) | MOM (Strong Bull + RS≥6) | STD (default/bearish)

**Sort:** finalScore DESC, then ATR% ASC as tiebreaker within ±2 score points.

### Python Bot v13.4 — TSL Parameters

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

**TSL progression (STD):** <2% hold SL → 2–4% breakeven → 4–10% lock+2% → >10% ATR trail → >8% gap-up lock 50%

**Daily message schedule:** 08:45 GM | 09:15–15:30 market hours | 12:28 mid-day | 15:15 close summary

**CE candidate flag (informational):** ATR% 1.5–2.5% = normal mover (+65%/-40%); ATR% >2.5% = fast mover (+50%/-35%)

**Hard exit:** >5% loss = immediate exit | 2-day swing / 3-day positional min hold | 5-day cooldown post-exit

### History Sheet Columns (A–R)

```
A  Symbol      B  Entry Date   C  Entry Price  D  Exit Date
E  Exit Price  F  P/L%         G  Result        H  Strategy
I  Exit Reason J  Trade Type   K  Initial SL    L  TSL at Exit
M  Max Price   N  ATR at Entry O  Days Held     P  Capital ₹
Q  Profit/Loss ₹               R  Options Note
```

---

## 13. Critical Upload Chain

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json  (public_video_url = "")

upload_youtube.py → writes youtube_video_id + public_video_url to meta
upload_facebook.py → FB Page + overwrites public_video_url in meta
upload_instagram.py → reads public_video_url → polls FINISHED → publishes
```

### Morning Reel (7:00 AM)

```
generate_reel_morning.py → morning_reel_YYYYMMDD.mp4 + morning_reel_meta
upload_youtube.py (morning mode) → upload_facebook.py → upload_instagram.py
```

### Daily Videos (7:30 AM)

```
generate_analysis.py → analysis_video.mp4 + analysis_video_id.txt
generate_education.py → reads analysis_video_id.txt → links Part 1 → education_video.mp4
```

### Kids Channel (8:00 AM)

```
generate_kids_video.py → kids_video_YYYYMMDD.mp4 + kids_meta_YYYYMMDD.json
upload_kids_youtube.py → HerooQuest YouTube channel
upload_facebook.py --meta-prefix kids → HerooQuest Facebook Page
[Instagram → manual upload from phone]
```

---

## 14. Known Issues & Fixes

### 🔴 P1: `generate_articles.py` calls Groq directly

**Problem:** Has `from groq import Groq` + `client = Groq(...)` — two direct Groq calls (title generator + article body). Zero fallback if Groq fails.

**Fix — replace both Groq calls:**

```python
# Remove from top of file:
# from groq import Groq
# client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Add:
from ai_client import ai

# Replace title generator call:
ai_title_raw = ai.generate(
    title_prompt,
    system_prompt="You generate precise financial article titles. Respond with only the title text.",
    content_mode=CONTENT_MODE,
    lang="en",
    max_tokens=60,
    temperature=0.9
)
ai_title = ai_title_raw.strip().strip('"').strip("'")

# Replace article body call:
content = ai.generate(
    prompt,
    system_prompt=f"You are Amit Kumar of AI360Trading writing as a {persona['name']}...",
    content_mode=CONTENT_MODE,
    lang="en",
    max_tokens=5500,
    temperature=0.88
)
```

### ❌ Facebook Group Posting

**Fix steps:**
1. developers.facebook.com → App → Add `publish_to_groups` permission
2. Ensure bot is Admin of the group
3. Group Settings → Advanced → "Allow content from apps" ON
4. Regenerate token → update `META_ACCESS_TOKEN` secret
5. `token_refresh.yml` will maintain it automatically once scope is added

### ⚠️ Instagram Auto-Post — Verify

Upload chain must complete in order. Facebook must run first to write `public_video_url`. Check logs for `FINISHED` from Instagram polling.

```
https://graph.facebook.com/me/accounts?access_token=TOKEN
```
Confirm `INSTAGRAM_ACCOUNT_ID` matches the numeric ID in the response.

### ⚠️ YouTube Community Tab — 500 Subs Required

`generate_community_post.py` saves to `output/community_post_YYYYMMDD.txt` without crashing if channel is below threshold. Enable in YouTube Studio → Customization → Layout → Community Tab once reached.

### ✅ META Token Auto-Refresh

`token_refresh.yml` handles this every 50 days automatically. `META_APP_ID` and `META_APP_SECRET` already added.

### ✅ Article Slug Uniqueness Fixed

HHMM time suffix appended to all slugs. Two articles with similar titles on the same day get different permalinks and never overwrite each other.

### ✅ Google De-indexing on Article Delete Fixed

`cleanup_old_posts()` reads each deleted post's permalink from front matter and calls `notify_google_url_deleted()` with `URL_DELETED`. Google removes it from search index immediately.

### ✅ MAX_POSTS Raised to 120

Old value of 60 was deleting articles Google had already indexed (causing GSC 404 errors). 120 posts ≈ 30 days history ≈ 1.2 MB storage — well within GitHub Pages limits.

### ✅ Live Price Strip in Article Front Matter Fixed

`nifty_level`, `sp500_level`, `bitcoin_level`, `gold_level` now written to all post front matter. The `post.html` layout can render a live data strip using these fields.

### ✅ Affiliate Links in Articles

`get_affiliate_block(pillar_id)` injects PolicyBazaar / Policygenius / CompareTheMarket / Zerodha / Webull links naturally. Max 3 per article, never labelled "sponsored".

---

## 15. Environment Variables & Secrets

### Trading API (Phase 4)

| Secret | Purpose | Status |
| --- | --- | --- |
| `DHAN_API_KEY` | Dhan API key | ✅ Added — not connected |
| `DHAN_API_SECRET` | Dhan API secret | ✅ Added |
| `DHAN_CLIENT_ID` | Client ID | ✅ Added |
| `DHAN_PIN` | Account PIN | ✅ Added |
| `DHAN_TOTP_KEY` | 2FA TOTP key | ✅ Added |

### Social Platforms

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook + Instagram API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ |
| `META_APP_SECRET` | Facebook App Secret | ✅ |
| `FACEBOOK_PAGE_ID` | ai360trading Page | ✅ |
| `FACEBOOK_GROUP_ID` | ai360trading Group | ✅ (posting broken) |
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest Kids Page | ✅ |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business numeric ID | ✅ — verify |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth (Hindi) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth (English) | ✅ Added |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth (HerooQuest) | ✅ |

### AI Providers

| Secret | Priority | Free? | Status |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Primary | ✅ Free | ✅ |
| `GEMINI_API_KEY` | Secondary (finance) / Primary (kids) | ✅ Free | ✅ |
| `ANTHROPIC_API_KEY` | Tertiary | ❌ Pay-per-use | ✅ |
| `OPENAI_API_KEY` | Quaternary | ❌ Pay-per-use | ✅ |
| `HF_TOKEN` | Kids only (image gen) | ✅ Free tier | ✅ |

### Google / GCP

| Secret | Purpose |
| --- | --- |
| `GCP_SERVICE_ACCOUNT_JSON` | Indexing API + Google Sheets (gspread) |
| `GH_TOKEN` | GitHub API (secret updates in token_refresh.py) |

### Telegram

| Secret | Purpose |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot authentication |
| `TELEGRAM_CHAT_ID` | Free channel (@ai360trading) |
| `CHAT_ID_ADVANCE` | Advance (₹499/month) |
| `CHAT_ID_PREMIUM` | Premium (bundle) |

### Affiliate Links (Optional — default public URLs used if not set)

| Secret | Default URL |
| --- | --- |
| `AFFILIATE_INSURANCE_IN` | policybazaar.com |
| `AFFILIATE_INSURANCE_US` | policygenius.com |
| `AFFILIATE_INSURANCE_UK` | comparethemarket.com |
| `AFFILIATE_BROKER_IN` | zerodha.com/open-account |
| `AFFILIATE_BROKER_US` | webull.com |
| `AFFILIATE_BROKER_UK` | trading212.com |
| `AFFILIATE_LOANS_IN` | paisabazaar.com |
| `AFFILIATE_LOANS_US` | lendingtree.com |
| `AFFILIATE_LOANS_UK` | moneysupermarket.com |

---

## 16. Human Touch System (Anti-AI-Penalty)

All finance content uses `human_touch.py`. **Never use raw AI output directly.**

| Technique | Method | What It Does |
| --- | --- | --- |
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | "Maine dekha hai..." injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05x range |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns, varies connectors |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded — different set each day |
| SEO tags | `seo.get_video_tags(mode, lang, is_short)` | India + Global combined |
| Banned phrase removal | Internal | "Certainly!", "It's important to note", etc. stripped |

---

## 17. Technical Standards

### The "Full Code" Rule

> AI assistants **must always provide the complete file content** when modifying any file. Partial snippets or diffs are strictly prohibited.

```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the full code for any file you modify.
```

### AI Client Usage Rule — No Exceptions (Main System)

```python
from ai_client import ai, img_client
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang=LANG)
data     = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
```

### Human Touch Usage Rule — No Exceptions

```python
from human_touch import ht, seo
hook  = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
clean = ht.humanize(raw_script, lang=LANG)
tags  = seo.get_video_tags(mode=CONTENT_MODE, lang=LANG)
speed = ht.get_tts_speed()
```

### TTS Speed Pattern

```python
tts_speed = ht.get_tts_speed()
rate_pct  = int((tts_speed - 1.0) * 100)
rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
await edge_tts.Communicate(text, VOICE, rate=rate_str).save(path)
```

### Dependency Pins

| Package | Version | Reason |
| --- | --- | --- |
| `Pillow` | `>=10.3.0` | LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy crashes |
| `moviepy` | `==1.0.3` | Newer versions break audio |
| `yfinance` | Latest | `fast_info['last_price']` ONLY — never `.history()` |
| `PyNaCl` | Latest | GitHub Secret encryption |
| `google-generativeai` | `>=0.8.0` | Gemini fallback — in requirements.txt ✅ |
| `anthropic` | `>=0.40.0` | Claude fallback — in requirements.txt ✅ |
| `openai` | `>=1.50.0` | OpenAI fallback — in requirements.txt ✅ |
| `gspread` | Latest | Google Sheets |
| `oauth2client` | Latest | GCP service account auth |

### Voice Assignments

| Voice | Gender | Used For |
| --- | --- | --- |
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English channel content |
| `en-US-GuyNeural` | Male | English Short 2 alternative |

### Video Formats

| Content | Ratio | Platform |
| --- | --- | --- |
| Analysis + Education | 16:9 | YouTube |
| Shorts, Reels, Morning Reel, ZENO | 9:16 | YouTube Shorts / Reels / Instagram |

---

## 18. Improvement Priority Queue

### 🔴 P1 — Fix Immediately (Breaking Risk)

| # | Task | File | Effort |
| --- | --- | --- | --- |
| 1 | Refactor `generate_articles.py`: replace 2 direct Groq calls with `ai_client.py` | `generate_articles.py` | 2 hours |

### 🟠 P2 — High Impact (Revenue + Global Reach)

| # | Task | File | Effort |
| --- | --- | --- | --- |
| 2 | Add English `localizations` to YouTube upload | `upload_youtube.py` | 2 hours |
| 3 | Add `publishAt` scheduling — 8:30 PM IST default for USA/UK CPM | `upload_youtube.py` | 1 hour |
| 4 | Generate + upload SRT subtitle files from TTS script | generators + `upload_youtube.py` | 3 hours |
| 5 | Verify Instagram auto-upload is live (test run + check logs) | Manual test | 1 hour |
| 6 | Fix Facebook Group posting (`publish_to_groups` token scope) | Meta console | 30 min |

### 🟡 P3 — English Channel Expansion

| # | Task | File |
| --- | --- | --- |
| 7 | `generate_english.py` — Short 4 English | New file |
| 8 | `upload_youtube_english.py` — English channel upload | New file |

### 🔵 P4 — Dhan Live Trading

| # | Item | Status |
| --- | --- | --- |
| 9 | Backtest validation (30–40 paper trades, win rate >35%) | Running |
| 10 | Dhan API connection + order execution | Secrets added |
| 11 | Options CE execution | CE flag already in alerts |
| 12 | Live capital deployment ₹45,000 max | After backtest |

---

## 19. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Timeline | Status |
| --- | --- | --- | --- | --- |
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | Current | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | 3–6 months | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | 6–12 months | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | 12–18 months | Planned |

`img_client` in `ai_client.py` is the Phase 2 upgrade hook — zero generator changes needed.

---

## 20. Full Data Flow

```
Every 5 min (Mon–Fri market hours)
└── main.yml → trading_bot.py v13.4
    └── gspread: AlertLog + History + Nifty200
    └── Market regime + WAITING→TRADED + TSL + exits
    └── T4 memory updated each run

7:00 AM daily
└── daily-morning-reel.yml
    └── generate_reel_morning.py → upload_youtube → upload_facebook → upload_instagram

8:00 AM daily
└── kids-daily.yml
    └── generate_kids_video.py → upload_kids_youtube
    └── upload_facebook.py --meta-prefix kids
    [→ Instagram: manual]

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py → Part 1 YouTube
    └── generate_education.py → Part 2 YouTube (links to Part 1)

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py (⚠️ Groq direct — P1 fix) → _posts/
    └── GitHub Pages auto-deploy
    └── Google Indexing API → instant submission (new) + URL_DELETED (removed)
    └── cleanup_old_posts() capped at MAX_POSTS=120

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 + Short 3 → YouTube
    └── generate_community_post.py → Community Tab

12:00 PM daily
└── generate_community_post.py (inside daily-shorts.yml)

8:30 PM daily
└── daily_reel.yml
    └── generate_reel.py (✅ ai_client) → ZENO reel
    └── upload_youtube → upload_facebook → upload_instagram

Every 50 days
└── token_refresh.yml → META refresh → GitHub Secret → Telegram alert
```

---

## 21. Website

- **URL:** ai360trading.in
- **Hosting:** GitHub Pages — Jekyll, `master` branch `_posts/`
- **Auto-publish:** `daily-articles.yml` commits directly
- **SEO:** Google Indexing API instant submission; JSON-LD schema; long-tail keyword seeds from `content_calendar.py`; live price strip in front matter
- **Revenue:** Google AdSense (USA/UK English = highest CPM) + affiliate links
- **Pillars:** Stock Market · Bitcoin/Crypto · Personal Finance · AI Trading
- **Markets:** India (Nifty50, BankNifty) · USA (S&P500, NASDAQ) · UK (FTSE100) · Brazil (IBOVESPA) · Crypto (BTC, ETH)
- **Post limit:** MAX_POSTS=120 ≈ 30 days history ≈ 1.2 MB — ensures no indexed article is ever deleted

---

## 22. Social Media

| Platform | Handle |
| --- | --- |
| 🌐 Website | ai360trading.in |
| 📣 Telegram Free | @ai360trading |
| 📣 Telegram Advance | ai360trading_Advance — ₹499/month |
| 📣 Telegram Premium | ai360trading_Premium — bundle |
| ▶️ YouTube Trading | @ai360trading |
| ▶️ YouTube Kids | @HerooQuest |
| 📸 Instagram | @ai360trading |
| 👥 Facebook Group | facebook.com/groups/ai360trading |
| 📘 Facebook Page | facebook.com/ai360trading |
| 📘 Facebook Kids | HerooQuest (ID: 1021152881090398) |
| 🐦 Twitter/X | @ai360trading |

---

## 23. How to Test Everything

```bash
# Force content mode
GitHub Actions → workflow → Run workflow → content_mode = market / weekend / holiday

# Kids channel with specific language
GitHub Actions → Kids Channel → Run workflow → lang = both / hi / en

# Verify ai_client fallback in logs
✅ AI generated via groq
⚠️ groq failed → ✅ AI generated via gemini

# Trading bot log pattern
[REGIME] Nifty CMP ₹24527 vs 20DMA ₹23364 → BULLISH
[INFO] Active trades: 2/5
[DONE] 11:55:12 IST | mem=4509 chars

# AppScript verify
Google Sheet → AI360 TRADING menu → MANUAL SYNC → Logger

# Automation switch
Google Sheet → AlertLog → T2 → YES to enable
```

---

*Documentation maintained by AI360Trading automation.*
*Full audit: April 21, 2026 — Claude Sonnet 4.6*

**Change log this update:**
- ✅ `generate_reel.py` confirmed fixed — uses `ai_client.py` (was Groq direct)
- ✅ `requirements.txt` fixed — `google-generativeai`, `anthropic`, `openai` added
- ✅ HerooQuest Kids Channel fully documented (Section 11)
- ✅ Affiliate link system documented (Section 18)
- ✅ Article improvements documented: slug uniqueness, Google de-indexing, MAX_POSTS=120, live price front matter, SEO seeds
- ✅ Free tier limits table added (Section 8)
- ✅ Optimal posting times added (Section 9)
- ⚠️ `generate_articles.py` Groq-direct calls documented as P1 fix — Section 14
- ✅ Platform status table updated with Kids + Facebook Kids

*Update this file whenever architecture, secrets, platform status, or file logic changes.*
