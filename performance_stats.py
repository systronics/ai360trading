# ══════════════════════════════════════════════════════════════════════════════
# performance_stats.py — v1.1 (2026-07-20)
# ══════════════════════════════════════════════════════════════════════════════
# v1.1: write_data_json() dumps the same honest ledger stats to _data/
#   performance.json (Jekyll auto-loads _data/*.json as site.data.performance)
#   so static pages — the membership page, not just generated articles — can
#   show the real, live win-rate/ledger table instead of a hardcoded number.
# Reads the CLOSED-trade ledger (History tab of Ai360tradingAlgo) and turns it
# into an "our real signal performance" block for website articles.
#
# WHY: hundreds of aggregator sites chase the same market keywords with the
# same rewritten news. Our own live paper-trading ledger — wins AND losses,
# published honestly — is original data none of them have (E-E-A-T + trust).
#
# DESIGN RULES (same as everything else in this repo):
#   • FAIL-OPEN everywhere: any error → get_performance_summary() returns None
#     and article_perf_html() returns "" — an article can NEVER break on this.
#   • Read-only: opens the sheet, reads History, writes NOTHING.
#   • ₹0: uses the same GCP service account the trading bot already uses.
#   • One sheet read per run (module-level cache) — generate_articles produces
#     2 articles per run; both share the same fetch.
#
# History columns (0-based; appended by trading_bot._exit_trade):
#   0 Symbol | 1 Entry Date | 2 Entry | 3 Exit Date | 4 Exit | 5 P/L % |
#   6 Result (WIN ✅/LOSS ❌) | 7 Strategy | 8 Reason | 9 Type | ... | 16 P/L ₹
# ══════════════════════════════════════════════════════════════════════════════

import os
import json

SHEET_NAME = "Ai360tradingAlgo"

_cache = {"loaded": False, "stats": None}


def _open_history():
    """Connect read-only to the History tab. Raises on failure (caller catches)."""
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        with open("service_account.json") as f:
            raw = f.read().strip()
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    return gspread.authorize(creds).open(SHEET_NAME).worksheet("History")


def _to_float(s):
    try:
        return float(str(s).replace("%", "").replace(",", "").replace("₹", "").strip())
    except Exception:
        return None


def get_performance_summary(max_recent=3):
    """
    Returns a dict of honest ledger stats, or None if anything fails:
      total, wins, losses, win_rate, net_pnl_rs, avg_win_pct, avg_loss_pct,
      best (sym, pct), worst (sym, pct), recent [(sym, exit_date, pct, is_win)]
    Cached for the life of the process (one sheet read per run).
    """
    if _cache["loaded"]:
        return _cache["stats"]
    _cache["loaded"] = True
    try:
        rows = _open_history().get_all_values()[1:]
        wins, losses = [], []
        net_rs = 0.0
        closed = []
        for r in rows:
            while len(r) < 17:
                r.append("")
            sym = str(r[0]).replace("NSE:", "").strip()
            result = str(r[6]).upper()
            pct = _to_float(r[5])
            if not sym or pct is None or ("WIN" not in result and "LOSS" not in result):
                continue
            is_win = "WIN" in result
            (wins if is_win else losses).append(pct)
            rs = _to_float(r[16])
            if rs is not None:
                net_rs += rs
            closed.append((sym, str(r[3]).strip(), pct, is_win))

        total = len(closed)
        if total == 0:
            _cache["stats"] = None
            return None

        by_pct = sorted(closed, key=lambda t: t[2])
        stats = {
            "total":        total,
            "wins":         len(wins),
            "losses":       len(losses),
            "win_rate":     round(len(wins) / total * 100),
            "net_pnl_rs":   round(net_rs),
            "avg_win_pct":  round(sum(wins) / len(wins), 1) if wins else 0.0,
            "avg_loss_pct": round(sum(losses) / len(losses), 1) if losses else 0.0,
            "best":         (by_pct[-1][0], by_pct[-1][2]),
            "worst":        (by_pct[0][0], by_pct[0][2]),
            # History is append-only → last rows = most recently closed
            "recent":       closed[-max_recent:][::-1],
        }
        _cache["stats"] = stats
        return stats
    except Exception as e:
        print(f"[PERF] History read skipped ({e}) — articles continue without the block")
        _cache["stats"] = None
        return None


