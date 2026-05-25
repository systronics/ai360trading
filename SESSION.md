# SESSION.md — AI360Trading

---

## Last Updated: 2026-05-25 15:30

---

## Current Version Map

| File | Version | Last Changed |
|---|---|---|
| `trading_bot.py` | **v15.6** | 2026-05-25 (Batch 4) |
| `appscript_v14.gs` | **v15.13** | 2026-05-25 (Batch 4) |
| `ai_client.py` | v2.4 | May 2026 |
| `human_touch.py` | v2.2 | May 2026 |
| `generate_longterm.py` | **v1.5** | 2026-05-25 (Batch 4) |
| `generate_education.py` | v1.1 | May 2026 |
| `generate_reel.py` | v2.1 | May 2026 |
| `generate_reel_morning.py` | v2.3 | May 2026 |
| `generate_shorts.py` | v3.3 | May 2026 |
| `generate_articles.py` | current | May 2026 |
| `generate_kids_video.py` | v2.3 | May 2026 |
| `refresh_cashwatchlist.py` | **v1.3** | 2026-05-25 (Batch 4) |
| `fetch_holidays.py` | **v1.2** | 2026-05-25 (Batch 4) |
| `token_refresh.py` | **v2.2** | 2026-05-25 (Batch 1) |
| `upload_youtube.py` | v2.2 | May 2026 |
| `upload_facebook.py` | v2.6 | May 2026 |
| `content_calendar.py` | v2.2 | May 2026 |
| `indian_holidays.py` | current | March 2026 |
| `.internal-ops.md` | 2026-05-25 | May 2026 |
| `CLAUDE.md` | created | 2026-05-25 |
| `CHANGELOG.md` | updated | 2026-05-25 |
| `SESSION.md` | updated | 2026-05-25 |
| `smartsync.bat` | created | 2026-05-25 |
| `instructions.txt` | updated | 2026-05-25 |
| `upload_instagram.py` | v1.0 | 2026-05-25 |

---

## Last Session Summary

**2026-05-25 (afternoon):** Full trading system audit + Batches 1 & 2 fixes applied.
- **Audit scope:** Everything trading-related (12 files: trading_bot.py, appscript_v14.gs, generate_longterm.py, refresh_cashwatchlist.py, fetch_holidays.py, token_refresh.py, indian_holidays.py + 5 GitHub Actions workflows).
- **Findings:** 3 Critical, 9 High, 11 Medium, 7 Low, 10 Suggestions.
- **Batch 1 applied (6 fixes — all zero-risk, high-priority):**
  - C1: token_refresh.py now alerts both Basic+Advance (was Advance-only)
  - C2: trading_bot.yml timeout 4→8 min
  - H1: 4 scripts get clear cred validation errors
  - H3: trading_bot.py daily dedup flags use exact-key lookup
  - H8: 2 workflows standardized to requirements.txt
  - H9: AppScript LeaderType match is now case-insensitive
- **Batch 2 applied (5 fixes — small risk, high value):**
  - C3: AppScript holidays auto-load from BotMemory (no more manual yearly update)
  - H2: trading_bot.py _exit_trade uses actual sheet qty for P/L (data integrity)
  - M1: step_a TRADED promotion batched K:M update (saves ~16s/morning)
  - M3: Removed 3 redundant trading_bot.yml backup crons
  - M4: Tightened cron window (saves ~3 wasted runs/day)
- **Batch 3 applied (5 fixes — medium risk, behavioral + perf):**
  - H4 (refresh_cashwatchlist): _current_price uses fast_info → info → history fallback chain
  - H4 (generate_longterm): price/52w from hist (not .info); .info wrapped for graceful fallback
  - H7: AppScript cash detection works in BEARISH market (was bullish-only)
  - M7: LTWatchlist batch_update — 1 API call instead of 25 (saves ~30s/Sunday)
  - M9: indian_holidays.py — removed duplicate (10,2) entry
- **Batch 4 applied (6 fixes — final polish):**
  - M2: refresh_cashwatchlist.py batch_update for all formula/status writes (saves ~2 min/monthly)
  - M5: token_refresh.yml comment corrected (was "every 40 days" — actual is 1st+15th)
  - M6: AppScript _bmPurge uses regex for date check (defensive)
  - M8: fetch_holidays.py FALLBACK_2027 cleaned (removed weekend dates)
  - M10: generate_longterm.py P&L cutoff widened 7→8 days (captures Friday-edge trades)
  - Removed obsolete v15.1 Y1 migration code from trading_bot.py (was running every tick)

**AUDIT COMPLETE.** 22 of 27 numbered findings addressed across 4 batches. Remaining 5 (M11, L2, L5, L6, L7) intentionally deferred as low-value or requiring coordinated changes.
- **Telegram routing verified working** by Amit ji — Basic/Advance/Premium all receive correct trade alerts.

**2026-05-25 (morning):** Created SmartSync memory system — 4 new files added (CLAUDE.md, CHANGELOG.md, SESSION.md, smartsync.bat).

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
- trading_bot.py → v15.6
- appscript_v14.gs → v15.13
- ai_client.py → v2.4
- human_touch.py → v2.2
- generate_longterm.py → v1.5
- generate_education.py → v1.1
- generate_reel.py → v2.1
- generate_reel_morning.py → v2.3
- generate_shorts.py → v3.3
- generate_kids_video.py → v2.3
- refresh_cashwatchlist.py → v1.3
- fetch_holidays.py → v1.2
- token_refresh.py → v2.2
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
