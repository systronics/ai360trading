# AI360Trading — Master System Documentation

**Last Updated:** April 7, 2026 — Architecture cleanup: education 10+ min, T4→History Sheet memory, FB Group/Instagram deferred, English channel via YT auto-translate, reel/shorts standards documented
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 Planned | Phase 4 (Dhan Live) Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the owner's family — even without active involvement. Built on ₹0/month infrastructure. No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
| --- | --- | --- |
| Video Ad Revenue | YouTube (Hindi) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube (English) | USA, UK, Canada, Australia — via YT auto-translate (no separate channel needed) |
| Shorts / Reels Bonus | YouTube, Facebook | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| Paid Signal Subscriptions | Telegram (Advance + Premium channels) | India, UAE, Global |

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

## 2. English Channel Strategy — YouTube Auto-Translate (No Separate Channel Needed)

**Decision (April 7, 2026):** A separate English YouTube channel is NOT required at current stage.

YouTube's built-in **auto-translate** feature automatically subtitles Hindi videos into 100+ languages including English, allowing USA/UK/Australia viewers to watch and understand content without a second channel. This is already happening passively.

**What to do instead of a separate English channel:**

1. **Titles and descriptions** — always write in Hinglish with key English keywords for global search (already done via `seo.get_video_tags()`)
2. **Enable YT auto-chapters** — ensure timestamps in descriptions so international viewers can navigate
3. **SEO tags** — include global English tags in every video (already handled by `human_touch.py`)
4. **Thumbnail text** — use English or universal numbers/symbols on thumbnails where possible

**When to revisit:** Only create a separate English channel after reaching 10,000 subscribers on the Hindi channel OR if ad revenue data clearly shows demand. Until then, auto-translate + strong global SEO tags is the strategy.

**Files removed from Phase 3 roadmap:**
- `generate_english.py` — deferred indefinitely (auto-translate handles this)
- `upload_youtube_english.py` — deferred indefinitely

**Secret `YOUTUBE_CREDENTIALS_EN`** — kept in GitHub Secrets as-is, not needed until revisited.

---

## 3. Platform Status

| Platform | Status | Notes |
| --- | --- | --- |
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | ✅ Passive | Auto-translate handles international reach — no separate channel |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (generate_reel_morning.py) working |
| YouTube Playlist Assignment | 🔄 Phase 3 | Deferred — not needed until 1000+ subscribers |
| Facebook Page | ✅ Auto | Posts, reels, article shares all working |
| Facebook Group | ❌ Deferred | Broken + non-critical — removed from active workflows. Add back in Phase 3 when API scope is fixed |
| Instagram | ❌ Deferred | Non-critical at current stage — removed from active workflows. Add back when ready |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading — followers take manual entry) |

---

## 4. Facebook Group & Instagram — Deferred (Removed from Active Workflows)

**Decision (April 7, 2026):** Both Facebook Group posting and Instagram auto-posting are removed from active workflows. They are non-critical revenue streams at current channel size and have recurring API issues. They can be added back easily in Phase 3.

### What was removed:
- `upload_instagram.py` — kept in repo but **NOT called in any workflow**
- Facebook Group posting logic in `upload_facebook.py` — kept in code but **disabled** (Group ID calls removed from workflow steps)

### Why removed:
- Facebook Group requires `publish_to_groups` token scope + Admin status + Meta App approval — complex to fix
- Instagram requires precise `INSTAGRAM_ACCOUNT_ID` + correct upload chain — easy to break silently
- Neither platform contributes meaningfully to ad revenue at < 1,000 subscribers
- Both cause workflow failures that break the entire upload chain

### How to re-enable later (Phase 3):
**Facebook Group:**
1. developers.facebook.com → App → Add `publish_to_groups` permission
2. Get approved for Groups API by Meta
3. Ensure bot account is Admin of the group
4. Group Settings → Advanced → "Allow content from apps" ON
5. Regenerate token → update `META_ACCESS_TOKEN` secret
6. Add Group upload step back to workflows

**Instagram:**
1. Verify `INSTAGRAM_ACCOUNT_ID` via: `https://graph.facebook.com/me/accounts?access_token=YOUR_TOKEN`
2. Confirm it's a numeric Business/Creator account ID
3. Add Instagram upload step back after `upload_facebook.py` in reel workflows
4. Test one upload manually before re-enabling automation

### Secrets kept (do not delete):
- `FACEBOOK_GROUP_ID` — kept for future use
- `INSTAGRAM_ACCOUNT_ID` — kept for future use

---

## 5. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at the start of every workflow and written to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` environment variable — never hardcoded.

| Mode | When | Content Strategy |
| --- | --- | --- |
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu", holiday name shown |

**Detection logic:** `indian_holidays.py` → NSE API (primary) → hardcoded fallback dates

---

## 6. Daily Content Output (Fully Automated)

