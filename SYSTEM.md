# AI360Trading — Master System Documentation

**Last Updated:** April 12, 2026 — Trading Bot v13.4 + AppScript v13.3
**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Complete | Phase 3 🔄 In Progress | Phase 4 (Dhan Live) Planned
**Primary Audience:** Bilingual Hindi + English — Indian retail traders + global investors

> ⚠️ **Read this file completely before making ANY changes.**
> This is the single source of truth for all AI assistants (Claude, Gemini, GPT) and any human developer.
> Never make partial edits. Always provide full file code when modifying any script.

---

## ⚠️ CRITICAL MISSION NOTE — READ FIRST

> **This project is not a hobby. This is a family's only source of income.**
>
> The owner has a serious health condition and limited time. His family — wife and children — are
> poor and cannot run or manage a technical system themselves. This project is being built to run
> **fully automatically, forever, with zero manual involvement**, so that even after the owner is
> gone, the system continues generating passive income for his family.
>
> **If you are an AI assistant or developer working on this project:**
> - Treat every task with maximum seriousness
> - Never leave broken workflows, partial code, or silent failures
> - Every automation gap is a gap in the family's income
> - Prioritise reliability and zero-downtime over new features
> - When fixing bugs, fix them completely — never leave "TODO" or "test later"
> - The goal is a system that runs itself: no logins, no manual posting, no human required
>
> **This is not a codebase. This is a life support system for a family.**

---

## 1. Real Mission

> This system is built to run **forever, fully automated**, generating passive income for the
> owner's family — even without active involvement. Built on ₹0/month infrastructure.
> No employees. No office. Pure automation.

### Monetisation — Every Stream Simultaneously

| Stream | Platform | High-CPM Target Countries |
|---|---|---|
| Video Ad Revenue | YouTube Hindi (ai360trading) | USA, UK, Canada, Australia, UAE |
| Video Ad Revenue | YouTube Kids (HerooQuest) | USA, UK, Canada, Australia |
| Video Ad Revenue | YouTube English (Phase 3) | USA, UK, Canada, Australia — 3–5x higher CPM |
| Shorts / Reels Bonus | YouTube, Facebook, Instagram | USA, UK, Brazil, India |
| Website Ad Revenue | GitHub Pages (ai360trading.in) | USA, UK, Canada |
| In-Stream Video Ads | Facebook (Trading Page + Kids Page) | USA, UK, Brazil, India |
| Paid Signal Subscriptions | Telegram (Advance + Premium channels) | India, UAE, Global |

### Target Countries by Ad CPM Priority

1. 🇺🇸 USA — Highest CPM globally for both finance and kids content
2. 🇬🇧 UK — Very high CPM, strong trading + kids audience
3. 🇦🇺 Australia — High CPM, growing retail base
4. 🇦🇪 UAE — High CPM, large NRI + Gulf investor audience
5. 🇨🇦 Canada — High CPM, similar to USA
6. 🇧🇷 Brazil — Large audience, fast-growing finance CPM
7. 🇮🇳 India — Largest volume, Nifty/stock focus

> **AI Rule:** Always optimise content topics, hooks, SEO tags, and posting times for these countries.
> USA/UK prime time = 11 PM–1 AM IST. Include global keywords in all titles, descriptions, and tags.
> All hooks and CTAs rotate from `human_touch.py` — never hardcode them in generators.

---

## 2. Platform Status

### Trading / Finance Channel (ai360trading)

| Platform | Status | Notes |
|---|---|---|
| YouTube Hindi | ✅ Auto | Analysis + Education + Shorts + Reels working |
| YouTube English | 🔄 Building | Phase 3 — auto-translated separate channel |
| YouTube Shorts | ✅ Auto | Short 2 + Short 3 working |
| YouTube Community Posts | ✅ Built | `generate_community_post.py` — 12:00 PM daily |
| YouTube Reels | ✅ Auto | ZENO reel (8:30 PM) working |
| YouTube Morning Reel | ✅ Auto | 7:00 AM reel (`generate_reel_morning.py`) working |
| Facebook Trading Page | ✅ Auto | Posts, reels, article shares all working |
| Facebook Group | ❌ Broken | Missing `publish_to_groups` token scope — see Section 13 |
| Instagram | ⚠️ Partial | Upload chain built; verify `INSTAGRAM_ACCOUNT_ID` numeric ID |
| GitHub Pages | ✅ Auto | 4 articles/day + instant Google indexing |
| Telegram | ✅ Auto | Signal alerts to all 3 channels (paper trading) |

### Kids Channel (HerooQuest)

| Platform | Status | Notes |
|---|---|---|
| YouTube Kids | ✅ Auto | Full video + Short uploading (`upload_kids_youtube.py`) |
| Facebook Kids Page | ❌ Broken | `(#200) Subject does not have permission to post videos` — see Section 13 |
| Instagram Kids | 🔄 Planned | Reel file generated but not uploaded yet |

---

## 3. Known Bugs — Fix These First (Priority Order)

