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
*(Read from actual files — 2026-07-14 full audit)*

### Trading Engine
| File | Version |
|---|---|
| `trading_bot.py` | v15.21 (2026-07-16: time-fair volume gate — Filter 8 gates on volume PACE via IST clock; v15.20 calibrated RSI hot-leader exception; v15.19 Nifty%/VIX feeds revived) |
| `entry_quality.py` | v1.0 (reversal veto + target room + composite ranking) |
| `option_intelligence.py` | v1.1 (2026-07-15: bearish → SKIP; old PE path contradicted buy-side-only longs) |
| `institutional_edges.py` | v1.1 (2026-07-16: volume gate time-adjusted — partial-day reading ÷ expected session fraction, 1.5× bar unchanged) |
| `fetch_earnings.py` | v1.0 (Batch 3, daily 18:30 IST) |
| `fetch_bhavcopy.py` | v1.0 (Batch 4, Mon-Fri 20:00 IST) |
| `fetch_smallmidcap.py` | v1.4 (Mon-Fri 20:30 IST — REAL 5d volume + SmallMidLive board + target floor ≥5% w/ honest R:R) |
| `fetch_rs.py` | v1.0 (yfinance RS repair feed — keeps Nifty200 RS col alive; GOOGLEFINANCE #N/A killed all scores once) |
| `fetch_fii_dii.py` | v1.0 (real FII/DII flow → BotMemory MKT_* keys) |
| `appscript.gs` | v15.22 (LIVE in editor, clasp-deployed 2026-07-16 21:59 IST: SL noise floor MIN_SL_ATR_MULT 0.75 + confirm-at-open guard on night option alerts; v15.21 honest premarket regime message + CONFIG.VERSION stamps; v15.20 option-alert safety pack; deploy via `.\deploy_appscript.ps1`) |

### Long-Term Signals
| File | Version |
|---|---|
| `generate_longterm.py` | v1.7 |
| `refresh_cashwatchlist.py` | v1.3 |
| `fetch_holidays.py` | v1.3 |

### Core Infrastructure
| File | Version |
|---|---|
| `ai_client.py` | v2.5 |
| `human_touch.py` | v2.2 |
| `token_refresh.py` | v2.2 |
| `content_calendar.py` | v2.4 |
| `money_funnel.py` | current (single source of truth for broker links in CONTENT — Zerodha/Dhan/Groww/CoinDCX) |
| `indian_holidays.py` | current (no version tag) |

### Content Generators
| File | Version |
|---|---|
| `generate_education.py` | v1.3 (weekly dup-guard: skips if Week N already on channel) |
| `generate_reel.py` | v2.4 |
| `generate_reel_morning.py` | v2.5 |
| `generate_shorts.py` | v3.11 (2026-07-14 retention pack: 20-25s payoff-at-end scripts + Ken Burns motion + 2s CTA) |
| `generate_articles.py` | current (no version tag; 2026-07-13 phrase-cooldown + perf block) |
| `performance_stats.py` | v1.0 (2026-07-13 — History ledger → article performance block, fail-open) |
| `generate_kids_video.py` | v3.0 (2026-07-13 — story-seed grounding + cold open + completeness retry + CTA/narrator variety) |
| `kids_content_calendar.py` | v2.0 (2026-07-13 — 128 seeded classic stories + no-repeat 128-day scheduler) |

### Upload & Distribution
| File | Version |
|---|---|
| `upload_youtube.py` | v2.3 |
| `upload_facebook.py` | v2.6 |
| `upload_kids_youtube.py` | v2.6 (2026-07-13 — Devanagari-first SEO titles: {hi} | {en} | Hindi Kahaniya | Moral Stories) |

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

## 🔒 NEVER CHANGE — OWNER-VALIDATED DECISIONS
*(Each line exists because of real money, real data, or an explicit owner decision. Do NOT "improve" these. If a change seems needed, present evidence and get owner approval FIRST. Full history in `.internal-ops.md` + memory.)*

### Trading — hard rules
| Rule | Why (evidence) |
|---|---|
| `BROKER_MODE = "PAPER"` — never connect Dhan API / place real orders | Phase 4 only, owner must explicitly start it |
| **Buy-side only** — never build/propose shorting or PE buying | Owner DECLINED sell-side 2026-06-05; bearish regime → options SKIP (option_intelligence v1.1) |
| **RS ≥ 5 gate** (bot Filter 7 + appscript GATE 3) — never lower | Data-validated 2026-07-15: ALL 6 target winners pass, 2/5 losers correctly blocked |
| **RSI hot-leader exception exactly as calibrated** — bullish + RSI 65–75 + stock up on day = allowed; >75 hard block; fail-CLOSED without day data | 13-trade study 2026-07-15: no loser ever entered overbought; NYKAA-class winners were being refused. Don't revert to hard-65, don't raise above 75 |
| **VOL gate = 1.5× PACE** (time-fair since v15.21/v1.1) — the 1.5× bar stays | Bar is deliberate (institutional footprint); only the measurement was made time-fair. Reversal-risk/ranking uses RAW relvol on purpose |
| **MIN_SL_ATR_MULT = 0.75** — DMA-anchored SLs must leave ≥0.75×ATR room | BHARATFORG 07-16: DMA snap gave a 1.07% stop on a 2-4 week trade + fake RR 9.6 |
| **Owner's risk rule:** tight SL, target ≥5% *reachability-aware* (ATR%≥1.3 only), trail, option loss hard-capped 20%, option exit stock-anchored | v15.18 design; do NOT blindly hard-floor targets at 5% for low-vol names |
| Empty AlertLog on a red/quiet day is CORRECT behavior, not a bug | NIFTY_MIN_PCT_BULLISH −0.30 + honest gates; 07-16 verified: 0 entries was right |
| **Fail-open for data feeds, fail-closed only where calibrated** | free-forever_self_repair: a dead feed must never kill the bot; the RSI exception is deliberately fail-CLOSED |

### Money & platform
| Rule | Why |
|---|---|
| **₹0/month forever** — no paid services without explicit owner approval | 6-family-member livelihood; free tiers only |
| **`human_touch.py` on ALL content** — never bypass | Content authenticity pipeline |
| **AI use is DISCLOSED, never evaded** — never build AI-detection evasion | FB flag 2026-06-07 was informational; disclosure + quality is the compliant path |
| **`ai_client.py` for every AI call** (Groq → Gemini → Claude → OpenAI → Templates) | Never call AI APIs directly |
| **`money_funnel.py`** = single source of broker/referral links in content | |
| Repo stays PUBLIC (GitHub Actions unlimited); `.internal-ops.md`/`SESSION.md`/`CHANGELOG.md` stay PC-LOCAL (gitignored) | Owner decision 2026-05-30 |

### Operational invariants
| Rule | Why |
|---|---|
| **Owner trades MANUALLY with real money off the Telegram alerts** | Alert quality = family income. Test + verify BEFORE every deploy; subscriber-facing wording must be honest (no fake VIX, no false-certain regime verdicts, no stale version stamps) |
| **AppScript deploys via `.\deploy_appscript.ps1` (clasp)** — never manual paste; bump `CONFIG.VERSION` every release | It is the single source for all message version stamps |
| `.bat`/`.cmd`/`.ps1` files stay **CRLF** (`.gitattributes` enforces) | smartsync.bat was silently broken for months by LF endings |
| NSE holidays only from the **official NSE list** — never guess/hardcode from memory | 2026-05-27 full outage from a wrong hardcoded list |
| Never ask the owner for chart screenshots for calibration — use yfinance | Owner directive 2026-07-15; charts only when HE offers them |
| T2 cell (AlertLog col T row 2) = automation master switch | YES = enabled |

---

## END OF EVERY SESSION

Before ending, update SESSION.md with:
- What was done this session
- Current version of every file changed
- Any new pending tasks discovered
- Any new known issues

Also update, every time without exception:
- `.internal-ops.md` — dated entry: what changed, WHY, what was verified, what was deliberately NOT changed
- `CHANGELOG.md` — same change in subscriber/owner language
- The CURRENT FILE VERSIONS table in this file (CLAUDE.md)
- The 🔒 NEVER CHANGE section in this file — add any new owner-validated decision made this session
- Memory (`MEMORY.md` + topic file) — so the next session starts already knowing

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
