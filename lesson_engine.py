"""
lesson_engine.py — evergreen LESSON videos for serious traders (v1.0, 2026-10-18)
==================================================================================
Builds a 2-4 minute landscape (1280x720) lesson video from REAL data with free tools only:
  * topic from lesson_bank.py (evergreen bank + balanced picker)
  * real historical charts from yfinance, animated with Pillow (lesson_visuals.py)
  * narration via edge_tts (free), one clip per scene so picture and voice stay in sync
  * lesson_bank.quality_gate() must pass (real number, a Rule line, an honest limit, no hype)

THIS VERSION (v1.0) IS A SAMPLE BUILDER ONLY. It renders to a local folder and NEVER uploads.
Posting is a separate, owner-approved step (nothing here touches YouTube/Facebook/Telegram).

Usage:  python lesson_engine.py --sample [--out DIR] [--no-render]
"""

import os, sys, asyncio, argparse, random
from pathlib import Path
from datetime import datetime

import numpy as np

import lesson_bank as bank
import lesson_visuals as lv

# A fixed, liquid, well-known universe for the sample (keeps the download small and the
# examples recognisable). Production would use the full Nifty 200 list.
UNIVERSE = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "LT", "ITC",
            "HINDUNILVR", "BHARTIARTL", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "ASIANPAINT", "WIPRO",
            "HCLTECH", "TECHM", "BAJFINANCE", "NTPC", "POWERGRID", "ONGC", "COALINDIA", "TATASTEEL",
            "JSWSTEEL", "M&M", "EICHERMOT", "HEROMOTOCO", "CIPLA", "DRREDDY", "DIVISLAB", "GRASIM",
            "BPCL", "HAL", "BEL", "TRENT", "CHOLAFIN", "SIEMENS"]

# From our own 2026-10-18 backtest (194 large Indian stocks, Oct 2020 - Oct 2026, daily data, 0.2% costs).
BACKTEST = {"trades": 2452, "win_rate": 41, "avg_win": 16.8, "avg_loss": -6.2, "avg_trade": 3.3,
            "random_avg": 1.7, "median": -2.2, "stocks": 194, "years": 5}

COST = 0.002


# ───────────────────────────── data + trades ────────────────────────────────

def _indicators(df):
    import pandas as pd
    c, h, l = df["Close"], df["High"], df["Low"]
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    ema50 = c.ewm(span=50, adjust=False).mean()
    cl50 = c.shift(1).rolling(50).max()
    sig = ((c > cl50) & (c.shift(1) <= cl50.shift(1)) & (c > ema50)).fillna(False)
    return atr, ema50, cl50, sig, l.rolling(20).min()


def find_trades(max_symbols=None, start="2021-06-01", end="2025-06-30"):
    """Simulate the 50-day closing-high rule (same exit logic as our backtest) and return trades
    with the data needed to draw them. Network: one yfinance batch call."""
    import yfinance as yf
    syms = UNIVERSE[:max_symbols] if max_symbols else UNIVERSE
    raw = yf.download([s + ".NS" for s in syms], period="6y", interval="1d", group_by="ticker",
                      auto_adjust=False, progress=False, threads=True)
    trades = []
    for s in syms:
        try:
            df = raw[s + ".NS"].dropna(subset=["Close", "Open", "High", "Low"])
            if len(df) < 300:
                continue
            atr, ema50, cl50, sig, low20 = _indicators(df)
            idx = df.index
            o, c = df["Open"].values, df["Close"].values
            i = 260
            while i < len(df) - 2:
                if sig.iloc[i] and str(start) <= str(idx[i].date()) <= str(end):
                    e = float(o[i + 1])
                    stop = max(float(low20.iloc[i]), e * 0.88)
                    hi, trail, path = e, stop, []
                    exit_i, exit_p, reason = None, None, "time"
                    for k in range(i + 1, min(i + 121, len(df))):
                        hi = max(hi, float(c[k]))
                        trail = max(trail, hi - 3.0 * float(atr.iloc[k]))
                        path.append((k, trail))
                        if c[k] < trail and k > i + 1:
                            nxt = k + 1 if k + 1 < len(df) else k
                            exit_i, exit_p = nxt, float(o[nxt]) if k + 1 < len(df) else float(c[k])
                            reason = "trail"
                            break
                    if exit_i is None:
                        exit_i = min(i + 120, len(df) - 1)
                        exit_p = float(c[exit_i])
                    ret = exit_p / e - 1 - COST
                    trades.append({"sym": s, "df": df, "sig_i": i, "entry_i": i + 1, "exit_i": exit_i,
                                   "entry": e, "exit": exit_p, "ret": ret, "level": float(cl50.iloc[i]),
                                   "ema": ema50.values.tolist(), "trail": path, "days": exit_i - (i + 1), "reason": reason})
                    i = exit_i + 1
                else:
                    i += 1
        except Exception as ex:
            print(f"[LESSON] {s} skipped: {ex}")
    return trades