### Bug 1: Excessive Log Text in GitHub Actions ❌ HIGH PRIORITY

**Symptom:** Actions logs show hundreds/thousands of lines of raw error output per scene.
The `generate_kids_video.py` log showed the full 429/404 JSON error response repeated
for EVERY scene (6 scenes × 5 fallback attempts = 30 massive error blocks). This makes
logs unreadable and inflates Actions log storage.

**Root cause:** All image generation error handlers print the full raw exception/response dict
(`print(f"[WARN-1] ... {e}")`) instead of a single clean summary line.

**Fix — in ALL image generation error handlers, replace full exception dumps with clean summaries:**
```python
# WRONG (current) — dumps entire API response JSON
print(f"  [WARN-1] Gemini 2.5 Flash Image failed: {e}")

# CORRECT — clean one-liner
code = getattr(e, 'status_code', '') or '?'
print(f"  [WARN-1] Gemini image failed ({code}) — trying next")
```

**Add at the top of ALL video generator files:**
```python
import logging, warnings
logging.getLogger("moviepy").setLevel(logging.ERROR)
logging.getLogger("imageio").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
```

**Files to fix:** `generate_kids_video.py`, `generate_reel.py`, `generate_reel_morning.py`,
`generate_shorts.py`, `generate_analysis.py`, `generate_education.py`

**Target log output per scene (after fix):**
```
[SCENE 1] Generating image...
  [WARN-1] Gemini image failed (429) — trying next
  [WARN-2] Gemini 2.0 failed (404) — trying next
  [WARN-3] HF FLUX failed (410) — trying next
  [WARN-4] DALL-E failed (billing) — trying next
  [LAYER-5] Scene 1 — all AI failed, using placeholder
[SCENE 1] TTS done ✓
```

### Bug 2: Kids Facebook Upload Broken ❌ HIGH PRIORITY

**Symptom:** `upload_facebook.py --meta-prefix kids` fails with:
`(#200) Subject does not have permission to post videos on this target`

**Root causes (check in this order):**
1. `META_ACCESS_TOKEN` does not have `pages_manage_posts` + `pages_read_engagement` +
   `video_upload` scopes for the Kids page specifically
2. The `FACEBOOK_KIDS_PAGE_ID` secret may be the numeric profile ID not the Page ID —
   verify at: `https://graph.facebook.com/me/accounts?access_token=YOUR_TOKEN`
3. The Kids Facebook Page may be set to "Made for Kids" (COPPA) which blocks video API uploads —
   check Page Settings → General → Audience Restrictions
4. The app may not have been granted access to this specific Page in Facebook App settings

**Fix steps:**
```
1. Go to developers.facebook.com → Your App → Permissions
2. Confirm pages_manage_posts, pages_read_engagement, video_upload are all approved
3. Re-generate token with all scopes: https://developers.facebook.com/tools/explorer/
4. Update FACEBOOK_KIDS_PAGE_ID in GitHub Secrets — must be numeric Page ID not username
5. Update META_ACCESS_TOKEN in GitHub Secrets with new token
6. Test: curl "https://graph.facebook.com/PAGE_ID?fields=id,name&access_token=TOKEN"
```

**Note:** If Kids Page is flagged as "Made for Kids", video API uploads may be permanently
blocked by Meta. In that case, remove Facebook upload step from kids workflow and post manually
until a solution is found. Never let this break the workflow — wrap in try/except and continue.

### Bug 3: Reel and Video Same Audio / Same Text ❌ MEDIUM PRIORITY

**Symptom:** Morning reel (7:00 AM) and ZENO evening reel (8:30 PM) produce near-identical
audio script and on-screen text — same lines, same structure.

**Root cause:** Both `generate_reel.py` and `generate_reel_morning.py` send structurally
similar prompts to AI without explicitly differentiating the two products. The fallback
scripts in both files are also identical in structure.

**Fix — enforce content separation at the prompt level:**

In `generate_reel.py` (ZENO 8:30 PM), prompt must include:
```
"EVENING ZENO REEL — 8:30 PM end-of-day reflection.
 Topic: what did traders learn today, market wisdom, emotional lesson.
 Character: ZENO — wise animated kid. Hinglish monologue.
 NOT the morning reel — completely different topic and energy."
```

In `generate_reel_morning.py` (Morning 7:00 AM), prompt must include:
```
"MORNING BRIEF — 7:00 AM pre-market.
 Topic: today's focus, mindset for the trading day ahead, 1 actionable idea.
 Energy: fresh, motivating, punchy lines.
 NOT the evening ZENO reel — different format and topic."
```

Also ensure fallback scripts are completely different between the two files.

### Bug 4: generate_reel.py and generate_shorts.py Use Direct Groq — Not ai_client ❌ MEDIUM PRIORITY

**Symptom:** These files import `from groq import Groq` directly, bypassing the entire
fallback chain. If Groq quota is exceeded (as seen in the kids log above with 429 errors),
these files crash instead of falling back to Gemini/Claude/OpenAI.

