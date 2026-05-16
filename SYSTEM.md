# AI360Trading — Master System Documentation

**Last Updated:** May 16, 2026 — AppScript v15.5 | Bot v15.0 (Drive, not yet GitHub) | HerooQuest 3 videos live | heroo.png fixed | human_touch v2.2 | ai_client v2.2
**Repo:** https://github.com/systronics/ai360trading
**Website:** https://ai360trading.in
**Owner:** Amit Kumar, Haridwar, Uttarakhand, India

---

## ⚠️ EVERY AI MUST READ THIS SECTION COMPLETELY BEFORE TOUCHING ANYTHING

This system is the **sole livelihood** of Amit Kumar's family. Amit has serious health issues and is in debt. His family is non-technical and cannot fix anything if it breaks. The system must run **forever, fully automatically, with zero human intervention.** This is not a hobby project — it is a family survival project.

### The 10 Absolute Rules — No Exceptions

| # | Rule | Why |
|---|------|-----|
| 1 | **NEVER break working code** | A broken workflow = zero income that day |
| 2 | **Always provide COMPLETE file replacements** | No partial snippets, no diffs, no "add this here" |
| 3 | **Cost must stay ₹0/month forever** | Verify free tier limits before adding any new service |
| 4 | **Never call AI APIs directly** | Always use `ai_client.py` — never Groq/Gemini/Claude/OpenAI directly |
| 5 | **Never use raw AI output** | Always pass through `human_touch.py` — YouTube penalises AI content |
| 6 | **Never execute real trades** | System is paper trading until Phase 4 is explicitly authorised |
| 7 | **Update SYSTEM.md after every change** | This file is the only memory across AI sessions |
| 8 | **Hook in first 5 seconds of every video** | Watch time is dropping — this is the #1 priority fix |
| 9 | **Thumbnails must have large bold text + emotion** | CTR is the #1 factor for YouTube growth |
| 10 | **When in doubt, do nothing new — fix what is broken** | Stability > features |

### How to Use This Document

1. Read Sections 1–3 first (Mission, Status, Priority Fixes)
2. Read the section relevant to your task
3. Check Section 13 for known bugs before starting
4. After your task, update Section 13 and this header's Last Updated date

---

## 1. Mission & Monetisation

> Build a fully automated passive income system that runs forever on ₹0/month infrastructure, generating income across every possible digital monetisation stream simultaneously. This is Amit's family's survival — it must work.

### Income Streams (All Active or Building)

| Stream | Platform | Target Countries | CPM Priority |
|--------|----------|-----------------|--------------|
| Video ad revenue | YouTube Hindi | USA, UK, Canada, Australia, UAE | High |
| Video ad revenue | YouTube English (Phase 3) | USA, UK, Canada, Australia | Highest (3–5× Hindi) |
| Shorts/Reels bonus | YouTube + Facebook | USA, UK, Brazil, India | Medium |
| Website ad revenue | ai360trading.in (GitHub Pages) | USA, UK, Canada | High |
| In-stream video ads | Facebook Page | USA, UK, Brazil, India | Medium |
| Paid signal subscriptions | Telegram (3 tiers) | India, UAE, Global | Recurring |
| Affiliate commissions | Insurance links in articles | India, UK, USA | Per-conversion |

### CPM Target Countries (priority order)
1. USA — Highest CPM globally for finance content
2. UK — Very high CPM, strong trading audience
3. Australia — High CPM, growing retail base
4. UAE — High CPM, large NRI + Gulf investor audience
5. Canada — High CPM, similar to USA
6. Brazil — Large audience, fast-growing finance CPM
7. India — Largest volume, Nifty/stock focus

> **AI Rule:** USA/UK prime time = 11 PM–1 AM IST. Always include global keywords in titles, descriptions, and tags.

---

## 2. Current Phase Status

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| Phase 1 | Infrastructure | ✅ Complete | GitHub Actions, Jekyll, ai_client, human_touch, META token refresh |
| Phase 2 | Content Upgrade | ✅ Complete | All generators upgraded; trading bot v15.0 |
| Phase 3 | English Channel + Global Scale | 🔄 Building | Education course live, HerooQuest 3 videos/day live |
| Phase 4 | Live Trading + Premium Options | 📋 Planned | Dhan API, 30+ paper trades first |

---

## 3. Priority Fix Order

### ✅ FIXED (May 2026)