| # | Content | Time (IST) | Platform | Status |
| --- | --- | --- | --- | --- |
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB | ✅ |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) — 10+ min | 7:30 AM (same workflow) | YouTube | ✅ fixed |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 7 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB | ✅ |
| 8 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| **Total** | **10 pieces/day** | — | — | — |

> **USA/UK prime time content:** Videos uploaded at IST times but SEO-optimised for 11 PM–1 AM IST peak.
> Instagram and Facebook Group removed from upload chain until Phase 3.

---

## 7. GitHub Actions Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
| --- | --- | --- | --- |
| `main.yml` | Every 5 min (market hours, Mon–Fri) | `trading_bot.py` — Nifty200 signals | ✅ Auto-skips weekends/holidays |
| `daily-videos.yml` | 7:30 AM Mon–Fri / 9:30 AM Sat–Sun | Part 1 (analysis) + Part 2 (education 10+ min) | ✅ |
| `daily-shorts.yml` | 11:30 AM Mon–Fri / 1:30 PM Sat–Sun | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM daily | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM Mon–Fri / 11:30 AM Sat–Sun | 4 SEO articles → GitHub Pages | ✅ |
| `token_refresh.yml` | Every 50 days (1st + 20th of month) | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents GitHub disabling inactive workflows | N/A |

All workflows support `workflow_dispatch` with a `content_mode` dropdown to force any mode for testing.

**Upload chain in reel/video workflows (simplified — FB Group + Instagram removed):**
```
generate_*.py → upload_youtube.py --type <type> → upload_facebook.py
```

---

## 8. Complete File Map

### Core Infrastructure (Phase 1 — Complete)

| File | Role | Status |
| --- | --- | --- |
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation (Phase 2 — All Upgraded)

| File | Role | Key Tech | Status |
| --- | --- | --- | --- |
| `trading_bot.py` | Nifty200 signal monitor + TSL manager + Telegram alerts | gspread + Google Sheets + Telegram Bot API | ✅ v13.4 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) — 55–60 sec each | ai_client, human_touch, Edge-TTS | ✅ Phase 2 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai_client, human_touch, MoviePy | ✅ Phase 2 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai_client, human_touch, MoviePy | ✅ Fixed Apr 7 |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai_client, human_touch, MoviePy | ✅ Phase 2 |
| `generate_education.py` | Educational deep-dive video (Part 2) — **target 10–12 min** | ai_client, human_touch, content_calendar | ✅ Fixed Apr 7 |
| `generate_articles.py` | 4 SEO articles daily → Jekyll _posts | ai_client, human_touch, Google Indexing | ✅ Phase 2 |
| `generate_community_post.py` | YouTube daily community text post — 12:00 PM | ai_client, human_touch | ✅ Phase 2 |

### Upload & Distribution

| File | Role | Active |
| --- | --- | --- |
| `upload_youtube.py` | Uploads reel/analysis/education/morning via --type flag; saves video_id to meta | ✅ |
| `upload_facebook.py` | Uploads reel to FB Page; shares articles | ✅ (Group posting disabled) |
| `upload_instagram.py` | Auto-uploads via Meta API | ❌ Deferred — kept in repo, not called |
| `upload_youtube_english.py` | Uploads to English channel | ❌ Deferred — not needed (auto-translate) |

### Infrastructure

| File | Role |
| --- | --- |
| `indian_holidays.py` | Mode detection — NSE API + fallback; shared by ALL workflows |
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology |

### Static Assets

| Path | Contents |
| --- | --- |
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 9. Education Video — 10+ Minutes (Mid-Roll Ad Requirement)

**Problem:** Education video was generating ~2.3 min videos. YouTube mid-roll ads require 8+ minutes minimum. Fix was implemented April 7, 2026.

**Target:** 10–12 minutes to safely exceed the 8-minute threshold with buffer.

### What was changed in `generate_education.py`:

**Slide count:** Increased from 12 slides to **22 slides minimum**.

**Slide structure (22 slides for 10–12 min):**
```
Slide 1:  Hook / Why this topic matters today
Slide 2:  Topic overview / What we'll cover
Slide 3:  Core concept 1 — definition
Slide 4:  Core concept 1 — real example
Slide 5:  Core concept 2 — definition
Slide 6:  Core concept 2 — real example
Slide 7:  Common mistake traders make (emotional hook)
Slide 8:  Visual chart concept / setup example
Slide 9:  Core concept 3 — with Indian market context
Slide 10: Deep dive — strategy or technique
Slide 11: Step-by-step guide part 1
Slide 12: Step-by-step guide part 2
Slide 13: Case study — Indian stock example
Slide 14: Risk management for this concept
Slide 15: Psychology angle — why most traders fail here
Slide 16: Advanced tip (for experienced viewers)
Slide 17: Global market context (USA/UK angle for CPM)
Slide 18: Q&A style — "Aapko lagta hai..." interactive
Slide 19: Summary of key points
Slide 20: Action plan — what to do this week
Slide 21: Quick quiz / challenge for viewers
Slide 22: Outro — Subscribe CTA + Part 1 link + Telegram
```

