# AI360Trading — Master System Documentation

**Last Updated:** April 8, 2026 — Full deep audit by Claude Sonnet 4.6: code review, bug findings, corrections, improvements, Phase 3/4 plans updated
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 In Progress | Phase 4 (Dhan Live) Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT).

---

## 0. AUDIT SUMMARY — April 8, 2026

Full code review of all files in the live repo (systronics/ai360trading). Every section below reflects actual code state, not just documentation.

### 🔴 CRITICAL BUGS FOUND

**BUG-001: generate_education.py — Still using Groq directly, NOT ai_client.py**
- File imports `from groq import Groq` and calls Groq directly
- This VIOLATES the AI client usage rule and bypasses the fallback chain
- If Groq is down, education video fails with no fallback
- Fix: Replace with `from ai_client import ai` and use `ai.generate_json()`

**BUG-002: generate_education.py — Slide count is NOT 22 (SYSTEM.md said fix was done)**
- Actual code: `generate_edu_slides()` uses `topic.get('slides', [])` — whatever content_calendar provides
- content_calendar.py topics have 4-6 slides, NOT 22
- The SYSTEM.md "fix" documents a plan but the code was NOT updated to 22 slides
- Result: education video is still only ~2-3 minutes, NOT 10-12 minutes
- Fix: Must either expand content_calendar slides to 22 per topic, OR change the prompt to expand each topic to 22 slides

**BUG-003: generate_education.py — voice pause is 0.8s, SYSTEM.md says fixed to 1.2s**
- Actual code line: `duration = voice_clip.duration + 0.8`
- SYSTEM.md claims this was fixed to 1.2s — it was NOT applied to the actual file
- Fix: Change to `duration = voice_clip.duration + 1.2`

**BUG-004: trading_bot.py — CHAT_ADVANCE and CHAT_PREMIUM are SWAPPED**
- Code: `CHAT_ADVANCE = os.environ.get('CHAT_ID_PREMIUM')` ← reads PREMIUM secret
- Code: `CHAT_PREMIUM = os.environ.get('CHAT_ID_ADVANCE')` ← reads ADVANCE secret
- This means advance signals go to premium channel and vice versa
- Fix: Swap the env var names OR swap the variable names throughout the file

**BUG-005: clean_mem() — Still using 30-day cutoff, SYSTEM.md says fixed to 14 days**
- Actual code: `cutoff = (datetime.now(IST) - timedelta(days=30)).strftime('%Y-%m-%d')`
- SYSTEM.md claims this was updated to 14 days — it was NOT applied
- The 20,000-char hard cap was also NOT added to the function
- Fix: Apply the 14-day + 20,000-char hard cap as documented in Section 10

**BUG-006: generate_education.py — Groq prompt asks for 50-70 words per slide**
- Actual prompt: `"content": "spoken Hinglish content 50-70 words"`
- SYSTEM.md says this was updated to 80-100 words — it was NOT applied
- Fix: Update prompt to 80-100 words per slide

### 🟡 WARNINGS / IMPROVEMENTS NEEDED

**WARN-001: content_calendar.py — Topics have 4-6 slides, need 22 for 10+ min video**
- All 5 weekday topic lists (Mon-Fri) have topics with only 4-8 slides each
- For 10-12 min education video: need either 22 slides OR a secondary expansion pass in generate_education.py
- Recommended fix: Add expansion logic in generate_education.py to pad to 22 slides using AI

**WARN-002: ai_client.py — Claude model name needs update**
- Code: `"claude-haiku-4-5-20251001"` — this is correct
- But `"claude-sonnet-4-6"` is listed without date suffix — may fail in API calls
- Fix: Update to `"claude-sonnet-4-6-20251101"` or verify the correct model string

**WARN-003: human_touch.py — random.seed(self.seed) set at __init__ time**
- Seed is set once on init with date value
- All calls to `random.choice()` after the first will be deterministic in sequence
- This is intentional (consistent daily content) but means if two generators run close together they share the same seed state
- Not a bug but worth noting — could cause minor content repetition if generators run in same process