| Item | Fixed | Notes |
|------|-------|-------|
| Telegram CHAT_ID swap (Advance/Premium reversed) | ✅ v14.0 | Fixed in trading_bot.py |
| AppScript Gate 5 blocking all stocks | ✅ v15.2 | RETEST_MAX_PULLBACK -0.03 → -0.08 |
| AppScript RR check failing all leaders | ✅ v15.2 | ATR_TGT_SWING_LEADER 3.5 → 4.0 |
| India VIX not fetching | ✅ v15.3 | Live Yahoo Finance fetch in AppScript |
| Options signal system | ✅ v15.3 | Premium only, VIX+expiry+strike |
| Base entry system | ✅ v15.4 | Gate 11, non-F&O equity, F&O BASE CE |
| AppScript T4 BotMemory spill (col T rows 3+) | ✅ v15.5 | _cleanSystemControlColumn() added |
| generate_analysis.py SEOTags TypeError | ✅ | Fixed build_video_meta() — returns 5 values |
| YouTube tags 480 char limit | ✅ | ASCII filter in generate_shorts.py v3.0 |
| Facebook page token #200 error | ✅ | get_page_token() in upload_facebook.py |
| generate_shorts.py Facebook fix | ✅ v3.0 | get_fb_page_token() added (Hindi only) |
| head.html Schema + dateModified | ✅ | Deployed |
| robots.txt pagination rule | ✅ | Deployed |
| HerooQuest Kids Facebook upload | ✅ | META_ACCESS_TOKEN_KIDS page token |
| generate_education.py replaces generate_analysis.py | ✅ May 15 | 52-week course, dual language |
| generate_shorts.py v3.0 | ✅ May 15 | AlertLog connected, ZENO auto, dual lang, FB fix |
| generate_kids_video.py v2.0 | ✅ May 15 | 3 outputs, heroo.png, dual lang |
| daily-videos.yml | ✅ May 15 | Runs education (not analysis), Hindi + English |
| daily-shorts.yml | ✅ May 15 | Dual language, AlertLog mode |
| kids-daily.yml | ✅ May 15 | Hindi + English split jobs, 3 output types |
| heroo.png double extension (heroo.png.png) | ✅ May 16 | Corrected to heroo.png — tomorrow's run will load correctly |
| human_touch.py v2.1 | ✅ May 15 | get_video_tags channel param + get_youtube_safe_tags + format_article_tags |
| human_touch.py v2.2 | ✅ May 16 | Education hooks, get_video_description(), safe_thumbnail_text(), safe_tts_price(), get_prompt_rules() |
| ai_client.py v2.2 | ✅ May 16 | Education system prompt, generate_with_stock_data(), Stability AI background |
| HerooQuest YouTube custom thumbnails | ✅ May 15 | Phone verified at studio.youtube.com |
| upload_instagram.py | ✅ May 15 | Deleted from GitHub |
| HerooQuest 3 videos live | ✅ May 16 | Full story + Cliffhanger + Did You Know all uploading daily |
| ZENO wrong emotion (crying on BREAKOUT) | ✅ May 16 | generate_shorts.py v3.1 — stage priority over pct |
| "पा" Hindi artifact in thumbnail | ✅ May 16 | safe_thumbnail_text() in human_touch.py v2.2 |
| Wrong SL in AI script (1457 → 145.7) | ✅ May 16 | get_prompt_rules() locks numbers + generate_with_stock_data() |
| Education video wrong hooks (chart/trading language) | ✅ May 16 | HOOKS_HINDI_EDUCATION in human_touch.py v2.2 |
| RSI + time + day + Nifty entry filters | ✅ May 16 | trading_bot.py v15.0 — saved to Drive |
| Re-entry cooldown after TARGET HIT | ✅ May 16 | trading_bot.py v15.0 — 5 trading days, RECD key in T4 |

### 🔴 CRITICAL — Push to GitHub Now

| # | Issue | File | Impact |
|---|-------|------|--------|
| 1 | trading_bot.py v15.0 not on GitHub | trading_bot.py | v13.5 running on server — missing all new filters |
| 2 | human_touch.py v2.2 not on GitHub | human_touch.py | Education hooks, safe_thumbnail_text missing |
| 3 | ai_client.py v2.2 not on GitHub | ai_client.py | Education system prompt missing |
| 4 | generate_shorts.py v3.1 not on GitHub | generate_shorts.py | ZENO wrong emotion still in old version |

### 🟡 IMPORTANT — This Week

| # | Issue | File | Impact |
|---|-------|------|--------|
| 5 | Facebook Group posting broken (token scope) | upload_facebook.py | Missing group distribution |
| 6 | English YouTube channel credentials | YOUTUBE_CREDENTIALS_EN secret | English shorts/education upload skipped |

