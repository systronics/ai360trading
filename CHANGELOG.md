# CHANGELOG — AI360Trading

---

## 2026-05-25 13:05
### Changed
- `instructions.txt` — Added upload_instagram.py v1.0 to current file versions list

---

## 2026-05-25 13:00
### Added
- `upload_instagram.py` → v1.0 — Recreated. Standalone Instagram Reels uploader. Supports --type reel/morning/short2/short3. Uses same 4-step resumable upload protocol as upload_facebook.py v2.6 and generate_shorts.py v3.3. Gets page token same way. Builds mode-aware captions (market/weekend/holiday). Saves ig_post_id to meta JSON on success. Saves caption to instagram_fallback_YYYYMMDD.txt on failure for manual posting.

---

## 2026-05-25 12:40
### Fixed
- `token_refresh.yml` — Added CHAT_ID_BASIC to env vars. Token refresh success/failure alerts now also reach the Basic channel which Amit ji monitors.

---

## 2026-05-25 12:35
### Fixed
- `longterm_signals.yml` — Replaced manual pip install with `pip install -r requirements.txt` to prevent silent failures if generate_longterm.py uses any package not in the manual list.
- `refresh_watchlists.yml` — Same fix applied to both jobs (refresh-cashwatchlist + refresh-longterm-watchlist).

---

## 2026-05-25 12:30
### Fixed
- `.gitignore` — Removed stale entries: `!generate_analysis.py` (file doesn't exist), `!generate_community_post.py` (file doesn't exist), `!SYSTEM.md` (renamed to .internal-ops.md). Added missing files that exist: `!generate_longterm.py`, `!refresh_cashwatchlist.py`, `!fetch_holidays.py`. Updated `!SYSTEM.md` → `!.internal-ops.md`.

---

## 2026-05-25 12:25
### Fixed
- `daily_reel.yml` — FACEBOOK_GROUP_ID was missing from upload_facebook.py step. Evening ZENO reel will now post to Group once token scope is fixed.

---

## 2026-05-25 12:20
### Fixed
- `daily-morning-reel.yml` — Two bugs fixed: (1) Content mode detection broken — same `python indian_holidays.py` issue as daily-videos, replaced with inline Python snippet; (2) FACEBOOK_GROUP_ID missing from Post to Facebook step — group will now receive morning reel when token is fixed.

---

## 2026-05-25 12:15
### Fixed
- `daily-videos.yml` — Content mode detection was broken: `python indian_holidays.py` only printed to stdout, never wrote CONTENT_MODE to GITHUB_ENV. Replaced with proper inline Python snippet that writes to GITHUB_ENV (same pattern as all other working workflows).

---

## 2026-05-25 12:00
### Fixed
- `appscript_v14.gs` — Header comment corrected: v15.8 → v15.9 (code was already v15.9, only comment was stale)

---

## 2026-05-25 11:45
### Changed
- `instructions.txt` — File versions updated to exact values read from actual files: trading_bot.py v15.1→v15.3, appscript v15.6→v15.8, added ai_client/human_touch/longterm/refresh/fetch/token/content_calendar/indian_holidays, generate_kids_video latest→v2.3, upload_youtube latest→v2.2, upload_kids_youtube latest→v2.3

---

## 2026-05-25 11:30
### Changed
- `instructions.txt` — Replaced with universal AI instructions: environment detection (PC vs Online), URL fallbacks for online AI, rules, pending tasks, file versions

---

## 2026-05-25 11:00
### Added
- `CLAUDE.md` — Claude Code session guide: owner info, file versions, strict rules, session protocol
- `CHANGELOG.md` — This file: version history for all project files
- `SESSION.md` — Persistent session state: version map, pending tasks, known issues, AI start prompt
- `smartsync.bat` — Windows batch file: syncs PC ↔ GitHub bidirectionally before every session

### Current File Versions (baseline snapshot — read from actual files)
- `trading_bot.py` → v15.3
- `appscript_v14.gs` → v15.8 in file header / v15.9 per .internal-ops.md
- `ai_client.py` → v2.4
- `human_touch.py` → v2.2
- `generate_longterm.py` → v1.2
- `generate_education.py` → v1.1
- `generate_reel.py` → v2.1
- `generate_reel_morning.py` → v2.3
- `generate_shorts.py` → v3.3
- `generate_articles.py` → current (no version tag)
- `generate_kids_video.py` → v2.3
- `refresh_cashwatchlist.py` → v1.0
- `fetch_holidays.py` → v1.0
- `token_refresh.py` → v2.1
- `upload_youtube.py` → v2.2
- `upload_facebook.py` → v2.6
- `content_calendar.py` → v2.2
- `indian_holidays.py` → current (no version tag)
- `.internal-ops.md` → 2026-05-23 (last updated)

---

<!-- Add new entries above this line. Most recent entry always at top. -->
<!-- Format:
## YYYY-MM-DD HH:MM
### Changed
- filename.py → vX.X — what changed
### Added
- new file — what it does
### Fixed
- what bug was fixed
-->