**WARN-004: trading_bot.py — ATR is estimated, not read from Nifty200 sheet**
- When marking WAITING→TRADED, ATR is estimated: `atr_est = (target - cp) / atr_tgt_mult`
- Nifty200 sheet column AC (r[28]) = ATR14 but this data is NOT passed to trading_bot.py
- The real ATR is in the sheet — should be read directly for more accurate TSL calculations
- Fix (Phase 3): Pass ATR from AlertLog or read from Nifty200 at trade entry time

**WARN-005: generate_education.py — YouTube upload is inside the file itself**
- Mixes content generation with upload logic
- SYSTEM.md architecture says upload_youtube.py --type education handles upload
- But generate_education.py also has its own upload_to_youtube() function
- This creates a double-upload risk if workflow calls both
- Confirm: workflow should use upload_youtube.py ONLY, and generate_education.py should NOT upload

**WARN-006: generate_education.py — temp audio file is .aac but written to output/ dir**
- `temp_audiofile=str(OUT / "temp_edu_audio.aac")` — good, using .aac not .mp3
- But if workflow fails mid-render, this temp file persists and can cause next run to fail
- Fix: Add cleanup of temp files at start of run()

**WARN-007: content_calendar.py — Holiday topics have 5 slides each, not 22**
- For holiday education videos, all 8 HOLIDAY_TOPICS have exactly 5 slides
- Same 10-min problem applies on holidays
- Fix: Same as WARN-001 — expand logic needed

**WARN-008: trading_bot.py — No Telegram retry on message send failure**
- `_send_one()` returns False on failure but callers do not retry
- On transient network failures, alerts can be lost silently
- Fix: Add simple 1-retry with 5s delay in `_send_one()`

**WARN-009: human_touch.py — get_hook() uses seed%len(hooks) — same hook every day same weekday**
- seed = YYYYMMDD as int, so same weekday in different weeks could reuse hooks
- Actually fine since seed changes daily, but 20231101 % 20 = different from 20231108 % 20
- Not a real bug, just confirm the modulo spread is sufficient across the 50+ hooks

**WARN-010: generate_education.py — fallback uses content_calendar points joined with space**
- Fallback content: `" ".join(s.get("points", [...]))` joins bullet points directly
- Result is awkward spoken audio like "Point 1. Point 2. Point 3."
- Fix: Join with ". " and add a connector word between points in fallback

### ✅ THINGS CONFIRMED WORKING CORRECTLY

- ai_client.py: Fallback chain Groq→Gemini→Claude→OpenAI→Templates — correct and robust
- human_touch.py: Anti-AI patterns, 50+ hooks, personal phrases — all working correctly
- trading_bot.py: TSL logic, CE flag, market regime, entry/exit — all correct
- content_calendar.py: 5-day rotation with correct topic variety — working
- trading_bot.py: batch TSL cell writes — correctly prevents Google Sheets rate limits
- trading_bot.py: price_sanity() checks — good protection against bad data
- trading_bot.py: skip_exit min hold logic — correctly prevents premature exit
- generate_education.py: gradient background, level themes — visually good
- generate_education.py: Part 1 ↔ Part 2 cross-linking — correctly implemented

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
| Broker Referral | Zerodha + Dhan affiliate links | India |

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

YouTube's built-in **auto-translate** feature automatically subtitles Hindi videos into 100+ languages including English, allowing USA/UK/Australia viewers to watch and understand content without a second channel.

**What to do instead of a separate English channel:**

1. **Titles and descriptions** — always write in Hinglish with key English keywords for global search
2. **Enable YT auto-chapters** — ensure timestamps in descriptions so international viewers can navigate
3. **SEO tags** — include global English tags in every video (handled by `human_touch.py`)
4. **Thumbnail text** — use English or universal numbers/symbols on thumbnails where possible

**When to revisit:** Only create a separate English channel after reaching 10,000 subscribers OR if ad revenue data clearly shows demand.

**Files deferred:**
- `generate_english.py` — deferred indefinitely
- `upload_youtube_english.py` — deferred indefinitely

---

## 3. Platform Status