### 🟢 MEDIUM TERM — Next Month

| # | Issue | File | Impact |
|---|-------|------|--------|
| 7 | HerooQuest thumbnails CTR 0.6% — too dark | Kids generator | Very low CTR — upgrade thumbnail style |
| 8 | Add ZENO to morning reel thumbnail | generate_reel_morning.py | No ZENO = low CTR |
| 9 | Test v15.4 base entry (needs bullish market) | AppScript | Market currently bearish |

---

## 4. Platform Status

| Platform | Status | Notes |
|----------|--------|-------|
| YouTube Hindi | ✅ Auto | Education + Shorts + Reels |
| YouTube Shorts (Hindi) | ✅ Auto | AlertLog top stock, ZENO auto-emotion |
| YouTube Shorts (English) | 🔄 Phase 3 | Code ready — needs YOUTUBE_CREDENTIALS_EN |
| YouTube English (long) | 🔄 Phase 3 | Code ready — needs YOUTUBE_CREDENTIALS_EN |
| YouTube Kids Hindi (HerooQuest) | ✅ Auto | 3 videos/day: Full + Cliffhanger + Did You Know |
| YouTube Kids English (HerooQuest) | 🔄 Phase 3 | Code ready — needs YOUTUBE_CREDENTIALS_KIDS_EN |
| YouTube Reels (ZENO 8:30 PM) | ✅ Auto | Working |
| YouTube Morning Reel (7 AM) | ✅ Auto | Working |
| Facebook Page (AI360Trading) | ✅ Auto | Shorts + reels + articles — page token fixed |
| Facebook Page (HerooQuest Kids) | ✅ Auto | Fixed May 2026 |
| Facebook Group (ai360trading) | ❌ Broken | Token missing publish_to_groups scope |
| Instagram | ❌ Removed | Post manually from reel artifact |
| GitHub Pages (ai360trading.in) | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram (3 channels) | ✅ Auto | Paper trading signals — 3 wins, 100% win rate |

---

## 5. Content Output Schedule (Daily, Fully Automated)

| # | Content | Generator | Time (IST) | Platform | Status |
|---|---------|-----------|-----------|----------|--------|
| 1 | Morning Reel (9:16) | generate_reel_morning.py | 7:00 AM | YouTube + Facebook | ✅ |
| 2 | Education Video Hindi (16:9, ~9 min) | generate_education.py | 7:30 AM weekday / 9:30 AM weekend | YouTube Hindi | ✅ |
| 3 | Education Video English (16:9) | generate_education.py | 7:30 AM | YouTube English | 🔄 Phase 3 |
| 4 | Stock Short Hindi (9:16, 45-60s) | generate_shorts.py | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts + Facebook | ✅ |
| 5 | Stock Short English (9:16) | generate_shorts.py | 11:30 AM | YouTube English Shorts | 🔄 Phase 3 |
| 6 | 4 SEO Articles | generate_articles.py | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 7 | ZENO Reel (9:16) | generate_reel.py | 8:30 PM | YouTube + Facebook | ✅ |
| 8 | HerooQuest Full Story Hindi | generate_kids_video.py | 8:00 AM | YouTube Kids | ✅ |
| 9 | HerooQuest Cliffhanger Short Hindi | generate_kids_video.py | 8:00 AM | YouTube Kids | ✅ |
| 10 | HerooQuest Did You Know Short Hindi | generate_kids_video.py | 8:00 AM | YouTube Kids | ✅ |
| 11 | HerooQuest Full Story English | generate_kids_video.py | 8:00 AM | YouTube Kids EN | 🔄 Phase 3 |
| 12 | Instagram | Manual | — | Instagram | ❌ Manual |

**Total: 10 pieces/day automated (Hindi) + 2 English Phase 3 pending**

---

## 6. Content Mode System

| Mode | When | Content Strategy |
|------|------|-----------------|
| `market` | Mon–Fri (excluding Indian holidays) | Top AlertLog stock short, weekly education topic |
| `weekend` | Saturday–Sunday | Base/Near Breakout from Nifty200, same education topic |
| `holiday` | Indian Market Holidays | Motivational investing lesson |

---

## 7. GitHub Actions Workflows