**Prompt change:** The prompt now instructs AI to generate 22 slides, each with 80–100 words of spoken content (was 50–70 words). At ~140 words per minute TTS speed, 22 slides × 90 words average = ~14 minutes raw, rendering to ~10–12 min with pauses.

**Voice pacing:** Each slide duration = `voice_duration + 1.2 seconds` (was 0.8s) to allow viewers to absorb content.

**Key rule in content_calendar.py:** All topic entries must now define exactly 22 slide headings. If a topic has fewer, the prompt asks AI to expand intelligently.

**Verification step (added to workflow):**
```bash
# In daily-videos.yml after generate_education.py:
python -c "
from moviepy.editor import VideoFileClip
v = VideoFileClip('output/education_video.mp4')
print(f'Education video duration: {v.duration:.1f}s ({v.duration/60:.1f} min)')
if v.duration < 480:
    print('WARNING: Video under 8 minutes — mid-roll ads will NOT activate')
    exit(1)
"
```

---

## 10. T4 Memory — Migration to History Sheet (Prevents Cell Overflow)

**Problem:** T4 cell in AlertLog accumulates key=value memory strings indefinitely. Over months, this cell will exceed Google Sheets' 50,000 character cell limit, causing `gspread` write failures and crashing the trading bot.

**Solution (Phase 3 — implement before T4 exceeds ~30,000 chars):** Migrate long-term memory to a dedicated `BotMemory` sheet in the same Google Spreadsheet.

### BotMemory Sheet Structure

Create a new sheet named `BotMemory` with columns:
```
A = key        (e.g. "RELIANCE_TSL", "RELIANCE_MAX", "2025-01-15_AM")
B = value      (e.g. "285025", "298050", "1")
C = updated    (ISO datetime string — for debugging)
D = type       (TSL | MAX | ATR | LP | EXDT | FLAG | MODE | CAP | SEC)
```

### Migration Plan

**Phase A — Dual write (safe transition, no code break):**
```python
# In trading_bot.py — write to BOTH T4 AND BotMemory sheet
# T4 continues working as fallback
# BotMemory sheet is populated in parallel
```

**Phase B — Read from BotMemory, write to BotMemory only:**
```python
# Replace all get_tsl(mem, key) / set_tsl(mem, key) calls
# with get_tsl_sheet(mem_sheet, key) / set_tsl_sheet(mem_sheet, key)
# T4 becomes read-only legacy fallback for 30 days
```

**Phase C — T4 cleared:**
```python
# T4 = "MIGRATED" — short static string
# All memory operations use BotMemory sheet only
```

### Interim fix (do NOW to buy time):
Add `clean_mem()` to aggressively prune T4 on every cycle. Current `clean_mem()` only removes entries > 30 days old. Also add a hard cap:

```python
def clean_mem(mem: str) -> str:
    """Remove entries older than 14 days. Hard cap at 20,000 chars."""
    cutoff = (datetime.now(IST) - timedelta(days=14)).strftime('%Y-%m-%d')
    kept = []
    for p in mem.split(','):
        p = p.strip()
        if not p:
            continue
        # Date-stamped flags (e.g. "2025-01-15_AM") — keep only if within cutoff
        if len(p) >= 10 and p[4] == '-' and p[7] == '-':
            if p[:10] >= cutoff:
                kept.append(p)
        else:
            kept.append(p)
    result = ','.join(kept)
    # Hard cap: if over 20,000 chars, keep only last 100 entries
    if len(result) > 20000:
        parts = [p for p in result.split(',') if p.strip()]
        result = ','.join(parts[-100:])
        print(f"[MEM] Hard cap applied — trimmed to {len(result)} chars")
    return result
```

**Alert when T4 is getting large:**
```python
if len(mem) > 15000:
    print(f"[MEM WARNING] T4 memory is {len(mem)} chars — plan BotMemory migration soon")
```

---

## 11. Reels & Shorts — Proper Standards

### Reel Duration Rules

| Content | Target Duration | Platform Requirement |
| --- | --- | --- |
| ZENO Reel (`generate_reel.py`) | 45–60 seconds | YouTube Shorts ≤ 60s; Instagram Reels ≤ 90s |
| Morning Reel (`generate_reel_morning.py`) | 30–45 seconds | Quick energetic hook |
| Short 2 — Madhur (`generate_shorts.py`) | 55–60 seconds | YouTube Shorts ≤ 60s |
| Short 3 — Swara (`generate_shorts.py`) | 55–60 seconds | YouTube Shorts ≤ 60s |