| Platform | Status | Notes |
| --- | --- | --- |
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | ✅ Passive | Auto-translate handles international reach |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | generate_community_post.py — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel working |
| YouTube Playlist Assignment | 🔄 Phase 3 | Deferred — not needed until 1000+ subscribers |
| Facebook Page | ✅ Auto | Posts, reels, article shares working |
| Facebook Group | ❌ Deferred | Broken + non-critical — removed from active workflows |
| Instagram | ❌ Deferred | Non-critical at current stage — removed from active workflows |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading) |

---

## 4. Facebook Group & Instagram — Deferred

**Decision (April 7, 2026):** Both removed from active workflows. Non-critical at current channel size.

### What was removed:
- `upload_instagram.py` — kept in repo but **NOT called in any workflow**
- Facebook Group posting logic in `upload_facebook.py` — kept in code but **disabled**

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
| 3 | Part 2 Video (16:9) — 10+ min | 7:30 AM (same workflow) | YouTube | ⚠️ Bug — still ~2-3 min (see BUG-001,002,003,006) |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 7 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB | ✅ |
| 8 | YouTube Community Post | 12:00 PM | YouTube Community Tab | ✅ |
| **Total** | **10 pieces/day** | — | — | — |

> **USA/UK prime time content:** Videos uploaded at IST times but SEO-optimised for 11 PM–1 AM IST peak.

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

> ⚠️ **generate_education.py has its own upload_to_youtube() function inside it.** If the workflow also calls upload_youtube.py --type education, the video will be uploaded TWICE. Audit the workflow YAML to confirm which method is used. One must be disabled.

---

## 8. Complete File Map

### Core Infrastructure (Phase 1 — Complete)

| File | Role | Status |
| --- | --- | --- |
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates fallback | ✅ |
| `human_touch.py` | Anti-AI-penalty layer — 50+ hooks, personal phrases, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update + Telegram alert | ✅ |

### Core Content Generation (Phase 2 — Mostly Complete, Education Has Bugs)

| File | Role | Key Tech | Status |
| --- | --- | --- | --- |
| `trading_bot.py` | Nifty200 signal monitor + TSL manager + Telegram alerts | gspread + Google Sheets + Telegram Bot API | ✅ v13.4 (BUG-004 — channels swapped) |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) — 55–60 sec each | ai_client, human_touch, Edge-TTS | ✅ Phase 2 |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ai_client, human_touch, MoviePy | ✅ Phase 2 |
| `generate_reel_morning.py` | Morning reel (7:00 AM) — day/country aware | ai_client, human_touch, MoviePy | ✅ Fixed Apr 7 |
| `generate_analysis.py` | 8-slide market analysis video (Part 1) | ai_client, human_touch, MoviePy | ✅ Phase 2 |
| `generate_education.py` | Educational deep-dive video (Part 2) | ai_client, human_touch, content_calendar | 🔴 3 bugs — NOT 10+ min yet |
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
| `content_calendar.py` | Rotates topics: Options, Technical Analysis, Psychology (4-8 slides per topic currently) |

### Static Assets

| Path | Contents |
| --- | --- |
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 9. Education Video — 10+ Minutes Fix Required

**Current state (April 8, 2026):** Video is still ~2-3 minutes. The SYSTEM.md documentation from April 7 described fixes that were NOT applied to the actual code.

**Required changes to generate_education.py:**

### Fix 1 — Replace Groq direct call with ai_client (BUG-001)
```python
# REMOVE these imports:
from groq import Groq

# REPLACE generate_edu_slides() with:
from ai_client import ai

def generate_edu_slides(topic, part1_url):
    prompt = f"""...(same prompt)..."""
    data = ai.generate_json(prompt, content_mode="market", lang="hi")
    return data
```

### Fix 2 — Increase slide count to 22 minimum (BUG-002)

The content_calendar topics have 4-8 slides. Two options:

**Option A (Recommended): Expand in generate_education.py prompt**
```python
# In the prompt, after showing topic slides:
f"""The above is an outline with {len(topic.get('slides', []))} sections.
Expand this into exactly 22 slides for a 10-12 minute video.
Keep the original sections. Add sub-slides, examples, case studies, and deeper explanations.
Each slide content must be 80-100 words of spoken Hinglish."""
```