| File | Trigger (IST) | Purpose |
|------|--------------|---------|
| `trading_bot.yml` | Every 5 min (08:15–16:29 Mon–Fri) | Signal monitor + TSL + Telegram alerts |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Education video Hindi + English |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Stock short Hindi + English |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning reel + ZENO reel |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages |
| `kids-daily.yml` | 8:00 AM daily | HerooQuest: 3 outputs × 2 languages |
| `token_refresh.yml` | 1st + 20th of month | Auto META token refresh |
| `keepalive.yml` | Periodic | Prevents GitHub disabling workflows |

**All yml files confirmed correct. No changes needed.**

---

## 8. Complete File Map

### Core Infrastructure

| File | Role | Version | Status |
|------|------|---------|--------|
| `ai_client.py` | Universal AI fallback chain + education persona + Stability AI | v2.2 | ⚠️ Not pushed |
| `human_touch.py` | Anti-AI-penalty layer — hooks, TTS, SEO, permanent fixes | v2.2 | ⚠️ Not pushed |
| `indian_holidays.py` | Mode detection | — | ✅ |
| `content_calendar.py` | Topic rotation | — | ✅ |
| `token_refresh.py` | Auto META token refresh | — | ✅ |

### Content Generators

| File | Role | Version | Status |
|------|------|---------|--------|
| `trading_bot.py` | Signal monitor + TSL + all filters | v15.0 | ⚠️ Drive only, GitHub has v13.5 |
| `generate_education.py` | 52-week course, dual language | v1.0 | ✅ |
| `generate_shorts.py` | AlertLog top stock, ZENO auto, dual lang, FB share | v3.1 | ⚠️ Not pushed |
| `generate_kids_video.py` | 3 output types, heroo.png, dual lang | v2.0 | ✅ |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | v2 | ✅ |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | v2 | ✅ |
| `generate_articles.py` | 4 SEO articles daily | v2.1 | ✅ |
| `generate_analysis.py` | RETIRED | — | ❌ Do not use |

### Upload & Distribution

| File | Role | Status |
|------|------|--------|
| `upload_youtube.py` | Standard YouTube upload | ✅ |
| `upload_kids_youtube.py` | HerooQuest YouTube + thumbnail | ✅ v2.1 |
| `upload_facebook.py` | FB Page upload — page token fixed | ✅ v2.1 |
| `upload_instagram.py` | **DELETED May 15** | ❌ Gone |

### Static Assets

| Path | Contents | Status |
|------|----------|--------|
| `public/image/heroo.png` | HerooQuest character — Pixar 3D boy, white cap, rainbow hoodie | ✅ Fixed May 16 |
| `public/image/zeno_*.png` | 7 ZENO emotions | ✅ |

### ZENO Emotions (7 available)

| File | Emotion | Stage Priority (v3.1 fix) |
|------|---------|--------------------------|
| zeno_happy.png | Happy | BREAKOUT ALERT (always, regardless of pct) |
| zeno_greed.png | Greed | BREAKOUT CONFIRMED (always) |
| zeno_thinking.png | Thinking | Near Breakout, Base, weekend |
| zeno_sad.png | Sad | Bearish, -3% |
| zeno_fear.png | Fear | Crash, -5%, high VIX |
| zeno_angry.png | Angry | FOMO warning |
| zeno_celebrating.png | Celebrating | Target hit |

---

## 9. AI Fallback Chain

**Never call AI APIs directly. Always use `ai_client.py`.**

```
Groq — llama-3.3-70b-versatile     (Primary — fastest, free)
    ↓ fails
Gemini — gemini-2.0-flash           (Secondary)
    ↓ fails
Claude — claude-haiku-4-5-20251001  (Tertiary)
    ↓ fails
OpenAI — gpt-4o-mini                (Quaternary)
    ↓ all fail
Templates in human_touch.py         (Always works)
```

### v2.2 Key Methods

```python
ai.generate(prompt, content_mode="market", lang="hi")
ai.generate_json(prompt, content_mode="education", lang="hi")
ai.generate_with_stock_data(prompt, lang="hi", sym="NESTLE", cmp=1446, sl=1380, target=1550)
# ↑ v2.2 NEW: locks stock numbers — prevents AI changing SL/Target

# System prompts (auto-selected by content_mode):
# "market"    → trader persona (Hindi/English)
# "education" → teacher persona — no chart/breakout/setup language
#               Fixes: education video starting with "chart kabhie jhooth nahi bolta"
```

---

## 10. Thumbnail & Hook Rules

### AI360Trading Shorts (v3.1)
- ZENO emotion: stage takes priority over pct_change — BREAKOUT always happy/greed
- Thumbnail text: safe_thumbnail_text() strips Devanagari only (keeps ₹ and numbers)
- No "पा" artifact — Hindi chars stripped before PIL renders
- Line1/Line2: English only | full_script: Hindi OK (TTS audio)

