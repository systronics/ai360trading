# CLAUDE.md — AI360Trading Session Guide
> Auto-read by Claude Code every session. Follow every rule. No exceptions.

---

## OWNER
**Amit Kumar, Haridwar, Uttarakhand, India**
**6 family members depend on this system for their livelihood.**
Family is non-technical — cannot fix a broken system.
One broken file = zero income that day. Treat every edit as critical.

---

## PROJECT
**AI360Trading** — Fully automated trading signals + content income platform.
- ₹0/month cost forever (free tiers only)
- Paper trading only — Phase 1–3. Do NOT connect Dhan API or execute real trades.
- Everything runs on GitHub Actions — zero manual daily work required.

---

## FIRST THING EVERY SESSION

```
1. Run smartsync.bat   (syncs PC ↔ GitHub — ensures you have latest files)
2. Read CHANGELOG.md   (what changed last)
3. Read SESSION.md     (pending tasks, known issues, current versions)
4. Read the actual file before touching it — NEVER use memory or stale reads
```

---

## CURRENT FILE VERSIONS
*(Read from actual files — 2026-05-27)*

### Trading Engine
| File | Version |
|---|---|
| `trading_bot.py` | v15.9 |
| `appscript_v14.gs` | v15.16 (needs manual paste) |

### Long-Term Signals
| File | Version |
|---|---|
| `generate_longterm.py` | v1.6 |
| `refresh_cashwatchlist.py` | v1.3 |
| `fetch_holidays.py` | v1.2 |

### Core Infrastructure
| File | Version |
|---|---|
| `ai_client.py` | v2.4 |
| `human_touch.py` | v2.2 |
| `token_refresh.py` | v2.2 |
| `content_calendar.py` | v2.3 |
| `indian_holidays.py` | current (no version tag) |

### Content Generators
| File | Version |
|---|---|
| `generate_education.py` | v1.1 |
| `generate_reel.py` | v2.1 |
| `generate_reel_morning.py` | v2.3 |
| `generate_shorts.py` | v3.3 |
| `generate_articles.py` | current (no version tag) |
| `generate_kids_video.py` | v2.3 |

### Upload & Distribution
| File | Version |
|---|---|
| `upload_youtube.py` | v2.2 |
| `upload_facebook.py` | v2.6 |
| `upload_kids_youtube.py` | current |
| `upload_instagram.py` | current |

---

## STRICT RULES — NO EXCEPTIONS

### Rule A — Read Files Directly
- Claude Code reads files with the Read tool — no GitHub URLs needed.
- **ALWAYS** read the actual file before touching it. Never use session memory or previous reads.
- **NEVER** assume what a file contains. Read fresh, then edit.

### Rule B — Only State What You Can See
- **NEVER** give line numbers unless you can show the exact text proving it.
- **NEVER** say "yes it is fixed" without showing the actual content.
- When the owner corrects you — accept it, re-read, do not defend wrong answers.

### Rule C — Always Provide Complete Files
- **NEVER** provide partial code, snippets, or diffs.
- **ALWAYS** provide the complete file from top to bottom — every line.
- Even a 1-line fix requires the full file to be provided.

### Rule D — Verify Before Claiming Fixed
- **NEVER** mark a bug as fixed without reading the file and showing the corrected lines.
- **NEVER** claim a function exists without showing the read code.

### Rule E — Ask, Don't Assume
- If something is unclear — ask one specific question.
- Never fill gaps with assumptions. Wrong assumptions waste the owner's time.

### Rule F — Update .internal-ops.md After Every Change
- Every file change must be documented in `.internal-ops.md` immediately.
- This is the master system doc — if it's not there, the next AI won't know about it.
- Also update CHANGELOG.md and SESSION.md at end of every session.

### Rule G — Never Break What Works
- Do NOT break any working workflow. A broken workflow = zero income that day.
- Do NOT add paid services without explicit approval.
- Do NOT connect Dhan API or execute real trades (Phase 4 only — not yet).
- **Always use `human_touch.py`** — never bypass it for content generation.

---

## END OF EVERY SESSION

Before ending, update SESSION.md with:
- What was done this session
- Current version of every file changed
- Any new pending tasks discovered
- Any new known issues

Then run:
```
git add -A
git commit -m "Session update: [brief description]"
git push
```

---

## KEY SYSTEM FACTS

- **AI Fallback chain:** Groq → Gemini → Claude → OpenAI → Templates (never call AI APIs directly — always use `ai_client.py`)
- **Content mode:** auto-detected by `indian_holidays.py` — market / weekend / holiday
- **Sheet:** `Ai360tradingAlgo` (Google Sheets)
- **T2 cell = automation on/off** (AlertLog col T row 2 — YES = enabled)
- **Paper trading only** — `CONFIG.BROKER_MODE = "PAPER"` in AppScript
- **Phase 3 pending:** Facebook Group posting (needs `publish_to_groups` token scope), Instagram full auto
- **Phase 4 planned:** Dhan API live trading — do NOT implement until explicitly asked

---

*See `.internal-ops.md` for full system documentation.*
*See `SESSION.md` for current task list and known issues.*