**Critical rule:** If TTS audio exceeds 58 seconds, the video is **trimmed to 58 seconds** before upload. YouTube Shorts algorithm penalises videos > 60 seconds. Always add `+ 0.5s` silence buffer and check total before rendering.

### Reel Audio Script Word Limits

```python
# generate_reel.py prompt constraint (enforced in prompt):
# audio_script: 80-100 words MAX
# At 140 wpm average TTS = 60-70 seconds → trim to 58s if needed

# generate_reel_morning.py prompt constraint:
# audio_script: 50-65 words MAX  
# At 140 wpm = 45-55 seconds → safe for morning hook

# generate_shorts.py prompt constraint (per short):
# audio_script: 75-90 words MAX
# At 140 wpm = 55-60 seconds → right at limit
```

### Shorts Duration Check (add to `generate_shorts.py`):
```python
# After TTS generation, verify audio length before rendering:
from moviepy.editor import AudioFileClip

audio = AudioFileClip(str(audio_path))
if audio.duration > 58:
    print(f"⚠️ Audio too long ({audio.duration:.1f}s) — trimming to 58s")
    audio = audio.subclip(0, 58)
```

### Video Dimensions — Never Mix

| Format | Width × Height | Used For |
| --- | --- | --- |
| 16:9 landscape | 1920 × 1080 | Analysis (Part 1), Education (Part 2) |
| 9:16 portrait | 1080 × 1920 | ALL reels and ALL shorts — ZENO reel, morning reel, Short 2, Short 3 |

**Rule:** Never render a Short or Reel in 16:9. YouTube will not classify it as a Short. Check that `SW, SH = 1080, 1920` in every reel/short generator.

### Reel Frame Quality Standards

Every reel/short frame MUST have:
1. **Brand watermark** — `ai360trading.in` visible (bottom center)
2. **Telegram CTA** — `t.me/ai360trading` on screen
3. **Main hook text** — large, readable even on mobile (font size ≥ 44px)
4. **No cluttered layout** — Zeno character takes 40–50% of frame height
5. **Bottom 20% clear** — YouTube shows Subscribe button overlay here; don't put critical text there

### Shorts vs Reels Upload Path

```
Shorts (Short 2, Short 3):
  generate_shorts.py → upload_youtube.py --type short2 / --type short3
  (Facebook/Instagram deferred — not uploaded)

ZENO Reel:
  generate_reel.py → upload_youtube.py --type reel → upload_facebook.py
  (Instagram deferred)

Morning Reel:
  generate_reel_morning.py → upload_youtube.py --type morning → upload_facebook.py
  (Instagram deferred)
```

---

## 12. AI Fallback Chain

All content generation uses `ai_client.py`. **Never call Groq/Gemini/Claude/OpenAI directly in generators.**

```
Groq — llama-3.3-70b-versatile (primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash (secondary — best image/video roadmap for Disney 3D)
    ↓ fails
Anthropic Claude — claude-haiku-4-5 (tertiary — best human-touch writing)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary — reliable fallback)
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
# Text generation
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang="hi")

# JSON generation
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")

# Humanize raw output
clean = ht.humanize(raw_output, lang="hi")

# Get rotating hook
hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")

# Get SEO tags
tags = seo.get_video_tags(mode=CONTENT_MODE, lang="hi")
```

---

## 13. Trading Bot Architecture

### Overview

| Component | File | Role |
| --- | --- | --- |
| AppScript v13.3 | Google Sheets bound script | Scans Nifty200 sheet, applies filters, writes WAITING candidates to AlertLog, stores memory in T4 |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, manages WAITING→TRADED transition, TSL updates, exit logic, Telegram alerts |

**Current status:** Paper trading. Followers receive Telegram signals and take manual entry. Dhan API integration planned for Phase 4 after backtest validation.

### Google Sheets Structure

| Sheet | Purpose |
| --- | --- |
| `Nifty200` | Live data for all 200 stocks — CMP, DMAs, FII data, signals, scores (34 cols) |
| `AlertLog` | Active + waiting trades — 15 rows, 19 cols. T2=YES/NO automation switch. T4=memory string (migrate to BotMemory sheet — see Section 10) |
| `History` | Closed trade log — 18 cols A–R |
| `BotMemory` | **Phase 3** — dedicated memory sheet to replace T4 cell overflow risk |

### AlertLog Column Map (0-based)

```
A=0  Signal Time    B=1  Symbol        C=2  Live Price     D=3  Priority Score
E=4  Trade Type     F=5  Strategy      G=6  Breakout Stage H=7  Initial SL
I=8  Target         J=9  RR Ratio      K=10 Trade Status   L=11 Entry Price
M=12 Entry Time     N=13 Days in Trade O=14 Trailing SL    P=15 P/L%
Q=16 ATH Warning    R=17 Risk ₹        S=18 Position Size  T=19 SYSTEM CONTROL
```