### HerooQuest Kids (v2.0)
- heroo.png fills first frame (80% height) — YouTube auto-thumbnail = face
- Custom thumbnails enabled (phone verified May 15)
- heroo.png.png → heroo.png fixed May 16 — active from May 17

### Education Videos (v1.0)
- Hook: get_hook(mode="education") → education-specific hooks (not trading language)
- Title: "Topic Name | Week N | AI360 Trading" — no random percentages

---

## 11. Permanent Fixes in human_touch.py v2.2

These fix Hindi/TTS/numbers issues FOREVER across ALL generators:

```python
safe_thumbnail_text(text)          # Strip Devanagari, keep ₹ — fixes "पा" artifact
safe_tts_price(val, lang)          # "1457 rupaye" not ₹1457 — fixes TTS confusion
validate_stock_numbers(sl,tgt,cmp) # Basic sanity check — trusts Sheet values
get_prompt_rules(lang, sym, cmp, sl, target, mode)  # Injects 3 rules into ALL AI prompts:
                                   # Rule 1: Thumbnail = English only
                                   # Rule 2: Exact numbers from Sheet, never change
                                   # Rule 3: No ₹ symbol in TTS script

# Education-specific additions:
HOOKS_HINDI_EDUCATION   # 15 hooks — no trading language
HOOKS_ENGLISH_EDUCATION # 15 hooks — no trading language
CTAS_HINDI_EDUCATION    # "Subscribe for 52-week course" style
ht.get_hook(mode="education", lang="hi", week=1)  # Returns education hook
ht.get_video_description(mode="education", week=1, topic="...")  # Proper description
seo.get_video_tags(mode="education")  # Education tags (not trading tags)
```

---

## 12. Trading System Architecture (v15.5 AppScript + v15.0 Bot)

### Trading Bot v15.0 — New Entry Filters

**Analysis from May 15 performance:**
- Morning entries (9:15-11:00 AM): BSE +3.87%, IDEA +5.94%, ADANIPORTS +5.58% — ALL WON
- Afternoon entries (12:11 PM bearish): NESTLEIND -1.82%, SAIL -2.62% — BOTH NEGATIVE
- Pattern: RSI 35-55 + morning + Nifty green = winners

**5 new filters before every entry:**

| Filter | Order | Cost | Rule |
|--------|-------|------|------|
| Re-entry cooldown | 1st | Instant (memory) | 5 trading days after TARGET HIT |
| Time window | 2nd | Instant (date math) | Bearish: 9:15-11:00 AM only. Bullish: 9:15-2:30 PM |
| Daily entry limit | 3rd | Instant (count) | Bearish: max 1/day. Bullish: max 3/day |
| Nifty direction | 4th | Instant (sheet) | Bearish: Nifty must be GREEN. Bullish: > -0.3% |
| RSI check | 5th | API call (last) | Bearish: RSI < 58. Bullish: RSI < 65 |

**Re-entry cooldown (new v15.0):**
```
After TARGET HIT → set RECD key in T4: NSE_IDEA_RECD_2026-05-15
After TSL/SL hit → NO cooldown (can re-enter next day if fresh setup)
Check is first filter — instant memory lookup, no API
Result: IDEA won't re-enter until May 23 (5 trading days after May 15)
```

**Day rules:**
```
Monday before 10:00 AM → skip (weekend gap risk)
Friday after 2:00 PM  → skip (weekend holding risk)
```

### AppScript v15.5 — Gates

| Gate | Rule | Breakout | Base |
|------|------|----------|------|
| 1 | FII ≠ SELLING | Required | Required |
| 2 | Market Regime | Bearish→Leaders only | Bullish only |
| 3 | Late Entry RS≥5 | Applied | N/A |
| 4/4b | Price validity + Result skip | Required | Required |
| 5 | Retest ≥ -8% | Applied | EXEMPT |
| 6 | Pivot resistance | Applied | EXEMPT |
| 7 | Volume filter | >120% | Relaxed 40% |
| 8 | ATH buffer >1% | Applied | EXEMPT |
| 9 | Trade type not AVOID | Required | Required |
| 10 | Sector concentration ≤2 | Required | Required |
| 11 | Base quality (v15.4) | N/A | FII+VCP+Days+SMA+ATH gap |

### AlertLog Column Map (0-based)