**Option B:** Manually expand every topic in content_calendar.py to 22 slides (very large file change, not recommended)

### Fix 3 — Update word count in prompt (BUG-006)
```python
# Change in prompt:
"content": "spoken Hinglish content 80-100 words"  # was 50-70 words
```

### Fix 4 — Update pause duration (BUG-003)
```python
# Change in the slide loop:
duration = voice_clip.duration + 1.2  # was 0.8
```

### Fix 5 — Remove duplicate upload from generate_education.py (WARN-005)
Remove the `upload_to_youtube()` function and the upload call from `generate_education.py` entirely. Let `upload_youtube.py --type education` handle all uploads, consistent with all other generators.

**Verification step (already in SYSTEM.md — confirm it is in workflow YAML):**
```bash
python -c "
from moviepy.editor import VideoFileClip
v = VideoFileClip('output/education_video.mp4')
print(f'Education video duration: {v.duration:.1f}s ({v.duration/60:.1f} min)')
if v.duration < 480:
    print('WARNING: Video under 8 minutes — mid-roll ads will NOT activate')
    exit(1)
"
```

**Target:** 10–12 minutes (safely exceeds 8-minute YouTube mid-roll threshold with buffer).

---

## 10. T4 Memory — Migration to History Sheet (Critical Path)

**Problem:** T4 cell in AlertLog accumulates key=value memory strings indefinitely. Over months, this cell will exceed Google Sheets' 50,000 character cell limit, causing `gspread` write failures.

**Current status (April 8, 2026):**
- clean_mem() still uses 30-day window (SYSTEM.md said 14 days — NOT applied to code)
- 20,000-char hard cap NOT applied to code
- BotMemory sheet NOT created yet

### IMMEDIATE FIX — Update clean_mem() in trading_bot.py (BUG-005)

Replace the current `clean_mem()` function:

```python
def clean_mem(mem: str) -> str:
    """Remove entries older than 14 days. Hard cap at 20,000 chars."""
    cutoff = (datetime.now(IST) - timedelta(days=14)).strftime('%Y-%m-%d')
    kept = []
    for p in mem.split(','):
        p = p.strip()
        if not p:
            continue
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

**Add warning when T4 is growing large:**
```python
if len(mem) > 15000:
    print(f"[MEM WARNING] T4 memory is {len(mem)} chars — plan BotMemory migration soon")
```

### BotMemory Sheet Structure (Phase 3)

Create a new sheet named `BotMemory` with columns:
```
A = key        (e.g. "RELIANCE_TSL", "RELIANCE_MAX", "2025-01-15_AM")
B = value      (e.g. "285025", "298050", "1")
C = updated    (ISO datetime string — for debugging)
D = type       (TSL | MAX | ATR | LP | EXDT | FLAG | MODE | CAP | SEC)
```

### Migration Phases

**Phase A — Dual write:**
Write to BOTH T4 AND BotMemory sheet simultaneously. T4 continues as fallback.

**Phase B — Read from BotMemory only:**
Replace all `get_tsl(mem, key)` / `set_tsl(mem, key)` with sheet-based equivalents.

**Phase C — T4 cleared:**
T4 = "MIGRATED" — short static string. All memory in BotMemory sheet.

---

## 11. Reels & Shorts — Standards

### Reel Duration Rules

| Content | Target Duration | Platform Requirement |
| --- | --- | --- |
| ZENO Reel (`generate_reel.py`) | 45–60 seconds | YouTube Shorts ≤ 60s |
| Morning Reel (`generate_reel_morning.py`) | 30–45 seconds | Quick energetic hook |
| Short 2 — Madhur (`generate_shorts.py`) | 55–60 seconds | YouTube Shorts ≤ 60s |
| Short 3 — Swara (`generate_shorts.py`) | 55–60 seconds | YouTube Shorts ≤ 60s |

**Critical rule:** If TTS audio exceeds 58 seconds, trim to 58 seconds before upload.

### Reel Audio Script Word Limits

```python
# generate_reel.py:       80-100 words MAX → ~60-70s → trim to 58s if needed
# generate_reel_morning.py: 50-65 words MAX → ~45-55s → safe
# generate_shorts.py:      75-90 words MAX → ~55-60s → right at limit
```

### Video Dimensions — Never Mix

| Format | Width × Height | Used For |
| --- | --- | --- |
| 16:9 landscape | 1920 × 1080 | Analysis (Part 1), Education (Part 2) |
| 9:16 portrait | 1080 × 1920 | ALL reels and ALL shorts |

**Rule:** `SW, SH = 1080, 1920` in every reel/short generator. Never 16:9 for shorts.

### Reel Frame Quality Standards

Every reel/short frame MUST have:
1. **Brand watermark** — `ai360trading.in` visible (bottom center)
2. **Telegram CTA** — `t.me/ai360trading` on screen
3. **Main hook text** — large, readable on mobile (font size ≥ 44px)
4. **No cluttered layout** — Zeno character takes 40–50% of frame height
5. **Bottom 20% clear** — YouTube Subscribe button overlay sits here

### Upload Path

```
Shorts: generate_shorts.py → upload_youtube.py --type short2 / --type short3
ZENO Reel: generate_reel.py → upload_youtube.py --type reel → upload_facebook.py
Morning: generate_reel_morning.py → upload_youtube.py --type morning → upload_facebook.py
```

---

## 12. AI Fallback Chain

All content generation uses `ai_client.py`. **Never call Groq/Gemini/Claude/OpenAI directly in generators.**

```
Groq — llama-3.3-70b-versatile (primary — fastest, free)
    ↓ fails