def pick_examples(trades, seed=7):
    """Winner (a typical big winner, not an outlier), a stop-out loser, and a chop trade."""
    rnd = random.Random(seed)
    wins = [t for t in trades if 0.12 <= t["ret"] <= 0.35 and 25 <= t["days"] <= 100 and t["reason"] == "trail"]
    losses = [t for t in trades if -0.09 <= t["ret"] <= -0.04]
    chops = [t for t in trades if abs(t["ret"]) <= 0.03 and 18 <= t["days"] <= 80 and t["reason"] == "trail"]
    if not (wins and losses and chops):
        return None
    w = min(wins, key=lambda t: abs(t["ret"] - 0.20))
    l = min(losses, key=lambda t: abs(t["ret"] + 0.06))
    c = max(chops, key=lambda t: t["days"])
    used = {w["sym"], l["sym"]}
    if c["sym"] in used:
        alt = [t for t in chops if t["sym"] not in used]
        c = max(alt, key=lambda t: t["days"]) if alt else c
    return {"winner": w, "loser": l, "chop": c}


def _window(t, before=60, after=12):
    df = t["df"]
    a = max(0, t["sig_i"] - before)
    b = min(len(df) - 1, t["exit_i"] + after)
    series = [(df.index[i].date(), float(df["Close"].iloc[i])) for i in range(a, b + 1)]
    ema = [t["ema"][i] for i in range(a, b + 1)]
    return a, b, series, ema


def _money(v):
    return f"{v:,.0f}" if v >= 1000 else f"{v:,.1f}"


def _chart_for_trade(t, label, title_tag, accent, dur):
    a, b, series, ema = _window(t)
    rel = lambda i: i - a
    markers = [(rel(t["entry_i"]), "ENTRY", lv.BLUE), (rel(t["exit_i"]), "EXIT", lv.GREEN if t["ret"] >= 0 else lv.RED)]
    trail = [(rel(k), v) for k, v in t["trail"] if a <= k <= b]
    pct = t["ret"] * 100
    panel = [
        ("TRADE", f"{t['sym']}", lv.WHITE),
        ("ENTRY", f"Rs {_money(t['entry'])}   {t['df'].index[t['entry_i']].strftime('%d %b %Y')}", lv.WHITE),
        ("EXIT", f"Rs {_money(t['exit'])}   {t['df'].index[t['exit_i']].strftime('%d %b %Y')}", lv.WHITE),
        ("RESULT (after 0.2% costs)", f"{pct:+.1f}%  in {t['days']} sessions", lv.GREEN if pct >= 0 else lv.RED),
    ]
    return lv.chart_scene(f"{label}: {t['sym']}", series, tag=title_tag, level=t["level"],
                          level_label="50-DAY CLOSING HIGH", ema=ema, markers=markers, trail=trail,
                          panel=panel, accent=accent)(dur)


# ───────────────────────────── script (narration) ───────────────────────────

def _d(t, i):
    return t["df"].index[i].strftime("%d %B %Y")


