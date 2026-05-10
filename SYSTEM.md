# AI360Trading — Master System Documentation

**Last Updated:** May 11, 2026 — Trading Bot v14.0 + AppScript v15.1 + Kids v2.0
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 In Progress | Phase 4 (Dhan Live) Planned
**Primary Audience:** Indian retail traders + global investors + Kids/Families worldwide

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation Streams

| Stream | Platform | Target Countries |
|---|---|---|
| Video Ad Revenue | YouTube Hindi (AI360Trading) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube English (AI360Trading) | USA, UK, Canada, Australia — 3–5x CPM |
| Video Ad Revenue | YouTube Kids (HerooQuest) | USA, UK, Germany, UAE, India |
| Shorts / Reels Bonus | YouTube, Facebook | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| Facebook Ads | Trading Page + Kids Page | USA, UK, Brazil, India |
| Signal Subscriptions | Telegram Advance + Premium | India, UAE, Global |
| Affiliate Income | Insurance, Broker accounts | India, USA, UK |

### CPM Priority by Channel

**Trading:** USA → UK → Australia → UAE → Canada → Brazil → India
**Kids (HerooQuest):** USA → UK → Germany → UAE → India
**China: EXCLUDED** — closed market, no foreign finance/kids platforms work.

> AI Rule: Optimise titles, hooks, SEO tags, posting times for above countries.
> USA/UK prime time = 11 PM–1 AM IST. All hooks rotate from human_touch.py — never hardcode.

---

## 2. Platform Status

| Platform | Channel | Status | Notes |
|---|---|---|---|
| YouTube Hindi | AI360Trading | ✅ Auto | Analysis + Education + Shorts |
| YouTube English | AI360Trading | 🔄 Phase 3 | Auto-translated channel |
| YouTube Kids | HerooQuest | ✅ Auto | Daily Heroo story, Pixar AI images |
| YouTube Shorts | AI360Trading | ✅ Auto | Short 2 (Madhur) + Short 3 (Neerja) |
| YouTube Community | AI360Trading | ✅ Auto | Daily poll at 7:30 PM IST |
| Facebook Trading | AI360Trading | ✅ Auto | Posts, reels, articles |
| Facebook Kids | HerooQuest | ✅ Auto | Kids video + thumbnail post |
| Facebook Group | AI360Trading | ❌ Broken | Missing `publish_to_groups` scope |
| Instagram | Both | ⚠️ Manual | Download artifact, post from phone |
| GitHub Pages | AI360Trading | ✅ Auto | 4 articles/day + Google indexing |
| Telegram | AI360Trading | ✅ Auto | 3-channel: Basic/Advance/Premium |

---

## 3. Content Mode System