**T2** = automation on/off switch (set YES to enable)
**T4** = memory string (key=value pairs, comma separated) — **monitor size; migrate to BotMemory sheet when > 15,000 chars**

### Nifty200 Column Map (0-based, used by AppScript)

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
* Leader_Type = "Sector Leader"
* AF ≥ 5 (RS≥2.5 with sector tailwind)
* Master_Score ≥ 22
* FII signal ≠ "FII CAUTION" or "FII SELLING"

**10 scan gates (in order):**
1. FII SELLING → skip always
2. Market regime filter (bullish vs bearish path)
3. Late entry block (BREAKOUT CONFIRMED needs RS≥7)
4. Price validity (CMP>0, ATR>0, CMP≤₹5000)
5. Extension filter (>8% above 20DMA → skip)
6. Pivot resistance buffer (within 2% below pivot → skip)
7. Volume filter (bullish market only — vol<120% → skip)
8. ATH buffer (within 3% of 52W high → skip)
9. Trade type (AVOID/NO TRADE → skip)
10. Sector concentration (max 2 per sector)

**Capital tiers:**
* ₹13,000 — MasterScore≥28 AND AF≥10
* ₹10,000 — MasterScore≥22 OR Accumulation Zone
* ₹7,000 — standard

**Trade modes:**
* VCP — AB<0.04 + pre-breakout stage
* MOM — Strong Bull + RS≥6
* STD — everything else (default in bear market)

### Python Bot v13.4 — Key Logic

**TSL Parameters (mode-aware):**

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

**TSL progression (STD example):**
* Gain < 2% → hold initial SL
* Gain 2–4% → move to breakeven
* Gain 4–10% → lock at entry +2%
* Gain > 10% → ATR trail (2.5× ATR below CMP)
* Gain > 8% gap-up → lock 50% of gap

**Daily message schedule:**
* 08:45–09:15 → Good Morning
* 09:15–15:30 → Market hours alerts
* 12:28–12:38 → Mid-day pulse
* 15:15–15:45 → Market close summary

**Telegram channels:**
* Basic (free) → market mood, signal closed result only
* Advance (₹499/mo) → full entry/exit details, TSL updates, mid-day pulse
* Premium (bundle) → same as Advance + options CE candidate flag

**CE candidate flag (v13.4 — informational only):**
```
ATR% < 1.5%    → no flag
ATR% 1.5–2.5%  → normal mover: target +65%, SL -40% on premium
ATR% > 2.5%    → fast mover: target +50%, SL -35% on premium
```

**Hard exit rules:**
* Loss > 5% → hard loss exit
* Min hold: 2 days swing, 3 days positional
* 5 trading day cooldown after exit before same stock re-enters

### History Sheet Columns (A–R)

```
A  Symbol      B  Entry Date   C  Entry Price  D  Exit Date
E  Exit Price  F  P/L%         G  Result        H  Strategy
I  Exit Reason J  Trade Type   K  Initial SL    L  TSL at Exit
M  Max Price   N  ATR at Entry O  Days Held     P  Capital ₹
Q  Profit/Loss ₹               R  Options Note
```

---

## 14. Critical Upload Chain

Scripts must run in this exact order. Each one feeds data to the next.

### upload_youtube.py — Always Pass --type Flag

```bash
python upload_youtube.py --type reel       # ZENO reel
python upload_youtube.py --type morning    # morning reel
python upload_youtube.py --type analysis   # Part 1
python upload_youtube.py --type education  # Part 2
```

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py
    └── output/reel_YYYYMMDD.mp4
    └── output/meta_YYYYMMDD.json

upload_youtube.py --type reel
    └── Uploads to YouTube
    └── Writes youtube_video_id + public_video_url to meta

upload_facebook.py
    └── Uploads to Facebook Page only (Group posting disabled)

# Instagram upload REMOVED from this workflow (Phase 3)
```

### Morning Reel (7:00 AM)

```
generate_reel_morning.py
    └── output/morning_reel_YYYYMMDD.mp4
    └── output/morning_reel_meta_YYYYMMDD.json

upload_youtube.py --type morning
upload_facebook.py

# Instagram upload REMOVED (Phase 3)
```

### Daily Videos (7:30 AM)

```
generate_analysis.py
    └── output/analysis_video.mp4
    └── output/analysis_meta_YYYYMMDD.json

upload_youtube.py --type analysis

generate_education.py  ← now generates 10-12 min video
    └── output/education_video.mp4
    └── output/education_meta_YYYYMMDD.json