def build_sample_script(ex):
    w, l, c = ex["winner"], ex["loser"], ex["chop"]
    bt = BACKTEST
    s = []
    s.append(("title", "Most breakouts fail. So why do traders keep using them? In this lesson we look at one specific rule, the fifty day closing high breakout, on real charts. "
              "We will see a winner, a loss, and a trade that went nowhere. Then we will look at what five years of data says, including what it does not prove."))
    s.append(("rule", "Here is the rule. First, a stock closes above the highest close of the last fifty trading days. That is the dashed gold line. "
              "Second, the stock is trading above its fifty day average, the blue line. Rule: act on the close, not on the intraday spike. A spike that fades by the close is not a breakout."))
    s.append(("winner", f"Example one: {w['sym']}. On {_d(w, w['sig_i'])} it closed above {_money(w['level'])}, and it was above its fifty day average. We assume entry at the next open, {_money(w['entry'])}. "
              f"The stop starts under the recent low, then trails three times the average true range below the highest close. That is the orange line, and notice it only moves up. "
              f"The trade exited on {_d(w, w['exit_i'])} at {_money(w['exit'])}. That is {w['ret'] * 100:+.1f} percent in {w['days']} sessions."))
    s.append(("loser", f"Example two: {l['sym']}. Same rule, same exit plan. This time price slipped back under the trailing stop after {l['days']} sessions, a loss of {abs(l['ret']) * 100:.1f} percent. "
              "A loss this size is what the rule expects. It is why position size matters: if a stop out costs you a small part of the account, you can survive many of them."))
    s.append(("chop", f"Example three: {c['sym']}. Nothing dramatic. After {c['days']} sessions the trade ended at {c['ret'] * 100:+.1f} percent. "
              "Many breakouts simply drift sideways. Time is a cost too, because your capital sits waiting."))
    s.append(("bars", f"Now the evidence. In our test on {bt['stocks']} large Indian stocks over {bt['years']} years, this rule won {bt['win_rate']} percent of its trades. "
              f"Winners averaged plus {bt['avg_win']} percent. Losers averaged minus {abs(bt['avg_loss'])} percent. The average trade made {bt['avg_trade']} percent, against {bt['random_avg']} percent for random entries. "
              f"The typical trade, the median, was a small loss of about {abs(bt['median'])} percent. The profit came from a few large winners."))
    s.append(("limits", "What this does not prove. Most of the gain came from one strong year, twenty twenty three. We tested only stocks that are in the index today, which flatters the result. "
              "Costs of point two percent per trade are included, but real slippage can be higher. Rule: use a breakout as a filter, size every position so a stop out is small, and expect to be wrong more often than right. "
              "This is education, not investment advice. The live list of current breakouts is on our website, ai three sixty trading dot in."))
    return s


# ───────────────────────────── TTS + render ─────────────────────────────────

async def _tts(text, voice, path):
    import edge_tts
    last = None
    for attempt in range(3):
        try:
            await edge_tts.Communicate(text, voice, rate="-2%").save(path)
            if os.path.getsize(path) > 1000:
                return
        except Exception as e:
            last = e
            await asyncio.sleep(2 * (attempt + 1))
    raise RuntimeError(f"TTS failed: {last}")


