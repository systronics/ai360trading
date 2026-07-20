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
| `trading_bot.py` | v15.27 (2026-07-20: full-system audit — removed dead ACCUM_ memory key that clean_mem never pruned; _read_atr_from_nifty200/_read_opt_tag_from_nifty200 switched from hardcoded row[28]/row[35] to header-name lookup (_find_nifty200_col) so a future inserted column can't silently corrupt SL/target/option math; stale "12-day"/BUY_PE comments fixed; v15.26 OWNER RULE — options are INTRADAY/1-2 day holds only; OPTION_MAX_TDAYS=2 replaces the base 12-trading-day rule for ALL option ledger rows (20% cap + expiry-week backstop unchanged); entry alerts carry _trade_style_lines — CASH/MTF vs cash vs accumulate + "Entry valid jab tak price SL ke upar" + TradingView chart line (DAILY/15m/WEEKLY); v15.25 option ledger follows the alert's rules; v15.24 unified strike grid + premium-aware option P/L; v15.23 full bug pack) |
| `entry_quality.py` | v1.0 (reversal veto + target room + composite ranking) |
| `option_intelligence.py` | v1.4 (2026-07-20: doc-only fix — stale 'BUY_PE' removed from action docstring, PE path confirmed dead since buy-side-only 2026-06-05; 2026-07-18: option alert wording = intraday/max 1-2 day hold, current-expiry rationale, 2-day exit; v1.3 strike table unified w/ appscript + est_option_leverage; v1.2 earnings via bm_data rows) |
| `institutional_edges.py` | v1.1 (2026-07-16: volume gate time-adjusted — partial-day reading ÷ expected session fraction, 1.5× bar unchanged) |
| `fetch_earnings.py` | v1.2 (2026-07-17: BSE long names → real NSE symbols via official EQUITY_L.csv (first-token keys were mostly dead); unmappable dropped; fail-open to old behavior; v1.1 atomic BotMemory write) |
| `fetch_bhavcopy.py` | v1.0 (Batch 4, Mon-Fri 20:00 IST) |
| `fetch_smallmidcap.py` | v1.5 (2026-07-18: easy-Hinglish digest — CASH-only rule, entry-valid line, TradingView DAILY line; v1.4 REAL 5d volume + SmallMidLive board + target floor ≥5% w/ honest R:R) |
| `fetch_rs.py` | v2.0 (2026-07-17: + TRUE ATR(14) feed into Nifty200 col AC — old formula was ONE day's high−low feeding all SL/targets; + NIFTYBEES→^NSEI benchmark freshness fallback; workflow moved to own `fetch-rs` concurrency group after `trading-bot` group froze RS 07-13→07-17) |
| `fetch_fii_dii.py` | v1.0 (real FII/DII flow → BotMemory MKT_* keys) |
| `fetch_index_meta.py` | v1.0 (2026-07-17: weekly Saturday — refreshes Nifty200 col AJ Options N50/YES/"" + col AK N200 YES/EX from NSE official lists; Telegram notice on drift; fail-open, never adds rows) |
| `appscript.gs` | v15.27 (LIVE, clasp-deployed 2026-07-20 20:26 IST: full-system audit — one-time header-position guard on the Nifty200 ATR (col 28) + Options-tag (col 35) reads in `_runScanner` (used by both the main scan and momentum scan); on header mismatch both fail SAFE to 0/null instead of trusting a shifted column, logs `[COLUMN-DRIFT]`; v15.26 OWNER RULE — option expiry = CURRENT month (≤5d rollover → next month, NEVER month+2; kills MIN_DAYS_BASE_ENTRY:40 that put a Jul signal on the dead Sep chain); option alert = intraday/1-2 din hold in easy Hinglish + entry-valid + TradingView lines; night-scan "Kaise trade kare" legend; v15.25 strike grid unified; deploy via `.\deploy_appscript.ps1`) |

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
| `human_touch.py` | v2.3 (2026-07-19: all hook libraries rewritten number-first for retention; no invented stats; {holiday}/{week} placeholders preserved) |
| `token_refresh.py` | v2.2 |
| `content_calendar.py` | v2.4 |
| `money_funnel.py` | v1.2 (2026-07-20: article_cta_html() now plugs a rotating calculator too — was the only funnel surface v1.1's tool_plug() rollout skipped, and articles are the site's highest-traffic surface; v1.1 TOOL_PAGES + tool_plug() daily calculator rotation in funnel_block/comment_text — video→website traffic loop; single source of truth for broker links in CONTENT — Zerodha/Dhan/Groww/CoinDCX) |
| `indian_holidays.py` | current (no version tag) |
| `health_watchdog.py` | v1.2 (2026-07-20: CHECK 7 — payment-page integrity; fetches the live membership/shop/starter-kit pages daily, alerts if the UPI ID or WhatsApp number ever differs from the pinned known-good value — detects a UPI-swap attack via repo compromise, since payments have no gateway yet; v1.1 GH_TOKEN PAT expiry early-warning) |

### Content Generators
| File | Version |
|---|---|
| `generate_education.py` | v1.3 (weekly dup-guard: skips if Week N already on channel) |
| `generate_reel.py` | v2.4 |
| `generate_reel_morning.py` | v2.5 |
| `generate_shorts.py` | v3.12 (2026-07-19: hook prompts prefer a REAL data number as first word; v3.11 retention pack: 20-25s payoff-at-end scripts + Ken Burns motion + 2s CTA) |
| `generate_articles.py` | current (2026-07-20: meta_description/schema_json now run through `clean_ai_title()` too — was only applied to the title, so a raw "SandP 500" LLM artifact could still ship in the meta tag/JSON-LD; also now calls `performance_stats.write_data_json()` alongside the existing article perf block; 2026-07-16 credibility pack: price carry-forward cache `_data/prices_cache.json` + honest Fear&Greed + filler-phrase ban + number-honesty rule 14 + internal-link dedup; 2026-07-13 phrase-cooldown + perf block) |
| `performance_stats.py` | v1.1 (2026-07-20: `write_data_json()` publishes the same honest ledger stats to `_data/performance.json` — Jekyll `site.data.performance` — so the membership page can show the real, live win-rate/ledger table, not just generated articles; fail-open carry-forward, same doctrine as prices_cache.json; v1.0 2026-07-13 — History ledger → article performance block) |
| `trending_keywords.py` | v1.1 (2026-07-20: whole-word seed filter in `_collect()` — YouTube autocomplete for seed "ipo" was returning "ipod"-class junk via shared prefix, not word-match; this had already published 2 live articles with "ipod" in the title/slug, both removed) |
| _(HerooQuest kids pipeline removed 2026-07-19 — generate_kids_video.py, kids_content_calendar.py, upload_kids_youtube.py, kids-daily.yml all deleted; channel retired as it cannot earn — see SESSION.md)_ |

### Upload & Distribution
| File | Version |
|---|---|
| `upload_youtube.py` | v2.3 |
| `upload_facebook.py` | v2.7 (2026-07-19 — kids branch removed; ZENO/morning/education/market paths unchanged) |

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
| **AppScript volume gates = time-fair PACE with EOD-identical bars** (v15.24: GATE 7 2.2×, BASE 1.4×, MOM/CASH 3.0×) — never revert to raw intraday readings, never change the bars without data | Volume_vs_Avg % is diff-form (+50 = 1.5×, owner screenshot v15.13); raw partial-day readings vs full-day averages structurally starved every intraday gate (the same bug fixed Python-side 07-16). Blank volume cells stay BLOCKED (volHasData) |
| **`_ENTRY_` memory keys = swing entries ONLY** (v15.23) — cash writes only `_CASH_` | The 3/day swing budget counter counts `_ENTRY_`; cash writing it too meant cash trades ate swing slots (v15.9 BUG-E's filter never worked) |
| **Earnings gate reads BotMemory ROWS via bm_data** (option_intelligence v1.2) — never revert to scanning the `_RUNTIME_MEM` string | fetch_earnings.py writes EARNINGS_* as sheet rows; the string scan matched nothing → CE suggestions possible the day before results |
| **ONE shared strike grid** (<100→1, <250→5, <500→10, <1000→20, <2000→50, ≥2000→100) in option_intelligence.strike_step + bot CE fallback + appscript _getStrikeInterval — change all three together or none | 2026-07-17: three divergent tables meant night vs entry alerts could name strikes on different ladders; the coarser grid is used because a coarse multiple always EXISTS when NSE's finer real spacing divides it (never alert a non-tradeable strike) |
| **MIN_SL_ATR_MULT = 0.75** — DMA-anchored SLs must leave ≥0.75×ATR room | BHARATFORG 07-16: DMA snap gave a 1.07% stop on a 2-4 week trade + fake RR 9.6 |
| **Owner's risk rule:** tight SL, target ≥5% *reachability-aware* (ATR%≥1.3 only), trail, option loss hard-capped 20%, option exit stock-anchored | v15.18 design; do NOT blindly hard-floor targets at 5% for low-vol names. Since bot v15.25 the PAPER LEDGER enforces the option rules too (20% est-loss cap + expiry-week backstop + v15.26 2-trading-day exit) — never revert options to generic stock time-stop/hard-loss monitoring |
| **OPTIONS = INTRADAY / MAX 1-2 DAY HOLDS, CURRENT EXPIRY** (owner rule 2026-07-18) — expiry picker: current month, ≤5d rollover → next month, NEVER month+2; swing/positional moves are traded in CASH/MTF, never as multi-week option holds; small/mid caps CASH only | Owner's own trading structure: liquidity lives in the current expiry (the old 40-day minimum put a 17-Jul signal on the dead Sep chain — no volume, ~20% spread); theta eats long option holds while the stock consolidates. Never restore MIN_DAYS-style far-expiry pickers or multi-week option hold wording |
| **Alert language = easy Hinglish + self-contained instructions** (v15.26): every entry/option alert states HOW to trade it (CASH/MTF/intraday), "Entry valid jab tak price SL ke upar hai", and which TradingView chart to check (DAILY swing / 15m cash+option timing / WEEKLY positional) | Owner + family act on these directly; a signal without "how" caused the MOTILALOFS Jul 1050 CE deviation (wrong strike, wrong expiry, wrong hold) |
| Empty AlertLog on a red/quiet day is CORRECT behavior, not a bug | NIFTY_MIN_PCT_BULLISH −0.30 + honest gates; 07-16 verified: 0 entries was right |
| **Fail-open for data feeds, fail-closed only where calibrated** | free-forever_self_repair: a dead feed must never kill the bot; the RSI exception is deliberately fail-CLOSED |
| **Nifty200 "ATR (14)" col = Python-fed true ATR (fetch_rs v2.0)** — never restore a GOOGLEFINANCE formula there | Audit 2026-07-17: old formula returned ONE day's high−low (ABB +60% off, IEX −26%) and fed every SL/target + option signal in both engines |
| **fetch_rs.yml keeps its OWN concurrency group** — never share `trading-bot` group | Sharing it froze RS 07-13→07-17 (queued runs kicked daily by the session loop); sheet writes are atomic, sharing was never needed |
| **Option signals gate on Nifty200 col AJ "Options"** (N50/YES/"" from NSE's official F&O file, fetch_index_meta weekly) — never gate on hardcoded stock lists | 2026-07-17: hardcoded F&O list still contained IRCTC (derivatives removed by SEBI purge), TATAMOTORS (demerged), ZOMATO (renamed) — impossible/dead option alerts |
| **Nifty200 col B = 18 NSE macro sectors; col AK N200 = YES/EX membership** — never revert to fine-grained custom labels | 62 of the old 100 labels held ONE stock → auto "rank 1 leader" bonuses, dead momentum-sector detection, biased "Strongest:" line |

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
| `health_watchdog.py`'s `EXPECTED_UPI`/`EXPECTED_WA` are PINNED values, not read from the live site | If the owner ever legitimately changes his UPI ID or WhatsApp number, update these constants in the SAME commit — otherwise the payment-integrity check (v1.2) will send a false "possible UPI-swap" alarm every day |

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