Auto-detected by `indian_holidays.py` → written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE`.

| Mode | When | Strategy |
|---|---|---|
| `market` | Mon–Fri (excl. holidays) | Live Nifty50/Global data, signals |
| `weekend` | Sat–Sun | Educational, wealth-building |
| `holiday` | NSE holidays | Motivational, investment lessons |

---

## 4. Daily Content Schedule

### Trading Channel (AI360Trading)

| Time IST | Content | Platform | Status |
|---|---|---|---|
| 7:00 AM | Morning Reel (9:16, 60s) | YouTube + FB | ✅ |
| 6:00 PM | Main Analysis Video (10-15 min) | YouTube Hindi | ✅ v2.0 |
| 6:00 PM | Education Video (22 slides, 10-12 min) | YouTube Hindi | ✅ |
| 7:00 PM | Short 2 Trade Setup (9:16) | YouTube | ✅ |
| 7:30 PM | Community Poll/Question | YouTube | ✅ |
| 8:30 PM | ZENO Reel (9:16, 60s) | YouTube + FB | ✅ |
| 10:00 AM | 2 Hindi + 2 English SEO Articles | GitHub Pages + FB | ✅ |

### Kids Channel (HerooQuest)

| Time IST | Content | Platform | Status |
|---|---|---|---|
| 4:30 PM weekdays | Heroo Story Video (5-7 min) | YouTube Kids + FB Kids | ✅ v2.0 |
| 10:00 AM weekends | Heroo Story Video (5-7 min) | YouTube Kids + FB Kids | ✅ v2.0 |

> **v2.0 timing fix:** Was 8:00 AM IST (kids at school) → 4:30 PM weekdays (kids home) + 10:00 AM weekends.

**Total: ~10 pieces/day across both channels**

---

## 5. GitHub Actions Workflows

| File | Cron (IST) | Purpose |
|---|---|---|
| `trading_bot.yml` | Every 5 min, 08:15–16:29, Mon–Fri | trading_bot.py signals |
| `daily-videos.yml` | 6:00 PM Mon–Fri | Analysis + Education video |
| `daily-morning-reel.yml` | 7:00 AM daily | Morning reel → YouTube + FB |
| `daily_reel.yml` | 8:30 PM daily | ZENO reel → YouTube + FB |
| `daily-shorts.yml` | 11:30 AM Mon–Fri | Short 2 + Short 3 |
| `daily-articles.yml` | 10:00 AM Mon–Fri | 4 articles → GitHub Pages |
| `kids-daily.yml` | 4:30 PM weekdays / 10:00 AM weekends | Heroo story → YouTube Kids + FB |
| `token_refresh.yml` | 1st + 20th of month | Auto META token refresh |
| `keepalive.yml` | Periodic | Prevents workflow disabling |

### GitHub Secrets (complete)

| Secret | Used By | Purpose |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | trading_bot.py + AppScript | Bot token |
| `CHAT_ID_BASIC` | trading_bot.py | Free channel |
| `CHAT_ID_ADVANCE` | trading_bot.py | ₹1000/mo channel |
| `CHAT_ID_PREMIUM` | trading_bot.py | ₹3000/mo channel |
| `GCP_SERVICE_ACCOUNT_JSON` | trading_bot.py | Google Sheets |
| `GROQ_API_KEY` | ai_client.py | Primary AI (free) |
| `GEMINI_API_KEY` | ai_client.py + kids | Secondary AI + image gen |
| `ANTHROPIC_API_KEY` | ai_client.py | Tertiary AI |
| `OPENAI_API_KEY` | ai_client.py + DALL-E | Quaternary AI + images |
| `HF_TOKEN` | generate_kids_video.py | HuggingFace FLUX.1 images |
| `STABILITY_API_KEY` | generate_kids_video.py | Stability AI images (Layer 4b) |
| `YOUTUBE_CREDENTIALS` | trading uploads | Hindi channel |
| `YOUTUBE_CREDENTIALS_KIDS` | upload_kids_youtube.py | HerooQuest channel |
| `META_ACCESS_TOKEN` | upload_facebook.py | Trading FB page |
| `META_ACCESS_TOKEN_KIDS` | upload_facebook.py | Kids FB page |
| `FACEBOOK_PAGE_ID` | upload_facebook.py | Trading page ID |
| `FACEBOOK_KIDS_PAGE_ID` | upload_facebook.py | Kids page ID (1021152881090398) |
| `FACEBOOK_GROUP_ID` | upload_facebook.py | Group (broken — missing scope) |
| `DHAN_API_KEY/SECRET/CLIENT_ID/PIN/TOTP_KEY` | Phase 4 | Live trading (not active) |
| `PLAYLIST_NIFTY_ANALYSIS` | upload | YouTube playlists |
| `PLAYLIST_SWING_TRADE` | upload | YouTube playlists |
| `PLAYLIST_WEEKLY_OUTLOOK` | upload | YouTube playlists |
| `PLAYLIST_ZENO_WISDOM` | upload | YouTube playlists |
| `GH_TOKEN` | workflows | GitHub API |
| `AFFILIATE_INSURANCE_IN/UK/US` | articles | Affiliate links |
| `STABILITY_API_KEY` | generate_kids_video.py | Image gen Layer 4b |
| `CRICAPI_KEY` | content | Cricket API |
| `HF_TOKEN` | kids | HuggingFace |

> ⚠️ AppScript uses Script Properties (not GitHub secrets).
> Keys: `TELEGRAM_BOT_TOKEN`, `CHAT_ID_BASIC`, `CHAT_ID_ADVANCE`, `CHAT_ID_PREMIUM`

---

## 6. Complete File Map

### Core Infrastructure

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI: Groq→Gemini→Claude→OpenAI→Templates | ✅ |
| `human_touch.py` | Hooks, SEO tags, thumbnail text, description templates, kids support | ✅ v2.0 |
| `token_refresh.py` | Auto META token + GitHub Secret update | ✅ |
| `indian_holidays.py` | Mode detection: NSE API + fallback | ✅ |
| `content_calendar.py` | Trading topics: Options/TA/Fundamentals/Strategy/Psychology by day | ✅ |
| `kids_content_calendar.py` | Kids topics: 8 categories, CPM-weighted, day-of-year rotation | ✅ |

### Trading Content Generation

| File | Role | Status |
|---|---|---|
| `trading_bot.py` | Signal monitor + TSL + 3-channel Telegram | ✅ v14.0 |
| `generate_analysis.py` | 10-15 min combined analysis video, stock-name title, mid-roll | ✅ v2.0 |
| `generate_education.py` | 22-slide education video 10-12 min | ✅ |
| `generate_shorts.py` | Short 2 (Madhur/trade) + Short 3 (Neerja/market pulse) | ✅ |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ✅ |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | ✅ |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | ✅ |
| `generate_community_post.py` | YouTube community poll (7:30 PM) | ✅ |

### Kids Content Generation

| File | Role | Status |
|---|---|---|
| `generate_kids_video.py` | Heroo story: AI images + TTS + Ken Burns zoom + FFmpeg | ✅ v2.0 |
| `upload_kids_youtube.py` | Upload to HerooQuest + thumbnail + short | ✅ v2.0 |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Trading channel uploads | ✅ |
| `upload_facebook.py` | FB Page (trading + kids with --meta-prefix) | ✅ |
| `upload_instagram.py` | ⚠️ API removed — manual from phone | ❌ |

---

## 7. AI Fallback Chain

### Text Generation (all channels)
```
Groq — llama-3.3-70b-versatile     (primary — free, fastest)
    ↓