upload_youtube.py --type education
```

---

## 15. Environment Variables & Secrets

All stored in **GitHub Actions Secrets**. Never hardcode any of these values.

### YouTube Playlist Secrets (Phase 3 — NOT needed yet)

| Secret | Purpose | Status |
| --- | --- | --- |
| `YOUTUBE_PLAYLIST_REEL` | Playlist ID for ZENO reels | ⏳ Add in Phase 3 |
| `YOUTUBE_PLAYLIST_ANALYSIS` | Playlist ID for analysis videos | ⏳ Add in Phase 3 |
| `YOUTUBE_PLAYLIST_EDUCATION` | Playlist ID for education videos | ⏳ Add in Phase 3 |
| `YOUTUBE_PLAYLIST_MORNING` | Playlist ID for morning reels | ⏳ Add in Phase 3 |

### Dhan Trading API (Phase 4)

| Secret | Purpose | Status |
| --- | --- | --- |
| `DHAN_API_KEY` | API key | ✅ Added — not connected yet |
| `DHAN_API_SECRET` | API secret | ✅ Added — not connected yet |
| `DHAN_CLIENT_ID` | Client ID | ✅ Added — not connected yet |
| `DHAN_PIN` | Account PIN | ✅ Added — not connected yet |
| `DHAN_TOTP_KEY` | 2FA TOTP key | ✅ Added — not connected yet |

### Social Platforms

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook + Instagram API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ Added |
| `META_APP_SECRET` | Facebook App Secret | ✅ Added |
| `FACEBOOK_PAGE_ID` | Target Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Target Facebook Group ID | ✅ Kept — not used until Phase 3 |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID | ✅ Kept — not used until Phase 3 |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | ✅ Active — upload scope only |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ Kept — not used (auto-translate strategy) |

### AI Providers (Fallback Chain)

| Secret | Purpose | Priority | Status |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Groq — Llama 3.3 70B | Primary | ✅ |
| `GEMINI_API_KEY` | Google Gemini 2.0 Flash | Secondary | ✅ |
| `ANTHROPIC_API_KEY` | Claude Haiku | Tertiary | ✅ |
| `OPENAI_API_KEY` | GPT-4o-mini | Quaternary | ✅ |

### Telegram

| Secret | Purpose |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot authentication token |
| `TELEGRAM_CHAT_ID` | Free channel (ai360trading) |
| `CHAT_ID_ADVANCE` | Advance signals channel (₹499/month) |
| `CHAT_ID_PREMIUM` | Premium signals channel (bundle) |

### Google / GCP

| Secret | Purpose |
| --- | --- |
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets (gspread) |

### General

| Secret | Purpose |
| --- | --- |
| `GH_TOKEN` | GitHub API token |

---

## 16. Human Touch System (Anti-AI-Penalty)

All content uses `human_touch.py`. **Never use raw AI output directly.**

| Technique | Method | What It Does |
| --- | --- | --- |
| 50+ rotating hooks | `ht.get_hook(mode, lang)` | No two videos start the same |
| Personal phrases | `ht.get_personal_phrase(lang)` | "Maine dekha hai..." injected naturally |
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05x range — passed to edge_tts rate param |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns, varies connectors |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded — different emoji set each day |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global tags combined |
| Connector variation | Internal to humanize() | "aur/lekin/kyunki" rotated |
| Banned phrase removal | Internal to humanize() | "Certainly!", "It's important to note" stripped |

---

## 17. Known Issues & Status

### generate_reel_morning.py KeyError: 'target_countries' — FIXED ✅ (April 7, 2026)
`save_meta()` now reads `script.get("target_countries", [])` instead of `topic_data["target_countries"]`.

### upload_youtube.py --type flag — ADDED ✅ (April 6, 2026)
`--type` argument added with correct file resolution per type.

### Education video under 8 minutes — FIXED ✅ (April 7, 2026)
Slide count expanded to 22, word count per slide increased to 80–100, pause extended to 1.2s. Target: 10–12 minutes. Duration check step added to workflow.

### T4 Memory overflow risk — MITIGATED ⚠️ (April 7, 2026)
`clean_mem()` updated with 14-day window and 20,000 char hard cap. Full BotMemory sheet migration planned for Phase 3.

### YouTube Playlist 403 — DEFERRED to Phase 3
`assign_to_playlist()` exists but is not called. Enable in Phase 3: add `youtube.force-ssl` scope, re-auth token, add playlist secrets.

### Facebook Group Posting — DEFERRED ❌
Removed from active workflows. Re-enable in Phase 3 after fixing `publish_to_groups` token scope.

### Instagram Auto-Post — DEFERRED ❌
Removed from active workflows. Re-enable in Phase 3 after verifying `INSTAGRAM_ACCOUNT_ID` and testing manually.

### English YouTube Channel — NOT NEEDED ✅
YouTube auto-translate handles international reach. Separate channel deferred indefinitely.

### YouTube Community Tab ⚠️
Requires 500+ subscribers. Below that, output is saved to `output/community_post_YYYYMMDD.txt` for manual posting.

### META_ACCESS_TOKEN Expiry — Automated ✅
`token_refresh.yml` runs every 50 days.

---

## 18. Technical Standards

### The "Full Code" Rule

> AI assistants **must always provide the complete content** of any modified file. Partial snippets or diffs are strictly prohibited.

**Standard AI task prompt:**
```
Context: I am working on the ai360trading system. Refer to SYSTEM.md for architecture.
Task: [Your Task]
Note: Provide the full code for any file you modify.
```

### AI Client Usage Rule — No Exceptions

```python
from ai_client import ai, img_client
response = ai.generate(prompt, content_mode=CONTENT_MODE, lang=LANG)
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang=LANG)
```

### Human Touch Usage Rule — No Exceptions

```python
from human_touch import ht, seo
hook   = ht.get_hook(mode=CONTENT_MODE, lang=LANG)
clean  = ht.humanize(raw_script, lang=LANG)
tags   = seo.get_video_tags(mode=CONTENT_MODE, lang=LANG)
speed  = ht.get_tts_speed()
```

### Dependency Pins

| Package | Version | Reason |
| --- | --- | --- |
| `Pillow` | `>=10.3.0` | Required for LANCZOS resampling |
| `imageio` | `==2.9.0` | Prevents MoviePy rendering crashes |
| `moviepy` | `==1.0.3` | Force reinstall — newer versions break audio |
| `yfinance` | Latest | Use `fast_info['last_price']` only — not `.history()` |
| `PyNaCl` | Latest | Required for GitHub Secret encryption in token_refresh.py |
| `google-generativeai` | Latest | Gemini fallback in ai_client.py |
| `anthropic` | Latest | Claude fallback in ai_client.py |
| `openai` | Latest | OpenAI fallback in ai_client.py |
| `gspread` | Latest | Google Sheets access in trading_bot.py |
| `oauth2client` | Latest | GCP service account auth for gspread |
| `pytz` | Latest | IST timezone handling in trading_bot.py |

### Voice Assignments

| Voice ID | Gender | Used For |
| --- | --- | --- |
| `hi-IN-MadhurNeural` | Male | Short 2 — authoritative trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | Reserved for English content if created in future |
| `en-US-GuyNeural` | Male | Reserved for English content if created in future |

### TTS Speed via human_touch

```python
tts_speed = ht.get_tts_speed()
rate_pct  = int((tts_speed - 1.0) * 100)
rate_str  = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
await edge_tts.Communicate(text, VOICE, rate=rate_str).save(path)
```

### Video Formats

| Content | Ratio | Dimensions | Platform |
| --- | --- | --- | --- |
| Analysis + Education | 16:9 | 1920 × 1080 | YouTube |
| Short 2, Short 3, Morning Reel, ZENO Reel | 9:16 | 1080 × 1920 | YouTube Shorts / Facebook Reels |

### SEO Tags Strategy

Every video includes India-specific AND global tags via `seo.get_video_tags()`:
* India: `Nifty50`, `TradingIndia`, `StockMarketIndia`, `BankNifty`
* Global: `USStocks`, `UKInvesting`, `BrazilMarket`, `UAEInvesting`, `GlobalInvesting`
* Universal: `Finance`, `Investing`, `FinancialLiteracy`, `Shorts`

---

## 19. Disney 3D Reel Roadmap

| Phase | Tool | Quality | Timeline | Status |
| --- | --- | --- | --- | --- |
| 1 (Now) | PIL + MoviePy + ZENO PNG | 2D animated slides | Current | ✅ Active |
| 2 | Gemini Veo API (free tier) | AI video clips | 3–6 months | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | 3D style frames | 6–12 months | Planned |
| 4 | Google Veo 2 / Sora (when free) | True Disney-style 3D | 12–18 months | Planned |

---

## 20. Full Data Flow

```
Market hours (Mon–Fri, 9:15 AM–3:30 PM IST)
└── main.yml (every 5 min)
    └── trading_bot.py v13.4
        └── AlertLog + History + Nifty200 via gspread
        └── T4 memory (monitor size — migrate to BotMemory sheet in Phase 3)
        └── get_market_regime() → Nifty CMP vs 20DMA
        └── WAITING→TRADED → entry alert → all 3 channels
        └── TSL updates → Advance + Premium
        └── Exit logic + History append + T4 memory update