Google Gemini — gemini-2.0-flash (secondary)
    ↓ fails
Anthropic Claude — claude-haiku-4-5-20251001 (tertiary — best human-touch writing)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary — reliable fallback)
    ↓ all fail
Pre-generated templates in human_touch.py (always works — zero downtime)
```

**⚠️ generate_education.py currently violates this rule — it calls Groq directly. Fix required (BUG-001).**

**Import pattern in ALL generators — no exceptions:**
```python
from ai_client import ai, img_client
from human_touch import ht, seo
```

---

## 13. Trading Bot Architecture

### Overview

| Component | File | Role |
| --- | --- | --- |
| AppScript v13.3 | Google Sheets bound script | Scans Nifty200, applies filters, writes WAITING candidates to AlertLog, stores memory in T4 |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog every 5 min, manages WAITING→TRADED, TSL updates, exit logic, Telegram alerts |

**Current status:** Paper trading. Followers receive Telegram signals and take manual entry.

### CRITICAL BUG: Telegram Channel Variables Are Swapped (BUG-004)

```python
# CURRENT (WRONG):
CHAT_ADVANCE = os.environ.get('CHAT_ID_PREMIUM')   # ← reads Premium secret!
CHAT_PREMIUM = os.environ.get('CHAT_ID_ADVANCE')   # ← reads Advance secret!