Google Gemini — gemini-2.0-flash   (secondary — 1,500/day free)
    ↓
Anthropic Claude — claude-haiku-4-5 (tertiary)
    ↓
OpenAI — gpt-4o-mini               (quaternary)
    ↓
Templates in human_touch.py        (always works)
```

### Image Generation (Kids channel only)
```
Layer 1:  Gemini 2.5 Flash Image    (500 free/day — best)
Layer 2:  Gemini 2.0 Flash Exp      (free backup)
Layer 3:  HuggingFace FLUX.1-schnell (free — HF_TOKEN)
Layer 4:  DALL-E 3 via OpenAI       (paid — OPENAI_API_KEY)
Layer 4b: Stability AI Core         (paid — STABILITY_API_KEY) ← wired v2.0
Layer 5:  Heroo placeholder         (always works — never fails)
```
All image layers use `requests` only — no extra packages needed.

---

## 8. Trading Bot Architecture

### Google Sheets

| Sheet | Purpose |
|---|---|
| `Nifty200` | ~211 stocks, 35 cols A–AI. All Sector_Rank uses `$500` range. |
| `AlertLog` | 21 rows, 19 cols. T2=YES switch. T4=Python-only state string. |
| `History` | Closed trades — 18 cols A–R |
| `BotMemory` | Key-value: _CAP/_MODE/_SEC/_RANK. AppScript writes, Python reads. |

> PriceCache and TempPriceCalc deleted in freshCleanStart — never recreate.

### Nifty200 Column Map (0-based)
```
r[0]  NSE_SYMBOL      r[1]  SECTOR         r[2]  CMP
r[3]  %Change         r[4]  20_DMA         r[5]  50_DMA
r[6]  200_DMA         r[7]  SMA_Structure  r[8]  52W_Low
r[9]  52W_High        r[10] %up_52W_Low    r[11] %down_52W_High
r[12] %dist_20DMA     r[13] Avg_Volume_20D r[14] Volume_vs_Avg%
r[15] FII_Buy_Zone    r[16] FII_Rating     r[17] Leader_Type
r[18] Signal_Score    r[19] FINAL_ACTION   r[20] RS
r[21] Sector_Trend    r[22] Breakout_Stage r[23] Retest%
r[24] Trade_Type      r[25] Priority_Score r[26] Pivot_Resistance
r[27] VCP_Status      r[28] ATR14          r[29] Days_Since_Low
r[30] 52W_Breakout_Score r[31] Sector_Rotation_Score (AF)
r[32] FII_Buying_Signal  r[33] Master_Score r[34] Sector_Rank
```

### Formula Fixes (all applied May 2026)

| Column | Fix |
|---|---|
| E/F/G (DMAs) | Buffer -35/-80/-320 days (was -30/-70/-300) |
| N (Avg_Vol) | `INDEX(...,0,2)` — extracts volume only, no date contamination |
| P (FII_Buy_Zone) | Overheated checked before Mild Correction |
| AC (ATR14) | `ARRAYFORMULA(INDEX(high,2,2,14)-INDEX(low,2,2,14))` 21 cal days |
| AI (Sector_Rank) | `RANK(AF3,FILTER(AF$3:AF$500,...),0)` — $500 range, no row limit |

### AppScript v15.1 Configuration

```javascript
MAX_TRADES: 8,  MAX_WAITING: 10,  MAX_MOM_SLOTS: 3,  LOG_ROWS: 21
MIN_PRIORITY: 15,  MIN_RR: 1.8
MAX_CMP: 8000,  ATH_BUFFER_PCT: 1.0
BASE_STAGE_MIN_VOL: 40,  LATE_ENTRY_MIN_RS: 5
RESULT_DAY_SKIP_PCT: 6.0,  CORP_ACTION_SKIP_PCT: 15.0
MORNING_VOL_BYPASS_UNTIL: "10:30"
```

### 10 Scan Gates

| Gate | Condition | Fix |
|---|---|---|
| 1 | FII SELLING → skip | — |
| 2 | Market regime | — |
| 3 | Late entry RS≥5 | Relaxed from 7 |
| 4 | CMP>0, ATR>0, CMP≤₹8000 | MAX_CMP raised |
| 4b | Skip if \|%Change\|>6% (result) or >15% (corp action) | NEW |
| 5 | Extension filter | — |
| 6 | Pivot resistance — EXEMPT breakout stages | FIXED |
| 7 | Volume — BYPASS before 10:30 AM, breakout always exempt | FIXED |
| 8 | ATH buffer 1% — EXEMPT breakout stages | FIXED |
| 9 | AVOID/NO TRADE → skip | — |
| 10 | Max 2 per sector | — |

**Gate 7 critical detail:** `isMorning` computed OUTSIDE `volVsAvg>0` check. Before fix, isMorning never ran because `volVsAvg>0` was always false in morning (partial-day volume = negative). After fix: entire gate skipped before 10:30 AM.

**Gates 6+8 critical detail:** BREAKOUT CONFIRMED/ALERT stages exempt from pivot resistance and ATH buffer. Unlocked BHEL, CGPOWER, FEDERALBNK, NTPC, JSWENERGY which were all wrongly blocked.

### Python Bot v14.0

**Critical fixes:**

| Fix | Problem | Solution |
|---|---|---|
| Channel swap | CHAT_ADVANCE read CHAT_ID_PREMIUM env | Correct env var names |
| Differentiation | Same message Advance + Premium | Advance=details, Premium=+CE flag |
| BotMemory | Read _CAP/_MODE from T4 string | Read from BotMemory SHEET |
| MAX_TRADES | Bot stopped at 5, AppScript allowed 8 | Both now 8 |
| Result day | Entered SBIN on earnings day | Skip if \|%Change\|>6% |
| Holiday | Relied on cron only | NSE_HOLIDAYS_2026 set in Python |
| BOT_MODE | Not implemented | test_telegram/daily_summary/weekly_summary |

**Env vars (exact names matter):**
```
TELEGRAM_BOT_TOKEN  ← not TELEGRAM_TOKEN
CHAT_ID_BASIC       ← not TELEGRAM_CHAT_ID
CHAT_ID_ADVANCE, CHAT_ID_PREMIUM, GCP_SERVICE_ACCOUNT_JSON
```

**3-channel content:**

| Channel | Good Morning | Entry Alert | Exit | CE Flag |
|---|---|---|---|---|
| Basic | Mood + count only | ❌ | WIN/LOSS% | ❌ |
| Advance | Full P/L + SL/Target | Full details | Full details | ❌ |
| Premium | Same as Advance | Same + CE hint | Same | ✅ rank≤5 |

**TSL params:**
```python
TSL_PARAMS = {
    "VCP": {"breakeven":3.0,"lock1":5.0,"trail":8.0, "atr_mult":2.0,"gap_lock":9.0},
    "MOM": {"breakeven":2.5,"lock1":4.5,"trail":7.0, "atr_mult":1.8,"gap_lock":8.0},
    "STD": {"breakeven":2.0,"lock1":4.0,"trail":10.0,"atr_mult":2.5,"gap_lock":8.0},
}
```

**Daily message schedule:**
- 08:45–09:29 → Good Morning (all 3 channels)
- 09:15–15:30 → Entry/exit/TSL alerts (Advance + Premium)
- 12:28–12:38 → Mid-day pulse (Advance + Premium)
- 15:15–15:45 → Market close summary (all 3 channels)

**Phase 4 readiness:** Need 30+ closed trades in History before enabling Dhan API.
**Current:** 1 trade (SBIN -7.30% loss, May 8, 2026 — result day entry, now prevented by v15.0 filter).

---

## 9. Kids Channel — HerooQuest

### Characters (brand-locked)

**Heroo** — brave 10-year-old Indian boy, spiky jet-black hair, warm brown skin, big brown eyes, red-blue superhero suit with golden H emblem, golden cape. Always main character centered in every frame.

**Arya** — cheerful 8-year-old Indian girl, dark hair in two braids with golden star clips, bright orange kurta. Heroo's curious friend.

**Visual style:** 3D CGI, Pixar/Disney quality, volumetric lighting, ray-traced shadows, vibrant colors, child-friendly atmosphere.

### Episode Structure

```
6 scenes × 18s narration = ~2 min audio
+ Ken Burns zoom (FFmpeg) = 5-7 min video
+ 9:16 crop → YouTube Short (60s)
+ 9:16 crop → Instagram Reel (90s, manual)
```

### Image Fallback Chain (generate_kids_video.py)

```
Layer 1:  Gemini 2.5 Flash Image (500 free/day)
Layer 2:  Gemini 2.0 Flash Exp  (free)
Layer 3:  HuggingFace FLUX.1    (free, HF_TOKEN)
Layer 4:  DALL-E 3              (paid, OPENAI_API_KEY)
Layer 4b: Stability AI Core     (paid, STABILITY_API_KEY) ← v2.0
Layer 5:  Heroo placeholder     (always works)
```

### Meta JSON (generate → upload)

```json
{
  "title_hi": "...", "title_en": "...",
  "description_en": "60-word SEO description",
  "moral_hi": "...", "moral_en": "...",
  "seo_tags": ["kids","HerooQuest","animation","Pixar",...],
  "video_path": "output/kids_video_YYYY-MM-DD.mp4",
  "short_path": "output/kids_short_YYYY-MM-DD.mp4",
  "reel_path":  "output/kids_reel_YYYY-MM-DD.mp4"
}
```

### Upload (upload_kids_youtube.py v2.0)

- `selfDeclaredMadeForKids: True` + `madeForKids: True` ✅ (YouTube Kids discovery)
- `categoryId: "27"` Education ✅
- Custom thumbnail from `kids_scene_01.png` ← **new v2.0** (was dark first frame)
- Short uploaded with same thumbnail ← **new v2.0**

### Content Calendar (kids_content_calendar.py)

8 categories rotating by day-of-year (no weekly repetition):
```
historical → science → moral_stories → religious →
emotional → biographies → fairy_tales → geography
```
Each category CPM-weighted for target countries. China excluded from all targets.

---

## 10. Content Strategy v2.0

### Title Formula

**Trading (stock-name FIRST — people search stock names):**
```
CGPOWER 🚀 BREAKOUT — ₹1000 Target? | Nifty50 11 May 2026 | AI360 Trading
```
Never: "Aaj Ka Market Analysis" — generic, nobody searches this.

**Kids:**
```
Heroo aur Apollo Mission 🚀 | Bacchon Ki Kahani | 11 May 2026
```

### Description Structure

```
Line 1-2: Hook + main insight (shown before "Show More" — most important)
━━━━━━━━━
Timestamps (0:00, 1:30, 3:00, 6:00, 9:00, 11:00)
━━━━━━━━━
Stock names covered
Part 1 link (for education video)
Telegram link
Website link
━━━━━━━━━
Hashtags (12 Hindi + 12 English)
```

### Upload Times (v2.0 corrected)

| Content | Old | New | Reason |
|---|---|---|---|
| Main video | 7:30 AM | 6:00 PM | India peak viewing 6-10 PM |
| Kids story | 8:00 AM | 4:30 PM wkday / 10 AM wkend | Kids home from school |
| Morning reel | 7:00 AM | 7:00 AM | ✅ Correct |
| ZENO reel | 8:30 PM | 8:30 PM | ✅ Correct |
| Community post | 12:00 PM | 7:30 PM | Peak engagement post-market |

### SEO Tags Strategy

**Trading:** Stock names first + Hinglish mix (12 Hindi + 12 English per video)
```
["CGPOWER share price", "शेयर बाजार आज", "nifty50 aaj ka analysis",
 "swing trade setup hindi", "best stocks to buy today india", ...]