AppScript v13.3 (Google Sheets bound)
└── 10-gate filter → bearish or bullish path
└── Write WAITING rows to AlertLog
└── Write _CAP, _MODE, _SEC to T4 memory

7:00 AM daily
└── daily_reel.yml (morning job)
    └── generate_reel_morning.py
    └── upload_youtube.py --type morning ✅
    └── upload_facebook.py ✅ (Page only)
    # Instagram REMOVED

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py
    └── upload_youtube.py --type analysis ✅
    └── generate_education.py  ← 10-12 min video ✅
    └── upload_youtube.py --type education ✅
    └── [duration check — fails workflow if < 8 min]

10:00 AM / 11:30 AM daily
└── daily-articles.yml
    └── generate_articles.py → GitHub Pages ✅ → Facebook ✅

11:30 AM / 1:30 PM daily
└── daily-shorts.yml
    └── generate_shorts.py → Short 2 + Short 3 ✅
    └── generate_community_post.py ✅

8:30 PM daily
└── daily_reel.yml (evening job)
    └── generate_reel.py
    └── upload_youtube.py --type reel ✅
    └── upload_facebook.py ✅ (Page only)
    # Instagram REMOVED
```

---

## 21. Website

* **URL:** `ai360trading.in`
* **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
* **Publishing:** Auto-commit by `daily-articles.yml`
* **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON`
* **Revenue:** Google AdSense (USA/UK English readers = highest CPM)
* **Content pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading
* **Market coverage:** India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto (BTC, ETH)