def article_perf_html(as_of_display):
    """
    The article block. Returns "" on any problem (fail-open).
    Honest by design: shows losses, avg loser and the worst trade — transparency
    IS the differentiator. Placed right before the conversion CTA (proof → ask).
    """
    try:
        s = get_performance_summary()
        if not s:
            return ""
        recent_rows = "".join(
            '<tr>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #e2e8f0"><b>{sym}</b></td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #e2e8f0">{exit_dt}</td>'
            f'<td style="padding:6px 10px;border-bottom:1px solid #e2e8f0;'
            f'color:{"#059669" if is_win else "#dc2626"};font-weight:700">'
            f'{pct:+.2f}% {"✅" if is_win else "❌"}</td>'
            '</tr>'
            for sym, exit_dt, pct, is_win in s["recent"]
        )
        net = s["net_pnl_rs"]
        return (
            '\n\n<div style="border:2px solid #16a34a;border-radius:14px;'
            'padding:18px 20px;margin:32px 0;background:#f0fdf4">\n'
            '<h3 style="margin:0 0 8px">📊 Our Real Signal Performance — Verified Ledger</h3>\n'
            f'<p style="margin:6px 0;font-size:0.92em;color:#374151">Every closed trade from our '
            f'automated system\'s live paper-trading ledger — wins <b>and</b> losses, as of {as_of_display}:</p>\n'
            f'<p style="margin:10px 0;font-size:1.02em"><b>{s["total"]} closed trades · '
            f'{s["win_rate"]}% win rate · net {"+" if net >= 0 else "−"}₹{abs(net):,}</b><br>'
            f'Average winner <b style="color:#059669">+{s["avg_win_pct"]}%</b> · '
            f'average loser <b style="color:#dc2626">{s["avg_loss_pct"]}%</b> · '
            f'best {s["best"][0]} {s["best"][1]:+.1f}% · worst {s["worst"][0]} {s["worst"][1]:+.1f}%</p>\n'
            '<table style="border-collapse:collapse;font-size:0.9em;margin:8px 0">'
            '<tr><th style="text-align:left;padding:6px 10px;border-bottom:2px solid #16a34a">Latest trades</th>'
            '<th style="text-align:left;padding:6px 10px;border-bottom:2px solid #16a34a">Closed</th>'
            '<th style="text-align:left;padding:6px 10px;border-bottom:2px solid #16a34a">Result</th></tr>'
            f'{recent_rows}</table>\n'
            '<p style="margin:6px 0;font-size:0.85em;color:#555">Published for transparency — losses included. '
            'Paper trading (no real money). See live setups on the '
            '<a href="/swing-dashboard/">signal dashboard</a>. '
            '<i>Educational only — not SEBI-registered advice.</i></p>\n'
            '</div>\n'
        )
    except Exception as e:
        print(f"[PERF] block build skipped ({e})")
        return ""


def write_data_json(as_of_display, path="_data/performance.json"):
    """
    Dumps get_performance_summary() to a Jekyll _data JSON file so static
    pages (membership.md) can render the real ledger via site.data.performance
    — no Python execution at page-render time. FAIL-OPEN: if the sheet read
    fails, the OLD file is left untouched (same carry-forward doctrine as
    _data/prices_cache.json) rather than wiping a working page's numbers.
    Returns True if it wrote a fresh file, False if left untouched.
    """
    try:
        s = get_performance_summary()
        if not s:
            print("[PERF] no stats — leaving existing performance.json untouched")
            return False
        out = {
            "as_of":        as_of_display,
            "total":        s["total"],
            "wins":         s["wins"],
            "losses":       s["losses"],
            "win_rate":     s["win_rate"],
            "net_pnl_rs":   s["net_pnl_rs"],
            "avg_win_pct":  s["avg_win_pct"],
            "avg_loss_pct": s["avg_loss_pct"],
            "best":         {"sym": s["best"][0],  "pct": s["best"][1]},
            "worst":        {"sym": s["worst"][0], "pct": s["worst"][1]},
            "recent": [
                {"sym": sym, "exit_date": exit_dt, "pct": pct, "is_win": is_win}
                for sym, exit_dt, pct, is_win in s["recent"]
            ],
        }
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"[PERF] wrote {path}")
        return True
    except Exception as e:
        print(f"[PERF] write_data_json skipped ({e}) — leaving existing file untouched")
        return False


if __name__ == "__main__":
    # Read-only self-test against the live sheet (writes nothing, sends nothing)
    s = get_performance_summary()
    print(json.dumps(s, ensure_ascii=False, indent=2, default=str) if s else "No stats (fail-open OK)")
    html = article_perf_html("13 July 2026")
    print(f"\nHTML block: {len(html)} chars")
    print(html)
