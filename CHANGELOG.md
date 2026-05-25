# CHANGELOG — AI360Trading

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