```

**Kids:** Bilingual — Hindi audience + English NRI/global
```
["hindi kahani", "bacchon ki kahani", "HerooQuest", "Heroo",
 "kids stories in english", "bedtime stories", "moral stories children", ...]
```

### Video Length for Mid-Roll Ads

YouTube places mid-roll ads at 8+ minutes. Both main video (10-15 min) and education video (22 slides, 10-12 min) are above threshold. Kids video (5-7 min) is below — intentional for kids attention span.

---

## 11. Emergency Procedures (For Family)

> If Telegram messages stop:
1. Google Sheet → check T2 = YES
2. Run 📡 TEST TELEGRAM from sheet menu → if no message → check Script Properties
3. GitHub → Actions → look for red ❌ → click to see error
4. "Quota exceeded" → wait 1 hour
5. "Token expired" → run token_refresh.yml
6. Bot sends own crash alerts to Advance channel automatically

> If Kids videos stop:
1. GitHub → Actions → kids-daily.yml → Run workflow → check log
2. Look for `[IMG-1]` through `[LAYER-5]` — which image layer fired?
3. Check Gemini quota at aistudio.google.com
4. Artifacts saved in GitHub Actions — download + upload to YouTube manually

**To check system alive anytime:** 📡 TEST TELEGRAM from Google Sheet. Works 24/7.

---

## 12. Known Issues & Planned

| Issue | Status | Action |
|---|---|---|
| Facebook Group `publish_to_groups` | ❌ Open | Re-authorize Meta App with group scope |
| Instagram API | ❌ Removed | Manual upload from phone — artifact saved |
| YouTube English channel | 🔄 Phase 3 | Same content translated — 3-5x CPM |
| Dhan API live trading | 📋 Phase 4 | Need 30+ paper trades in History |
| NSE Corporate Actions API | 📋 Planned | Auto-detect result days |
| kids_content_calendar.py China tags | ⚠️ Minor | Remove China from geography targets |

---

## 13. Phase Roadmap

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Complete | Core infra — AI client, content gen, all platforms |
| Phase 2 | ✅ Complete | Trading + Kids channels fully automated |
| Phase 3 | 🔄 In Progress | English channel + FB Group fix + Instagram |
| Phase 4 | 📋 Planned | Dhan/Zerodha live API (30+ paper trades first) |
| Phase 5 | 💭 Future | Options auto-execution when CE flag triggers |

---

*AI360 Trading + HerooQuest Kids — Built to run forever. Zero maintenance. Pure automation.*
*Last updated by Claude Sonnet 4.6 — May 11, 2026*