def render(script, ex, out_dir, voice="en-IN-PrabhatNeural"):
    from moviepy.editor import VideoClip, AudioFileClip, concatenate_videoclips
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bt = BACKTEST
    scenes = []
    for k, (kind, text) in enumerate(script):
        mp3 = str(out_dir / f"scene{k}.mp3")
        try:
            asyncio.run(_tts(text, voice, mp3))
        except Exception:
            asyncio.run(_tts(text, "en-IN-NeerjaNeural", mp3))
        aud = AudioFileClip(mp3)
        dur = aud.duration + 0.7
        if kind == "title":
            mf = lv.title_scene("The 50-day closing-high breakout", "Real examples, wins and losses, and what 5 years of data says", tag="TRADING LESSON")
        elif kind == "rule":
            t = ex["winner"]
            a, b, series, ema = _window(t)
            sig = t["sig_i"] - a
            mf = lv.chart_scene("The rule on a real chart", series, tag="THE RULE", level=t["level"], level_label="50-DAY CLOSING HIGH", ema=ema,
                                markers=[(sig, "CLOSE ABOVE", lv.GREEN)],
                                panel=[("CONDITION 1", "Close above the 50-day closing high", lv.GOLD), ("CONDITION 2", "Price above its 50-day average", lv.BLUE),
                                       ("WAIT FOR", "The CLOSE, not the spike", lv.WHITE)],
                                accent=lv.GOLD, reveal_to=sig + 4)(dur)
        elif kind == "winner":
            mf = _chart_for_trade(ex["winner"], "Example 1 - a winner", "EXAMPLE 1", lv.GREEN, dur)
        elif kind == "loser":
            mf = _chart_for_trade(ex["loser"], "Example 2 - a stop-out", "EXAMPLE 2", lv.RED, dur)
        elif kind == "chop":
            mf = _chart_for_trade(ex["chop"], "Example 3 - a trade that went nowhere", "EXAMPLE 3", lv.GOLD, dur)
        elif kind == "bars":
            mf = lv.bars_scene("What 5 years of data says", [
                ("Average winner", bt["avg_win"], lv.GREEN, "%"),
                ("Average loser", bt["avg_loss"], lv.RED, "%"),
                ("Typical (median) trade", bt["median"], lv.RED, "%"),
                ("Average per trade", bt["avg_trade"], lv.GOLD, "%"),
                ("Random entry, average", bt["random_avg"], lv.MUTED, "%"),
            ], note=f"{bt['win_rate']}% of trades won (the bars show average return per trade). {bt['trades']:,} trades, {bt['stocks']} large Indian stocks, daily data, costs included. Our own test.")
        else:
            mf = lv.text_scene("What this does NOT prove", [
                "Most of the gain came from one strong year (2023)",
                "Only today's index stocks were tested, which flatters results",
                "Real slippage can be higher than the 0.2% we assumed",
                "A breakout is a filter, not a promise",
            ], tag="THE LIMITS", accent=lv.GOLD,
                rule="Rule: size every position so a stop-out is small, and expect to be wrong more often than right.")
        clip = VideoClip(mf, duration=dur).set_audio(aud)
        scenes.append(clip)
    final = concatenate_videoclips(scenes, method="compose")
    out = str(out_dir / "lesson_sample.mp4")
    final.write_videofile(out, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    return out, final.duration


# ───────────────────────────── main ─────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--out", default="_drafts_local/lesson_sample")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    if not a.sample:
        print("v1.0 only builds the local sample: python lesson_engine.py --sample")
        return 0
    topic = next(t for t in bank.TOPICS if t["id"] == "rc01")
    print(f"[LESSON] topic: {topic['id']} - {topic['title']}")
    trades = find_trades()
    print(f"[LESSON] simulated {len(trades)} trades across {len(UNIVERSE)} stocks")
    ex = pick_examples(trades)
    if not ex:
        print("[LESSON] could not find three suitable examples")
        return 1
    script = build_sample_script(ex)
    text = " ".join(t for _, t in script)
    facts = {"win": BACKTEST["win_rate"], "winner": BACKTEST["avg_win"], "loser": BACKTEST["avg_loss"],
             "ex_winner": f"{ex['winner']['ret'] * 100:.1f}", "ex_loser": f"{abs(ex['loser']['ret']) * 100:.1f}"}
    ok, why = bank.quality_gate(text, facts)
    print(f"[LESSON] quality gate: {'PASS' if ok else 'FAIL'} {why} | words={len(text.split())}")
    if not ok:
        return 1
    for k, e in ex.items():
        print(f"   {k}: {e['sym']} entry {e['df'].index[e['entry_i']].date()} exit {e['df'].index[e['exit_i']].date()} ret {e['ret'] * 100:+.1f}% days {e['days']}")
    if a.no_render:
        return 0
    path, dur = render(script, ex, a.out)
    print(f"[LESSON] rendered {path}  ({dur:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