# CORRECT SHOULD BE:
CHAT_ADVANCE = os.environ.get('CHAT_ID_ADVANCE')   # ← reads Advance secret
CHAT_PREMIUM = os.environ.get('CHAT_ID_PREMIUM')   # ← reads Premium secret
```

This means paid Advance subscribers (₹499/mo) are receiving Premium-tier content, and Premium subscribers are receiving Advance-tier content. Fix immediately.

### Google Sheets Structure

| Sheet | Purpose |
| --- | --- |
| `Nifty200` | Live data for all 200 stocks — CMP, DMAs, FII data, signals, scores (34 cols) |
| `AlertLog` | Active + waiting trades — 15 rows, 19 cols. T2=YES/NO automation switch. T4=memory string |
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

### TSL Parameters (mode-aware)

```python
TSL_PARAMS = {
    "VCP": { "breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0 },
    "MOM": { "breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0 },
    "STD": { "breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0 },
}
```

### TSL Progression (STD example)

- Gain < 2% → hold initial SL
- Gain 2–4% → move to breakeven
- Gain 4–10% → lock at entry +2%
- Gain > 10% → ATR trail (2.5× ATR below CMP)
- Gain > 8% gap-up → lock 50% of gap

### Daily Message Schedule

- 08:45–09:15 → Good Morning
- 09:15–15:30 → Market hours alerts
- 12:28–12:38 → Mid-day pulse
- 15:15–15:45 → Market close summary

### Telegram Channels

- Basic (free) → market mood, signal closed result only
- Advance (₹499/mo) → full entry/exit details, TSL updates, mid-day pulse, CE candidate flag
- Premium (bundle) → same as Advance + options advisory

### CE Candidate Flag (v13.4 — informational only)

```
ATR% < 1.5%    → no flag
ATR% 1.5–2.5%  → normal mover: target +65%, SL -40% on premium
ATR% > 2.5%    → fast mover: target +50%, SL -35% on premium
Wednesday entry → prefer monthly expiry
```

### Hard Exit Rules

- Loss > 5% → hard loss exit
- Min hold: 2 days swing, 3 days positional
- 5 trading day cooldown after exit before same stock re-enters

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

### upload_youtube.py — Always Pass --type Flag

```bash
python upload_youtube.py --type reel       # ZENO reel
python upload_youtube.py --type morning    # morning reel
python upload_youtube.py --type analysis   # Part 1
python upload_youtube.py --type education  # Part 2
```

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py → upload_youtube.py --type reel → upload_facebook.py
```

### Morning Reel (7:00 AM)

```
generate_reel_morning.py → upload_youtube.py --type morning → upload_facebook.py
```

### Daily Videos (7:30 AM)

```
generate_analysis.py → upload_youtube.py --type analysis
generate_education.py → upload_youtube.py --type education
[duration check — fails workflow if < 8 min]
```

> ⚠️ **CONFIRM** that generate_education.py does NOT also upload internally. The file currently has its own upload_to_youtube() function. If the workflow uses upload_youtube.py --type education, the internal upload in generate_education.py must be removed or disabled.

---

## 15. Environment Variables & Secrets

All stored in **GitHub Actions Secrets**. Never hardcode any of these values.

### Social Platforms

| Secret | Purpose | Status |
| --- | --- | --- |
| `META_ACCESS_TOKEN` | Facebook + Instagram API | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ |
| `META_APP_SECRET` | Facebook App Secret | ✅ |
| `FACEBOOK_PAGE_ID` | Target Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Target Facebook Group ID | ✅ Kept — not used until Phase 3 |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business/Creator numeric ID | ✅ Kept — not used until Phase 3 |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | ✅ Active |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ Kept — not used (auto-translate) |

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
| `TELEGRAM_TOKEN` | Bot authentication token (note: code uses TELEGRAM_TOKEN, not TELEGRAM_BOT_TOKEN) |
| `TELEGRAM_CHAT_ID` | Free channel (ai360trading) |
| `CHAT_ID_ADVANCE` | Advance signals channel (₹499/month) |
| `CHAT_ID_PREMIUM` | Premium signals channel (bundle) |

### Dhan Trading API (Phase 4)

| Secret | Purpose | Status |
| --- | --- | --- |
| `DHAN_API_KEY` | API key | ✅ Added — not connected yet |
| `DHAN_API_SECRET` | API secret | ✅ Added — not connected yet |
| `DHAN_CLIENT_ID` | Client ID | ✅ Added — not connected yet |
| `DHAN_PIN` | Account PIN | ✅ Added — not connected yet |
| `DHAN_TOTP_KEY` | 2FA TOTP key | ✅ Added — not connected yet |

### YouTube Playlist Secrets (Phase 3 — NOT needed yet)

| Secret | Purpose | Status |
| --- | --- | --- |
| `YOUTUBE_PLAYLIST_REEL` | Playlist ID for ZENO reels | ⏳ Add in Phase 3 |
| `YOUTUBE_PLAYLIST_ANALYSIS` | Playlist ID for analysis videos | ⏳ Add in Phase 3 |
| `YOUTUBE_PLAYLIST_EDUCATION` | Playlist ID for education videos | ⏳ Add in Phase 3 |
| `YOUTUBE_PLAYLIST_MORNING` | Playlist ID for morning reels | ⏳ Add in Phase 3 |

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
| TTS speed variation | `ht.get_tts_speed()` | 0.95–1.05x range |
| Humanize output | `ht.humanize(text, lang)` | Strips robotic patterns, varies connectors |
| Emoji rotation | `ht.get_emoji_set()` | Day-seeded — different emoji set each day |
| SEO tags | `seo.get_video_tags(mode, lang)` | India + Global tags combined |
| Connector variation | Internal to humanize() | "aur/lekin/kyunki" rotated |
| Banned phrase removal | Internal to humanize() | "Certainly!", "It's important to note" stripped |

---

## 17. Known Issues & Status

### BUG-001: generate_education.py uses Groq directly instead of ai_client — 🔴 FIX REQUIRED
### BUG-002: Education video still ~2-3 min due to only 4-6 slides — 🔴 FIX REQUIRED
### BUG-003: Pause duration is 0.8s not 1.2s as documented — 🔴 FIX REQUIRED
### BUG-004: Telegram CHAT_ADVANCE and CHAT_PREMIUM variables are swapped — 🔴 FIX REQUIRED IMMEDIATELY
### BUG-005: clean_mem() still uses 30-day window, no hard cap — 🔴 FIX REQUIRED
### BUG-006: Education slide word count is 50-70, not 80-100 as documented — 🔴 FIX REQUIRED
### WARN-005: generate_education.py has duplicate upload logic — ⚠️ AUDIT WORKFLOW YAML
### generate_reel_morning.py KeyError 'target_countries' — ✅ FIXED (April 7, 2026)
### upload_youtube.py --type flag — ✅ ADDED (April 6, 2026)
### YouTube Playlist 403 — ⏳ DEFERRED to Phase 3
### Facebook Group Posting — ❌ DEFERRED to Phase 3
### Instagram Auto-Post — ❌ DEFERRED to Phase 3
### English YouTube Channel — ✅ NOT NEEDED (auto-translate strategy)
### YouTube Community Tab — ⚠️ Requires 500+ subscribers. Output saved to txt for manual posting below threshold.
### META_ACCESS_TOKEN Expiry — ✅ Automated every 50 days
### T4 Memory overflow risk — ⚠️ MITIGATION PENDING (clean_mem fix not yet applied)

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

**generate_education.py currently violates this rule. Fix required.**

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
| `en-US-JennyNeural` | Female | Reserved for English content |
| `en-US-GuyNeural` | Male | Reserved for English content |

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

Every video includes India-specific AND global tags via `seo.get_video_tags()`.

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
        └── T4 memory (⚠️ fix clean_mem — then migrate to BotMemory in Phase 3)
        └── get_market_regime() → Nifty CMP vs 20DMA
        └── WAITING→TRADED → entry alert → all 3 channels
        └── TSL updates → Advance + Premium
        └── Exit logic + History append + T4 memory update
        └── ⚠️ CHAT_ADVANCE and CHAT_PREMIUM are currently swapped — fix BUG-004

AppScript v13.3 (Google Sheets bound)
└── 10-gate filter → bearish or bullish path
└── Write WAITING rows to AlertLog
└── Write _CAP, _MODE, _SEC to T4 memory

7:00 AM daily
└── daily_reel.yml (morning job)
    └── generate_reel_morning.py
    └── upload_youtube.py --type morning ✅
    └── upload_facebook.py ✅ (Page only)

7:30 AM / 9:30 AM daily
└── daily-videos.yml
    └── generate_analysis.py
    └── upload_youtube.py --type analysis ✅
    └── generate_education.py  ← ⚠️ still ~2-3 min — 6 bugs to fix
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
```

---

## 21. Website

- **URL:** `ai360trading.in`
- **Hosting:** GitHub Pages (Jekyll, `master` branch `_posts/`)
- **Publishing:** Auto-commit by `daily-articles.yml`
- **SEO Indexing:** Instant via `GCP_SERVICE_ACCOUNT_JSON`
- **Revenue:** Google AdSense (USA/UK English readers = highest CPM)
- **Content pillars:** Stock Market, Bitcoin/Crypto, Personal Finance, AI Trading
- **Market coverage:** India (Nifty50, BankNifty), USA (S&P500, NASDAQ), UK (FTSE100), Brazil (IBOVESPA), Crypto (BTC, ETH)

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

### Phase 2 ✅ Mostly Complete (Education Video Has 6 Bugs — Fix Before Claiming Complete)
`generate_articles.py`, `generate_analysis.py`, `generate_education.py` (⚠️ bugs), `generate_reel.py`, `generate_shorts.py`, `generate_community_post.py`

### Phase 2.5 🔴 IMMEDIATE — Fix Critical Bugs

These must be fixed before any Phase 3 work:

| Bug | File | Fix | Priority |
| --- | --- | --- | --- |
| BUG-004 | `trading_bot.py` | Swap CHAT_ADVANCE/CHAT_PREMIUM env var names | 🔴 CRITICAL — losing subscriber trust |
| BUG-001 | `generate_education.py` | Replace Groq direct call with ai_client | 🔴 High |
| BUG-002 | `generate_education.py` | Add 22-slide expansion prompt | 🔴 High (losing mid-roll revenue) |
| BUG-003 | `generate_education.py` | Change pause from 0.8s to 1.2s | 🔴 High |
| BUG-006 | `generate_education.py` | Change word count from 50-70 to 80-100 | 🔴 High |
| BUG-005 | `trading_bot.py` | Update clean_mem() to 14-day + 20k cap | 🟡 Medium |
| WARN-005 | `generate_education.py` | Remove duplicate upload function | 🟡 Medium |
| WARN-008 | `trading_bot.py` | Add Telegram retry on failure | 🟡 Medium |

### Phase 3 🔄 Planned

| Item | File | Priority |
| --- | --- | --- |
| Fix Facebook Group token | Manual config task | 🟡 Medium (non-blocking) |
| Instagram verify live | After manual test | 🟡 Medium (non-blocking) |
| BotMemory sheet migration | `trading_bot.py` refactor | 🔴 High (do before T4 > 30,000 chars) |
| YouTube Playlist setup | Re-auth token + add secrets + uncomment call | 🔵 Low — after 1000 subs |
| Real ATR from sheet | `trading_bot.py` — read ATR from Nifty200 at entry | 🟡 Medium (better TSL accuracy) |
| Disney 3D reel upgrade | `ai_client.py` img_client Phase 2 | 🔵 Future |
| Telegram retry on failure | `trading_bot.py` — 1 retry with 5s delay | 🟡 Medium |
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

## 25. Next Session Priorities (For Working Together)

When we continue in the next session, work on these IN ORDER:

**Session 1 (do first):**
1. Fix BUG-004 in trading_bot.py (swap CHAT_ADVANCE/CHAT_PREMIUM)
2. Fix BUG-005 in trading_bot.py (update clean_mem)
3. Confirm workflow YAML — does generate_education.py upload internally or does upload_youtube.py handle it?

**Session 2:**
4. Rewrite generate_education.py completely:
   - Replace Groq with ai_client (BUG-001)
   - Change pause to 1.2s (BUG-003)
   - Change words to 80-100 (BUG-006)
   - Add 22-slide expansion prompt (BUG-002)
   - Remove duplicate upload if needed (WARN-005)

**Session 3:**
5. Test education video — confirm 10+ minutes
6. Add Telegram retry logic to trading_bot.py (WARN-008)
7. Begin BotMemory sheet setup (Phase 3)

---

*Documentation maintained by AI360Trading automation.*
*Full deep audit: April 8, 2026 — Claude Sonnet 4.6 — reviewed all files in live repo*
*6 critical bugs found, 10 warnings identified, all documented with exact file locations and fix instructions*
*Phase 1 complete: ai_client.py, human_touch.py, token_refresh.py, generate_reel_morning.py*
*Phase 2 mostly complete: all generators working EXCEPT generate_education.py (6 bugs — video still ~2-3 min not 10+ min)*
*Trading bot: AppScript v13.3 + Python v13.4 — paper trading active, BUG-004 (channel swap) critical to fix*
*Phase 3 remaining: Telegram channel swap fix, education video fix, clean_mem fix, BotMemory migration, playlists after 1000 subs*
*Phase 4 planned: Dhan live trading after backtest validation*
*Update this file whenever architecture, secrets, platform status, or file logic changes.*