```
A=0  Signal Time     B=1  Symbol         C=2  Live Price
D=3  Priority Score  E=4  Trade Type     F=5  Strategy
G=6  Breakout Stage  H=7  Initial SL     I=8  Target
J=9  RR Ratio        K=10 Trade Status   L=11 Entry Price
M=12 Entry Time      N=13 Days in Trade  O=14 Trailing SL
P=15 P/L%            Q=16 ATH Warning    R=17 Risk Rs.
S=18 Position Size   T=19 SYSTEM CONTROL
U=20 Options Signal  V=21 Strike         W=22 Expiry
X=23 Theta Risk

T2 = automation switch (YES/NO)
T4 = Python bot state (TSL/MAX/LP/ATR/EXDT/RECD per stock)
     RECD = Re-Entry Cooldown Date (set after TARGET HIT only)
     AppScript v15.5 protects T4 — clears col T rows 3+
```

### Paper Trading Performance (Week 1 — May 13-16)

```
Completed trades: 3 (3W / 0L) = 100% win rate
  BSE:        Entry ₹3,880 → Exit ₹4,030 | +3.87% | ₹502 profit | 1 day
  IDEA:       Entry ₹12.45 → Exit ₹13.19 | +5.94% | ₹773 profit | 2 days
  ADANIPORTS: Entry ₹1,716 → Exit ₹1,812 | +5.58% | ₹725 profit | 2 days
  Total realised: ₹2,001

Open trades (8): ONGC, BHEL, BHARATFORG, TATASTEEL, BANDHANBNK,
                  NESTLEIND, IDEA(new), SAIL
Watch: SAIL SL ₹191.33 — very close to current price

Need 27+ more completed trades before Phase 4 live trading.
```

### Telegram Channels

| Channel | Secret | Audience | Content |
|---------|--------|----------|---------|
| Basic | `CHAT_ID_BASIC` | Free | Market mood, signal count, CTA |
| Advance Rs.699/mo | `CHAT_ID_ADVANCE` | Paid | Full entry/exit, RSI, Nifty %, mid-day |
| Premium Rs.1499/mo | `CHAT_ID_PREMIUM` | Paid | Advance + Options signals + base entry |

---

## 13. Known Bugs & Status

### Bug 1 — trading_bot.py v15.0 not on GitHub 🔴
```
Drive: v15.0 (RSI+time+day+Nifty+RECD cooldown)
GitHub: v13.5 (old version, missing all 2026 improvements)
Fix: Download from Drive → paste into GitHub editor
Drive ID: 19Flhkq6__f3KuR5HzImJEXRC_5MnURGe
```

### Bug 2 — human_touch.py v2.2 not on GitHub 🔴
```
Missing: education hooks, safe_thumbnail_text, safe_tts_price, get_prompt_rules
Fix: Deploy from outputs
```

### Bug 3 — ai_client.py v2.2 not on GitHub 🔴
```
Missing: education system prompt, generate_with_stock_data
Fix: Deploy from outputs
```

### Bug 4 — generate_shorts.py v3.1 not on GitHub 🔴
```
Missing: ZENO stage-priority emotion fix, Facebook page-only fix
Fix: Deploy from outputs
```

### Bug 5 — Facebook Group Posting ❌
```
Token missing publish_to_groups scope.
Fix: Graph API Explorer → regenerate token with scope → update GitHub Secret
```

### Bug 6 — English Channel Credentials Missing
```
YOUTUBE_CREDENTIALS_EN not set → English uploads skipped gracefully (no crash).
Fix when ready: Add secret to GitHub.
```

---

## 14. Critical Upload Chain

### Daily Education (7:30 AM)
```
generate_education.py (hi) → YouTube Hindi
generate_education.py (en) → YouTube English (if credentials set)
```

### Daily Shorts (11:30 AM)
```
generate_shorts.py (hi) → YouTube + Facebook Page
generate_shorts.py (en) → YouTube English (if credentials set)
```

### HerooQuest Kids (8:00 AM)
```
Hindi job: full + short + didyouknow → 3 videos → YouTube Kids
English job: same 3 → YouTube Kids EN (if credentials set)
```

### Evening ZENO Reel (8:30 PM)
```
generate_reel.py → upload_youtube.py → upload_facebook.py → manual Instagram
```

---

## 15. Environment Variables & GitHub Secrets

### Telegram
| Secret | Purpose |
|--------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot auth token |
| `CHAT_ID_BASIC` | Free channel |
| `CHAT_ID_ADVANCE` | Advance Rs.699/mo |
| `CHAT_ID_PREMIUM` | Premium Rs.1499/mo |