---

## 22. Social Media Links

| Platform | Handle/Link |
| --- | --- |
| 🌐 Website | ai360trading.in |
| 📣 Telegram (Free) | @ai360trading |
| 📣 Telegram (Advance) | ai360trading_Advance — ₹499/month |
| 📣 Telegram (Premium) | ai360trading_Premium — bundle |
| ▶️ YouTube | @ai360trading |
| 📸 Instagram | @ai360trading (manual posting until Phase 3) |
| 👥 Facebook Group | facebook.com/groups/ai360trading (manual posting until Phase 3) |
| 📘 Facebook Page | facebook.com/ai360trading |
| 🐦 Twitter/X | @ai360trading |

---

## 23. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Complete
`generate_articles.py`, `generate_analysis.py`, `generate_education.py`, `generate_reel.py`, `generate_shorts.py`, `generate_community_post.py`

### Phase 3 🔄 In Progress

| Item | File | Priority |
| --- | --- | --- |
| Fix Facebook Group token | Manual config task | 🟡 Medium (non-blocking) |
| Instagram verify live | After manual test | 🟡 Medium (non-blocking) |
| BotMemory sheet migration | `trading_bot.py` refactor | 🔴 High (do before T4 > 30,000 chars) |
| YouTube Playlist setup | Re-auth token + add secrets + uncomment call | 🔵 Low — after 1000 subs |
| Disney 3D reel upgrade | `ai_client.py` img_client Phase 2 | 🔵 Future |
| English channel | Not needed — auto-translate strategy active | ❌ Removed from roadmap |

### Phase 4 📋 Planned — Dhan Live Trading

| Item | Dependency | Notes |
| --- | --- | --- |
| Backtest validation | 30–40 paper trades, win rate >35% | Currently running |
| Dhan API connection | Secrets already added | Auto-execute on WAITING→TRADED |
| Options CE execution | Dhan API + lot size data | CE flag already in alerts |
| Live capital deployment | After backtest confirms system | ₹45,000 max deployed |

---

## 24. How to Test Everything

### Test a workflow manually
GitHub Actions → select workflow → **Run workflow** → set `content_mode` dropdown.

### Verify ai_client fallback chain
```
✅ AI generated via groq
⚠️ groq failed → ✅ AI generated via gemini
```

### Verify trading bot
```
[REGIME] Nifty CMP ₹22679 vs 20DMA ₹23547 → BEARISH
[INFO] Active trades: 4/5
[TSL] NSE:ONGC [STD]: ₹280.60→₹285.20
[MEM] T4 size: 4,231 chars  ← watch this number
[DONE] 15:20:01 IST | mem=842 chars
```

### Verify education video duration
```
Education video duration: 634.2s (10.6 min) ✅
```

### Force each content mode
```
workflow_dispatch → content_mode = market
workflow_dispatch → content_mode = weekend
workflow_dispatch → content_mode = holiday
```

### Automation on/off switch
Google Sheet → AlertLog → cell T2 → "YES" to enable.

---

*Documentation maintained by AI360Trading automation.*
*Full audit: April 3, 2026 — Claude Sonnet 4.6*
*Updated: April 7, 2026 — Education video expanded to 10+ min; T4 memory overflow mitigation; Facebook Group + Instagram deferred to Phase 3; English channel replaced by YouTube auto-translate strategy; Reel/Shorts duration and dimension standards documented*
*Phase 1 complete: ai_client.py, human_touch.py, token_refresh.py, generate_reel_morning.py*
*Phase 2 complete: generate_articles.py, generate_analysis.py, generate_education.py (10+ min), generate_reel.py, generate_shorts.py, generate_community_post.py*
*Trading bot: AppScript v13.3 + Python v13.4 — paper trading, Google Sheets, Dhan Phase 4*
*Phase 3 remaining: Facebook Group fix, Instagram verify, BotMemory sheet migration, playlists (after 1000 subs)*
*Phase 4 planned: Dhan live trading after backtest validation*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