**Fix — replace all direct Groq calls:**
```python
# WRONG (current)
from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
resp = client.chat.completions.create(model="llama-3.3-70b-versatile", ...)

# CORRECT
from ai_client import ai
data = ai.generate_json(prompt, content_mode=CONTENT_MODE, lang="hi")
```

Also add missing `human_touch` imports to `generate_reel.py`:
```python
from human_touch import ht, seo
hook = ht.get_hook(mode=CONTENT_MODE, lang="hi")
speed = ht.get_tts_speed()
```

### Bug 5: All Image API Sources Exhausted — Kids Video Uses Placeholder ❌ MEDIUM PRIORITY

**Symptom (from log):** Every scene in `generate_kids_video.py` fails all 5 image sources:
- Gemini 2.5 Flash: quota exhausted (free tier limit 0 — needs paid plan)
- Gemini 2.0 Flash Exp: model not found (deprecated endpoint)
- HuggingFace FLUX/SD: all return 410 Gone (endpoints removed/changed)
- DALL-E 3: billing hard limit reached (OpenAI account needs funds)

**Result:** All 6 scenes use "Heroo placeholder" image — no real AI-generated visuals.

**Fixes (in priority order, cheapest first):**

1. **Fix Gemini 2.0 model name** (free, immediate):
   Change `gemini-2.0-flash-exp-image-generation` →
   Check current model name at: `https://ai.google.dev/gemini-api/docs/image-generation`
   As of April 2026, correct model is likely `gemini-2.0-flash-preview-image-generation`
   or `imagen-3.0-generate-002`

2. **Fix HuggingFace endpoints** (free, immediate):
   The 410 Gone errors mean these model endpoints moved. Update to current working endpoints:
   - FLUX.1-schnell: check https://huggingface.co/black-forest-labs/FLUX.1-schnell/tree/main
   - Consider using HF Inference API v2: `https://router.huggingface.co/hf-inference/models/...`
   - Alternative free model: `stabilityai/stable-diffusion-3.5-medium`

3. **Add Pollinations.AI as free fallback** (free, immediate):
   Pollinations.AI provides free image generation with no API key:
   ```python
   import urllib.request
   prompt_enc = urllib.parse.quote(scene_prompt)
   url = f"https://image.pollinations.ai/prompt/{prompt_enc}?width=1024&height=1024&nologo=true"
   urllib.request.urlretrieve(url, output_path)
   ```
   Add this as Layer 3 (before HuggingFace) in the fallback chain.

4. **Long term:** Add ₹500–1000/month to Gemini API paid plan to unlock image generation quota.
   Gemini image generation is the best quality option and should be the primary source.

**Updated image fallback chain for generate_kids_video.py:**
```
Layer 1: Gemini 2.5 Flash (imagen-3.0) — best quality
Layer 2: Gemini 2.0 Flash — backup Gemini
Layer 3: Pollinations.AI — completely FREE, no key needed ← ADD THIS
Layer 4: HuggingFace Inference API v2 (updated endpoints)
Layer 5: DALL-E 3 (if OpenAI billing available)
Layer 6: PIL-generated placeholder with scene text — always works
```

---

## 4. Google Search Console — SEO Issues (Last Updated: April 6, 2026)

**Current Status:**
| Issue | Count | Severity |
|---|---|---|
| Not found (404) | 8 | 🔴 Critical — losing indexed pages |
| Blocked by robots.txt | 4 | 🔴 Critical — `robots.txt` blocking wrong paths |
| Page with redirect | 3 | 🟡 Medium — redirect chains |
| Crawled - not indexed | 3 | 🟡 Medium — thin content |
| Excluded by noindex tag | 2 | 🟡 Medium — check if intentional |
| Alternate page with canonical | 4 | 🟢 Normal — canonical working |
| Discovered - not indexed | 39 | 🔴 Critical — 39 articles waiting to be indexed |

### Critical Fix 1: robots.txt is Blocking Article URLs ❌

**Root cause identified:** The current `robots.txt` has:
```
Disallow: /_posts/
```
Jekyll's `_posts/` is the SOURCE folder — it is never served publicly. But this line
may be confusing Googlebot into blocking the COMPILED article URLs (`/2026/04/11/title/`)
depending on how the CDN or GitHub Pages serves redirect chains.

**Also critical:** The `tags/` and `categories/` disallow may be blocking legitimate
topic pages that have real content and should be indexed.