### Social — AI360Trading
| Secret | Purpose | Status |
|--------|---------|--------|
| `META_ACCESS_TOKEN` | Facebook Page token | ✅ Auto-refreshed |
| `META_APP_ID` / `META_APP_SECRET` | Facebook App | ✅ |
| `FACEBOOK_PAGE_ID` | Main trading page | ✅ |
| `FACEBOOK_GROUP_ID` | Trading group | ✅ (posting broken) |
| `YOUTUBE_CREDENTIALS` | YouTube Hindi | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube English | 🔄 Phase 3 |

### Social — HerooQuest Kids
| Secret | Purpose | Status |
|--------|---------|--------|
| `FACEBOOK_KIDS_PAGE_ID` | HerooQuest FB Page | ✅ |
| `META_ACCESS_TOKEN_KIDS` | HerooQuest page token | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube Kids Hindi | ✅ |
| `YOUTUBE_CREDENTIALS_KIDS_EN` | YouTube Kids English | 🔄 Phase 3 |

### AI Providers
| Secret | Priority | Model |
|--------|----------|-------|
| `GROQ_API_KEY` | Primary | llama-3.3-70b-versatile |
| `GEMINI_API_KEY` | Secondary | gemini-2.0-flash |
| `ANTHROPIC_API_KEY` | Tertiary | claude-haiku-4-5-20251001 |
| `OPENAI_API_KEY` | Quaternary | gpt-4o-mini |
| `HF_TOKEN` | Image gen | Hugging Face |
| `STABILITY_API_KEY` | Image gen | Stability AI (3D backgrounds) |

### Dhan Trading API (Phase 4)
`DHAN_API_KEY`, `DHAN_API_SECRET`, `DHAN_CLIENT_ID`, `DHAN_PIN`, `DHAN_TOTP_KEY` — added, not connected.

### Google / GitHub
| Secret | Purpose |
|--------|---------|
| `GCP_SERVICE_ACCOUNT_JSON` | Google Sheets + Search Console |
| `GH_TOKEN` | GitHub API — token_refresh.py |
| `GOOGLE_SHEET_ID` | Sheet ID for fetch_live_trades() |

---

## 16. Human Touch System (v2.2)

| Method | Purpose |
|--------|---------|
| `ht.get_hook(mode, lang, week)` | mode="education" now works correctly |
| `ht.get_cta(lang, mode)` | Education CTAs vs market CTAs separated |
| `ht.get_video_description(mode, week, topic)` | Proper description for all content types |
| `ht.humanize(text, lang)` | Strips robotic patterns |
| `safe_thumbnail_text(text)` | Strips Devanagari, keeps ₹ — fixes "पा" |
| `safe_tts_price(val, lang)` | "1457 rupaye" not ₹1457 |
| `get_prompt_rules(lang, sym, cmp, sl, target, mode)` | Locks numbers, forces English thumbnail |
| `seo.get_video_tags(mode, is_short, channel, lang)` | Education vs market tags separated |

---

## 17. Technical Standards

### The Full Code Rule
> Always provide complete file content. Partial snippets or diffs are prohibited.

### Voice Assignments
| Voice | Used For |
|-------|---------|
| `hi-IN-SwaraNeural` | Education Hindi, Shorts Hindi, Kids Hindi, Reels |
| `en-US-JennyNeural` | Education English, Shorts English, Kids English |

### Video Formats
| Content | Ratio | Resolution |
|---------|-------|------------|
| Education, HerooQuest Full | 16:9 | 1920×1080 |
| All Shorts, Reels | 9:16 | 1080×1920 |

### Dependency Pins
| Package | Version |
|---------|---------|
| `moviepy` | ==1.0.3 |
| `imageio` | ==2.9.0 |
| `Pillow` | >=10.3.0 |

---

## 18. Website

| Property | Value |
|----------|-------|
| URL | ai360trading.in |
| Hosting | GitHub Pages (Jekyll, master branch _posts/) |
| MAX_POSTS | 60 articles — older auto-deleted |
| head.html | Conditional schema + dateModified=site.time |
| robots.txt | Single Disallow:/page covers all pagination |

---

## 19. Membership

| Plan | Price | Annual |
|------|-------|--------|
| Advance | Rs.699/month | Rs.5,588/year (save Rs.2,800) |
| Premium | Rs.1,499/month | Rs.11,988/year (save Rs.6,000) |

Payment: UPI 9634759528@upi
Activation: WhatsApp 9634759528 with screenshot + Telegram username

