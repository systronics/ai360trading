# SESSION.md — AI360Trading

---

## Last Updated: 2026-05-25 13:15

---

## Current Version Map

| File | Version | Last Changed |
|---|---|---|
| `trading_bot.py` | v15.3 | May 2026 |
| `appscript_v14.gs` | v15.9 | May 2026 |
| `ai_client.py` | v2.4 | May 2026 |
| `human_touch.py` | v2.2 | May 2026 |
| `generate_longterm.py` | v1.2 | May 2026 |
| `generate_education.py` | v1.1 | May 2026 |
| `generate_reel.py` | v2.1 | May 2026 |
| `generate_reel_morning.py` | v2.3 | May 2026 |
| `generate_shorts.py` | v3.3 | May 2026 |
| `generate_articles.py` | current | May 2026 |
| `generate_kids_video.py` | v2.3 | May 2026 |
| `refresh_cashwatchlist.py` | v1.0 | May 2026 |
| `fetch_holidays.py` | v1.0 | May 2026 |
| `token_refresh.py` | v2.1 | May 2026 |
| `upload_youtube.py` | v2.2 | May 2026 |
| `upload_facebook.py` | v2.6 | May 2026 |
| `content_calendar.py` | v2.2 | May 2026 |
| `indian_holidays.py` | current | March 2026 |
| `.internal-ops.md` | 2026-05-23 | May 2026 |
| `CLAUDE.md` | created | 2026-05-25 |
| `CHANGELOG.md` | created | 2026-05-25 |
| `SESSION.md` | created | 2026-05-25 |
| `smartsync.bat` | created | 2026-05-25 |
| `instructions.txt` | updated | 2026-05-25 |
| `upload_instagram.py` | v1.0 | 2026-05-25 |

---

## Last Session Summary

**2026-05-25:** Created SmartSync memory system — 4 new files added:
- `CLAUDE.md` — auto-read by Claude Code every session; contains all rules, versions, protocol
- `CHANGELOG.md` — version history log for all file changes
- `SESSION.md` — this file; persistent state across sessions
- `smartsync.bat` — run before every session to sync PC ↔ GitHub

System was fully operational at this point. No code changes made to any existing files.

---

## Pending Tasks — Priority Order

1. **Facebook Group posting** — Code ready in `upload_facebook.py` v2.6. Token needs `publish_to_groups` scope. Manual fix required (see Known Issues below).
2. **AdSense Publisher ID** — Replace `pub-XXXXXXXXXXXXXXXX` in `ads.txt` after AdSense approval.
3. **Phase 3** — Hindi→English dubbed audio track for global audience scale.

---

## Known Issues

| Issue | Status | Notes |
|---|---|---|
| Facebook Group posting | ❌ Blocked | Token missing `publish_to_groups` scope — manual fix in Graph API Explorer |
| AdSense Publisher ID | 📋 Pending | Replace pub-XXXXXXXXXXXXXXXX in ads.txt after approval |
| Dhan API (Phase 4) | 📋 Planned | Do NOT connect until explicitly approved |

---

## Starting Instruction for Any AI
*(Paste this at the start of any Claude.ai or AI chat session)*

```
You are helping me with my AI360Trading project.

OWNER: Amit Kumar, Haridwar. 6 family members depend on this system.
This is a fully automated trading signals + content income platform running on GitHub Actions.
Cost: ₹0/month. Paper trading only (Phase 1-3).

STRICT RULES you must follow:
1. NEVER provide partial code or snippets — always provide the complete file, every line.
2. NEVER assume file contents — I will paste the file for you to read before editing.
3. NEVER say something is fixed without showing the corrected content.
4. NEVER break working code — one broken workflow = zero income that day.
5. NEVER connect Dhan API or execute real trades — paper trading only.
6. Always use ai_client.py for AI calls (Groq→Gemini→Claude→OpenAI fallback).
7. Always use human_touch.py for content — never bypass it.
8. After every change: update .internal-ops.md + tell me the new version number.

CURRENT FILE VERSIONS:
- trading_bot.py → v15.3
- appscript_v14.gs → v15.8/v15.9
- ai_client.py → v2.4
- human_touch.py → v2.2
- generate_longterm.py → v1.2
- generate_education.py → v1.1
- generate_reel.py → v2.1
- generate_reel_morning.py → v2.3
- generate_shorts.py → v3.3
- generate_kids_video.py → v2.3
- refresh_cashwatchlist.py → v1.0
- token_refresh.py → v2.1
- upload_youtube.py → v2.2
- upload_facebook.py → v2.6
- content_calendar.py → v2.2

PENDING:
1. Facebook Group posting (needs publish_to_groups token scope)
2. Instagram full auto (depends on FB Group fix)

KNOWN ISSUES:
- FB Group posting blocked — token scope missing
- Instagram posting not yet live

Now please help me with: [describe your task here]
```

---

*Update this file at the end of every session.*
*Last sync: SmartSync or manual git pull — check before starting any session.*