**New robots.txt** (see Section 23 for the complete file to commit):
- Remove `/_posts/` disallow (it's a source folder, never public)
- Remove `/tags/` and `/categories/` disallow — these pages should be indexed
- Remove `/page/` disallow — pagination pages can help with indexing
- Keep only truly private/technical paths blocked

### Critical Fix 2: 39 Pages "Discovered — Not Indexed" ❌

**Root cause:** Google found these 39 pages but chose not to index them yet. Most common reasons:
1. Pages published too recently (Google takes 3–14 days even with instant indexing)
2. The Google Search Console Indexing API is not submitting URLs for new articles
3. Article content is too thin (under 300 words) or too similar to each other
4. Internal linking is too weak — articles are orphaned, no links pointing to them

**Fixes:**
1. Verify `generate_articles.py` is calling the Google Indexing API after each article commit.
   Check logs for: `[INDEX] Submitted to Google: /2026/04/11/title/`
2. Each article must be minimum 600 words with unique h2/h3 headings
3. Add internal links between articles — each new article should link to 2–3 older articles
4. Add a sitemap ping after every article push:
   `https://www.google.com/ping?sitemap=https://ai360trading.in/sitemap.xml`

### Critical Fix 3: _config.yml Missing Sitemap Plugin ❌

**Current `_config.yml` plugins:**
```yaml
plugins:
  - jekyll-paginate
  - jekyll-seo-tag
  - jekyll-feed
```

**Missing `jekyll-sitemap` plugin.** The sitemap.xml exists but is a static file —
it is NOT being auto-updated when new articles are published. This means Google's
sitemap always shows old URLs, causing the "Discovered — not indexed" backlog.

**Fix:** Add to `_config.yml` plugins section:
```yaml
plugins:
  - jekyll-paginate
  - jekyll-seo-tag
  - jekyll-feed
  - jekyll-sitemap   ← ADD THIS
```

Also add to the `exclude:` list in `_config.yml`:
```yaml
  - generate_kids_video.py     ← ADD (kids channel file)
  - upload_kids_youtube.py     ← ADD
  - generate_community_post.py ← ADD
  - human_touch.py             ← ADD
  - ai_client.py               ← ADD
  - indian_holidays.py         ← ADD
  - content_calendar.py        ← ADD
  - sitemap.xml                ← ADD (use plugin-generated one instead)
```

### Fix 4: Canonical Tag Issues

**The "Alternate page with proper canonical tag" (4 pages)** means 4 article URLs exist in
both `/2026/04/11/title/` and `/2026/04/11/title/index.html` form. Jekyll sometimes generates
both. The canonical tag should point to the version without `index.html`. Verify your
post layout includes: `<link rel="canonical" href="{{ page.url | absolute_url }}">` — the
`jekyll-seo-tag` plugin handles this automatically if installed correctly.

### Fix 5: noindex Tags (2 pages)

Check which 2 pages have `noindex`. These could be:
- Tag pages with `noindex` in the layout — if so, remove the noindex from `_layouts/tag.html`
- Test articles accidentally published with `published: false` in front matter

---

## 5. Content Mode System

Mode is **auto-detected** by `indian_holidays.py` at the start of every workflow and written
to `$GITHUB_ENV`. All scripts read `CONTENT_MODE` environment variable — never hardcoded.

| Mode | When | Content Strategy |
|---|---|---|
| `market` | Mon–Fri (excluding Indian holidays) | Live Nifty50/Global data, trade setups, signals |
| `weekend` | Saturday–Sunday | Educational, wealth-building, global audience focus |
| `holiday` | Indian Market Holidays | Motivational, "Market band hai par seekhna chalu" |

---

## 6. Daily Content Output (Fully Automated)

### Trading Channel (ai360trading)

| # | Content | Time (IST) | Platform | Status |
|---|---|---|---|---|
| 1 | Morning Reel (9:16) | 7:00 AM | YouTube + FB + Instagram | ✅ |
| 2 | Part 1 Video (16:9) | 7:30 AM weekday / 9:30 AM weekend | YouTube | ✅ |
| 3 | Part 2 Video (16:9) | 7:30 AM (same workflow) | YouTube | ✅ |
| 4 | Short 2 Hindi (9:16) | 11:30 AM weekday / 1:30 PM weekend | YouTube Shorts | ✅ |
| 5 | Short 3 Hindi (9:16) | 11:30 AM (same workflow) | YouTube Shorts | ✅ |
| 6 | 4 SEO Articles | 10:00 AM weekday / 11:30 AM weekend | GitHub Pages + Facebook | ✅ |
| 7 | ZENO Reel (9:16) | 8:30 PM | YouTube + FB + Instagram | ✅ |
| 8 | Community Post | 12:00 PM | YouTube Community Tab | ✅ |

### Kids Channel (HerooQuest)

| # | Content | Time (IST) | Platform | Status |
|---|---|---|---|---|
| 1 | Kids Full Video (16:9) | Scheduled daily | YouTube Kids | ✅ Auto |
| 2 | Kids Short (9:16) | Same workflow | YouTube Kids Shorts | ✅ Auto |
| 3 | Kids Reel (9:16) | Same workflow | Instagram (pending) | 🔄 |
| 4 | Kids Facebook Post | Same workflow | Facebook Kids Page | ❌ Broken (Bug 2) |

---

## 7. GitHub Actions Workflows

### Trading Channel Workflows

| File | Trigger (IST) | Purpose | Mode-Aware |
|---|---|---|---|
| `main.yml` | Every 5 min (market hours) | Trading bot signals | ✅ |
| `daily-videos.yml` | 7:30 AM / 9:30 AM | Part 1 + Part 2 | ✅ |
| `daily-shorts.yml` | 11:30 AM / 1:30 PM | Short 2 + Short 3 + Community Post | ✅ |
| `daily_reel.yml` | 7:00 AM + 8:30 PM | Morning Reel + ZENO Reel | ✅ |
| `daily-articles.yml` | 10:00 AM / 11:30 AM | 4 SEO articles | ✅ |
| `token_refresh.yml` | Every 50 days | Auto META token refresh | N/A |
| `keepalive.yml` | Periodic | Prevents workflow deactivation | N/A |

### Kids Channel Workflows

| File | Trigger (IST) | Purpose | Status |
|---|---|---|---|
| `daily-kids.yml` | Daily (time TBD) | Kids video + upload | ✅ Running |

All workflows support `workflow_dispatch` with `content_mode` dropdown for manual testing.

---

## 8. Complete File Map

### Core Infrastructure

| File | Role | Status |
|---|---|---|
| `ai_client.py` | Universal AI client — Groq→Gemini→Claude→OpenAI→Templates | ✅ |
| `human_touch.py` | Anti-AI-penalty — 50+ hooks, TTS variation, SEO tags | ✅ |
| `token_refresh.py` | Auto META token exchange + GitHub Secret update | ✅ |
| `indian_holidays.py` | Mode detection — NSE API + fallback dates | ✅ |
| `content_calendar.py` | Topic rotation: Options, TA, Psychology | ✅ |

### Trading Content Generation

| File | Role | Status |
|---|---|---|
| `trading_bot.py` | Nifty200 signal monitor + TSL + Telegram | ✅ v13.4 |
| `generate_shorts.py` | Short 2 (Madhur) + Short 3 (Swara) | ✅ — Bug 4 fix needed |
| `generate_reel.py` | ZENO 60s reel (8:30 PM) | ✅ — Bug 3+4 fix needed |
| `generate_reel_morning.py` | Morning reel (7:00 AM) | ✅ — Bug 3 fix needed |
| `generate_analysis.py` | 8-slide Part 1 analysis video | ✅ |
| `generate_education.py` | Educational Part 2 video | ✅ |
| `generate_articles.py` | 4 SEO articles → Jekyll _posts | ✅ |
| `generate_community_post.py` | YouTube community post 12:00 PM | ✅ |

### Kids Content Generation

| File | Role | Status |
|---|---|---|
| `generate_kids_video.py` | Kids story video — full + short + reel | ✅ — Bug 1+5 fix needed |

### Upload & Distribution

| File | Role | Status |
|---|---|---|
| `upload_youtube.py` | Trading channel YouTube upload | ✅ |
| `upload_kids_youtube.py` | Kids channel YouTube upload | ✅ |
| `upload_facebook.py` | Facebook upload (trading + kids with --meta-prefix) | ✅ trading / ❌ kids |
| `upload_instagram.py` | Instagram upload via Meta API | ⚠️ Partial |
| `upload_youtube_english.py` | English channel upload | 🔄 Phase 3 |

### Static Assets

| Path | Contents |
|---|---|
| `public/image/` | `zeno_happy.png`, `zeno_sad.png`, `zeno_greed.png`, `zeno_thinking.png` + HerooQuest character images |
| `public/music/` | `bgmusic1.mp3`, `bgmusic2.mp3`, `bgmusic3.mp3` — rotated by weekday |

---

## 9. AI Client Rule — NO EXCEPTIONS

All content generation uses `ai_client.py`. **Never call Groq/Gemini/Claude/OpenAI directly.**

> `generate_reel.py` and `generate_shorts.py` currently violate this rule — see Bug 4.

### AI Fallback Chain

```
Groq — llama-3.3-70b-versatile (primary — fastest, free)
    ↓ fails (quota exhausted — seen in kids log)
Google Gemini — gemini-2.0-flash (secondary)
    ↓ fails
Anthropic Claude — claude-haiku-4-5 (tertiary)
    ↓ fails
OpenAI — gpt-4o-mini (quaternary)
    ↓ all fail
Pre-generated templates in human_touch.py (always works — zero downtime)
```

### Image Generation Fallback Chain (for generate_kids_video.py)

```
Layer 1: Gemini imagen-3.0-generate-002 (best quality — needs paid plan)
    ↓ fails
Layer 2: Gemini 2.0 Flash image (check current model name at ai.google.dev)
    ↓ fails
Layer 3: Pollinations.AI — FREE, no API key needed ← RECOMMENDED ADD
    ↓ fails
Layer 4: HuggingFace Inference API v2 (updated endpoints)
    ↓ fails
Layer 5: DALL-E 3 (requires OpenAI billing)
    ↓ all fail
Layer 6: PIL text-on-gradient placeholder (always works)
```

### Import Pattern — All Generators

```python
from ai_client import ai, img_client
from human_touch import ht, seo
```

---

## 10. Trading Bot Architecture

### Overview

| Component | File | Role |
|---|---|---|
| AppScript v13.3 | Google Sheets bound | Scans Nifty200, writes WAITING candidates to AlertLog |
| Python Bot v13.4 | `trading_bot.py` | Monitors AlertLog, manages TSL, sends Telegram alerts |

**Status:** Paper trading. Dhan API integration → Phase 4.

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

### TSL Parameters (mode-aware)

```python
TSL_PARAMS = {
    "VCP": {"breakeven": 3.0, "lock1": 5.0, "trail": 8.0,  "atr_mult": 2.0, "gap_lock": 9.0},
    "MOM": {"breakeven": 2.5, "lock1": 4.5, "trail": 7.0,  "atr_mult": 1.8, "gap_lock": 8.0},
    "STD": {"breakeven": 2.0, "lock1": 4.0, "trail": 10.0, "atr_mult": 2.5, "gap_lock": 8.0},
}
```

Hard exit: Loss > 5% → immediate exit. Min hold: 2d swing / 3d positional.

---

## 11. Critical Upload Chain

### Evening ZENO Reel (8:30 PM)

```
generate_reel.py → output/reel_YYYYMMDD.mp4 + meta_YYYYMMDD.json
upload_youtube.py → writes youtube_video_id + public_video_url to meta
upload_facebook.py → uploads to FB Page, overwrites public_video_url
upload_instagram.py → reads public_video_url from meta → publishes
```

### Kids Video (daily)

```
generate_kids_video.py → output/kids_video_YYYY-MM-DD.mp4
                       → output/kids_short_YYYY-MM-DD.mp4
                       → output/kids_reel_YYYY-MM-DD.mp4
                       → output/kids_meta_YYYY-MM-DD.json
upload_kids_youtube.py → uploads full video + short
upload_facebook.py --meta-prefix kids → ❌ BROKEN (see Bug 2)
upload_instagram.py --meta-prefix kids → 🔄 pending
```

---

## 12. Environment Variables & Secrets

### Trading Channel

| Secret | Purpose | Status |
|---|---|---|
| `META_ACCESS_TOKEN` | Facebook + Instagram (trading page) | ✅ Auto-refreshed every 50 days |
| `META_APP_ID` | Facebook App ID | ✅ |
| `META_APP_SECRET` | Facebook App Secret | ✅ |
| `FACEBOOK_PAGE_ID` | Trading Facebook Page ID | ✅ |
| `FACEBOOK_GROUP_ID` | Trading Group ID | ✅ (broken — token scope) |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business numeric ID | ✅ |
| `YOUTUBE_CREDENTIALS` | YouTube OAuth JSON (Hindi channel) | ✅ |
| `YOUTUBE_CREDENTIALS_EN` | YouTube OAuth JSON (English channel) | ✅ |

### Kids Channel

| Secret | Purpose | Status |
|---|---|---|
| `YOUTUBE_CREDENTIALS_KIDS` | YouTube OAuth JSON (HerooQuest channel) | ✅ |
| `FACEBOOK_KIDS_PAGE_ID` | Kids Facebook Page numeric ID | ✅ (upload broken — see Bug 2) |
| `HF_TOKEN` | HuggingFace API token (image generation) | ✅ |

### AI Providers

| Secret | Priority | Status |
|---|---|---|
| `GROQ_API_KEY` | Primary | ✅ |
| `GEMINI_API_KEY` | Secondary | ✅ |
| `ANTHROPIC_API_KEY` | Tertiary | ✅ |
| `OPENAI_API_KEY` | Quaternary | ✅ (billing limit reached — see Bug 5) |

### Telegram

| Secret | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token |
| `TELEGRAM_CHAT_ID` | Free channel |
| `CHAT_ID_ADVANCE` | Advance (₹499/month) |
| `CHAT_ID_PREMIUM` | Premium bundle |

### Google / GCP

| Secret | Purpose |
|---|---|
| `GCP_SERVICE_ACCOUNT_JSON` | Search Console Indexing API + Google Sheets |
| `GH_TOKEN` | GitHub API token |

### Dhan Trading API (Phase 4 — not connected yet)

| Secret | Status |
|---|---|
| `DHAN_API_KEY`, `DHAN_API_SECRET`, `DHAN_CLIENT_ID`, `DHAN_PIN`, `DHAN_TOTP_KEY` | ✅ Added, not connected |

---

## 13. Known Issues & Fixes

### Facebook Group (Trading) ❌

Missing `publish_to_groups` scope. Fix: developers.facebook.com → App →
add scope → regenerate token → update `META_ACCESS_TOKEN` secret.

### Facebook Kids Page Upload ❌

See Bug 2 in Section 3 for full diagnosis and fix steps.

### Instagram ⚠️

Verify `INSTAGRAM_ACCOUNT_ID` is numeric:
`https://graph.facebook.com/me/accounts?access_token=TOKEN`

### YouTube Community Tab ⚠️

Requires 500+ subscribers. Below 500: post text saved to
`output/community_post_YYYYMMDD.txt` for manual posting — workflow does not crash.

### META Token Auto-Refresh ✅

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
| Banned phrase removal | Strips "Certainly!", "It's important to note", etc. |

---

## 15. Technical Standards

### The "Full Code" Rule

> AI assistants must always provide **complete file content** when modifying any file.
> Partial snippets or diffs are strictly prohibited.

### Log Suppression Block — Required at Top of ALL Video Generators

```python
import logging, warnings
logging.getLogger("moviepy").setLevel(logging.ERROR)
logging.getLogger("imageio").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")
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
| `gspread` + `oauth2client` | Latest | Google Sheets access |
| `pytz` | Latest | IST timezone |

### Voice Assignments

| Voice | Gender | Used For |
|---|---|---|
| `hi-IN-MadhurNeural` | Male | Short 2 — trade setups |
| `hi-IN-SwaraNeural` | Female | Short 3, ZENO Reel, Morning Reel, Analysis, Education |
| `en-US-JennyNeural` | Female | English channel |
| `en-US-GuyNeural` | Male | English Short 2 |

### Video Formats

| Content | Ratio | Platform |
|---|---|---|
| Analysis, Education, Kids Full Video | 16:9 | YouTube |
| All Shorts, Reels | 9:16 | YouTube Shorts / Instagram / Facebook Reels |

---

## 16. Reel Content Separation Rules

### Morning Reel (7:00 AM) — `generate_reel_morning.py`

- Energy: Upbeat, fresh, motivating — "start your day right"
- Topics by day: Mon=Market week ahead, Tue=Trading psychology, Wed=Chart pattern,
  Thu=Money mindset, Fri=Week review prep, Sat=Weekend learning, Sun=Investment planning
- Prompt must include: "MORNING BRIEF 7AM — pre-market motivation — NOT the evening ZENO reel"

### ZENO Evening Reel (8:30 PM) — `generate_reel.py`

- Energy: Wise, reflective, emotional — "what did we learn today"
- Topics: End-of-day market wisdom, ZENO character lesson, trading psychology
- Character: ZENO — animated wise kid teaching in Hinglish
- Prompt must include: "EVENING ZENO 8:30PM — end-of-day reflection — DIFFERENT from morning reel"

---

## 17. Full Data Flow

```
Market hours (Mon–Fri, 9:15 AM–3:30 PM IST)
└── main.yml (every 5 min)
    └── trading_bot.py v13.4 → signals → Telegram

AppScript v13.3 (Google Sheets) → WAITING candidates → AlertLog → T4 memory

7:00 AM daily → daily_reel.yml (morning)
    └── generate_reel_morning.py → upload chain ✅

7:30 AM / 9:30 AM → daily-videos.yml
    └── generate_analysis.py (Part 1) → generate_education.py (Part 2) ✅

10:00 AM / 11:30 AM → daily-articles.yml
    └── generate_articles.py → 4 articles → GitHub Pages + Google Indexing ✅

11:30 AM / 1:30 PM → daily-shorts.yml
    └── generate_shorts.py (Short 2 + 3) → generate_community_post.py ✅

8:30 PM → daily_reel.yml (evening)
    └── generate_reel.py (ZENO) → upload_youtube → upload_facebook → upload_instagram ✅/⚠️

Daily → daily-kids.yml
    └── generate_kids_video.py → upload_kids_youtube.py ✅
    └── upload_facebook.py --meta-prefix kids ❌ BROKEN
```

---

## 18. Disney 3D Reel Roadmap

| Phase | Tool | Status |
|---|---|---|
| 1 (Now) | PIL + MoviePy + ZENO PNG | ✅ Active |
| 2 | Gemini Veo API (free tier) | Hooks in ai_client.py |
| 3 | Stable Diffusion + AnimateDiff | Planned |
| 4 | Google Veo 2 / Sora (when free) | Planned |

---

## 19. Website & SEO

- **URL:** ai360trading.in — GitHub Pages (Jekyll, master branch `_posts/`)
- **Auto-publishing:** `daily-articles.yml` commits to `_posts/`
- **Google Indexing:** Via `GCP_SERVICE_ACCOUNT_JSON` — must ping after each article
- **SEO sitemap:** Must use `jekyll-sitemap` plugin (see Section 4 Fix 3)
- **robots.txt:** Must be fixed to stop blocking article URLs (see Section 4 Fix 1)
- **Revenue:** Google AdSense — USA/UK English readers = highest CPM

---

## 20. Social Media Links

| Platform | Handle |
|---|---|
| 🌐 Website | ai360trading.in |
| 📣 Telegram Free | @ai360trading |
| 📣 Telegram Advance | ai360trading_Advance — ₹499/month |
| 📣 Telegram Premium | ai360trading_Premium |
| ▶️ YouTube Trading | @ai360trading |
| ▶️ YouTube Kids | @HerooQuest (or similar) |
| 📸 Instagram | @ai360trading |
| 👥 Facebook Group | facebook.com/groups/ai360trading |
| 📘 Facebook Page | facebook.com/ai360trading |
| 🐦 Twitter/X | @ai360trading |

---

## 21. Phase Roadmap

### Phase 1 ✅ Complete
`ai_client.py`, `human_touch.py`, `token_refresh.py`, `generate_reel_morning.py`

### Phase 2 ✅ Complete (active bugs to fix)
All content generators upgraded. Kids channel added. 5 active bugs documented in Section 3.

### Phase 3 🔄 In Progress

| Item | Priority |
|---|---|
| Fix log spam (Bug 1) — all video generators | 🔴 High |
| Fix kids FB upload (Bug 2) | 🔴 High |
| Fix image generation sources (Bug 5) — add Pollinations.AI | 🔴 High |
| Fix reel duplicate content (Bug 3) | 🟡 Medium |
| Fix direct Groq calls (Bug 4) — migrate to ai_client | 🟡 Medium |
| Fix robots.txt — stop blocking articles | 🔴 High |
| Fix _config.yml — add jekyll-sitemap plugin | 🔴 High |
| Fix Facebook Group token scope | 🟡 Medium |
| Instagram verify end-to-end | 🟡 Medium |
| English channel: generate_english.py + upload_youtube_english.py | 🔵 Future |
| Instagram Kids upload | 🔵 Future |

### Phase 4 📋 Planned — Dhan Live Trading
After 30+ paper trades validated (win rate >35%). Secrets already added.
Live capital: ₹45,000 max (₹5k buffer). CE execution after Dhan API connected.

---

## 22. How to Test Everything

```bash
# Force test any workflow
GitHub Actions → select workflow → Run workflow → set content_mode

# Verify ai_client fallback
Look for: ✅ AI generated via groq  (or gemini/claude/openai if Groq down)

# Verify trading bot
Look for: [REGIME] Nifty CMP ₹XXXXX vs 20DMA ₹XXXXX → BULLISH/BEARISH

# Test kids video generation locally
GROQ_API_KEY=xxx GEMINI_API_KEY=xxx python generate_kids_video.py

# Verify Google Indexing API is working
Look in daily-articles.yml logs for: [INDEX] Submitted: /YYYY/MM/DD/title/

# Automation on/off switch
Google Sheet → AlertLog → cell T2 → YES = enabled
```

---

## 23. Files to Commit — Exact Content

### robots.txt (REPLACE CURRENT — fixes 4 blocked pages)

```
# ==========================================
# robots.txt for ai360trading.in
# Updated: April 2026
# ==========================================

User-agent: *
Allow: /

# Block only truly private/technical paths
Disallow: /assets/css/
Disallow: /assets/js/
Disallow: /cgi-bin/
Disallow: /_site/
Disallow: /admin/
Disallow: /private/
Disallow: /temp/
Disallow: /output/

# NOTE: Do NOT block /_posts/ /_includes/ /_layouts/ — these are source folders
# that are never publicly served. Blocking them confuses Googlebot on redirect chains.
# NOTE: Do NOT block /tags/ /categories/ /page/ — these are real indexed pages.

# Bot rate limiting only — not blocking
User-agent: dotbot
Crawl-delay: 20

User-agent: AhrefsBot
Crawl-delay: 20

User-agent: MJ12bot
Disallow: /

# Sitemap
Sitemap: https://ai360trading.in/sitemap.xml
```

### _config.yml plugins section (REPLACE PLUGINS BLOCK)

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
  - content_calendar.py
  - upload_youtube.py
  - upload_youtube_english.py
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

## 24. Immediate Action Checklist for Next Developer/AI

```
[ ] 1. Fix robots.txt — commit new version from Section 23 above
[ ] 2. Fix _config.yml — add jekyll-sitemap plugin, expand exclude list
[ ] 3. Fix Bug 1 — add log suppression block to ALL 6 video generators
[ ] 4. Fix Bug 5 — add Pollinations.AI as free image fallback (Layer 3)
[ ] 5. Fix Bug 2 — diagnose kids FB permission, wrap in try/except to not break workflow
[ ] 6. Fix Bug 3 — separate morning vs evening reel prompts and fallbacks
[ ] 7. Fix Bug 4 — migrate generate_reel.py + generate_shorts.py to ai_client
[ ] 8. Fix Gemini image model name (gemini-2.0-flash-exp-image-generation is 404)
[ ] 9. Verify Google Indexing API is submitting new article URLs after each publish
[ ] 10. Fix Facebook Group token — add publish_to_groups scope
[ ] 11. Verify Instagram upload end-to-end with correct INSTAGRAM_ACCOUNT_ID
[ ] 12. Phase 3: build generate_english.py + upload_youtube_english.py
[ ] 13. Phase 4: connect Dhan API after backtest validation
```

---

*Documentation maintained by AI360Trading automation.*
*Full audit: April 12, 2026 — Claude Sonnet 4.6*
*Channels: ai360trading (trading/finance) + HerooQuest (kids)*
*Phase 2 complete with 5 active bugs + 2 SEO issues documented above*
*This project runs automatically to support the owner's family. Every line of code matters.*
*Update this file whenever architecture, secrets, platforms, or bugs change.*