---

## 20. Disney 3D Reel Roadmap

| Phase | Tool | Status |
|-------|------|--------|
| 1 (Now) | PIL + MoviePy + ZENO PNG + Heroo PNG | ✅ Active |
| 1.5 | Stability AI backgrounds (img_client.generate_background()) | ✅ Code ready in ai_client.py v2.2 |
| 2 | Gemini Veo API (free tier) | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | Planned |
| 4 | Google Veo 2 / Sora (when free) | Planned |

---

## 21. Full Data Flow Diagram

```
MARKET HOURS (Mon-Fri 9:15 AM-3:30 PM IST)
trading_bot.py v15.0 (every 5 min):
  get_market_regime() → Nifty vs 20DMA
  step_a_enter_trades():
    Filter 1: Re-entry cooldown (RECD key) — instant
    Filter 2: Time window (day + regime) — instant
    Filter 3: Daily entry limit — instant
    Filter 4: Nifty direction — instant
    Filter 5: RSI(14) via yfinance — API call
    → If all pass: WAITING → TRADED, TSL set, Telegram sent
  step_b_monitor_trades():
    TSL updates → Advance+Premium
    Target hit → exit + set RECD cooldown (5 trading days)
    SL/TSL hit → exit (no cooldown)

AppScript v15.5 (every 5 min):
  _cleanSystemControlColumn() → protects T4
  11-gate filter → breakout or base
  Options signal → cols U-X + Premium Telegram
  Regime alert once/day → Advance+Premium

7:00 AM  → generate_reel_morning.py → YouTube + Facebook
7:30 AM  → generate_education.py (hi+en) → YouTube
8:00 AM  → generate_kids_video.py (3×2=6 videos) → YouTube Kids
10:00 AM → generate_articles.py → GitHub Pages + Facebook
11:30 AM → generate_shorts.py (hi→YouTube+FB | en→YouTube)
8:30 PM  → generate_reel.py (ZENO) → YouTube + Facebook
```

---

## 22. Channel Analytics & Growth Context

**AI360Trading (Main — as of May 2026):**
- 53 subscribers | 3,700 views/month | Watch time DOWN 31%
- Top Short: 416 views (ZENO Wisdom) — formula works
- Education course now running (evergreen > expiring market videos)
- ZENO emotion fix (v3.1) will improve CTR from next run

**HerooQuest (Kids — as of May 2026):**
- 1 subscriber | 162 views/28 days | CTR 0.6%
- 3 videos/day now live (full + cliffhanger + did you know)
- heroo.png character visible from May 17 (file fixed)
- Custom thumbnails enabled (phone verified)

---

## 23. Phase Roadmap

### Phase 1 ✅ Infrastructure (Complete)

### Phase 2 ✅ Content Upgrade (Complete)
All generators v2+ | Bot v15.0 | AppScript v15.5

### Phase 3 🔄 English Channel + Global Scale
- [x] Education course replacing market analysis ✅
- [x] generate_shorts.py v3.0 ✅ | v3.1 fix ⚠️ not pushed
- [x] generate_kids_video.py v2.0 ✅ — 3 videos/day live
- [x] heroo.png fixed (was heroo.png.png) ✅ May 16
- [x] human_touch.py v2.2 ✅ — education hooks, permanent fixes
- [x] ai_client.py v2.2 ✅ — education persona, stock number lock
- [x] trading_bot.py v15.0 ✅ — RSI+time+day+Nifty+RECD
- [x] Options signal system ✅ (v15.3)
- [x] Base entry system ✅ (v15.4)
- [ ] Push v15.0 bot + v2.2 files to GitHub 🔴 URGENT
- [ ] Add YOUTUBE_CREDENTIALS_EN secret
- [ ] Add YOUTUBE_CREDENTIALS_KIDS_EN secret
- [ ] HerooQuest thumbnails CTR improvement

### Phase 4 📋 Live Trading (After 30+ Paper Trades)
- Dhan API integration
- Win rate > 55% required
- 3 completed trades so far (need 27+ more)
- Current win rate: 100% (small sample — need more data)

---

## 24. Broker Partner Links

- [Zerodha](https://bit.ly/2VK6k5F)
- [Dhan](https://invite.dhan.co/?invite=MSIVC45309)

---

## 25. Contact & Legal

- **Admin:** admin@ai360trading.in
- **Location:** Haridwar, Uttarakhand, India
- **Legal:** All content educational only. Not SEBI registered.
- **Disclaimer:** ai360trading.in/disclaimer/
