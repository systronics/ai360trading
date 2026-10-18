"""
lesson_engine.py — evergreen LESSON videos for serious traders (v1.1, 2026-10-18)
==================================================================================
Builds a 3-4 minute landscape (1280x720) lesson video from REAL data with free tools only:
  * topic from lesson_bank.py (evergreen bank + balanced picker)
  * real historical charts from yfinance, animated with Pillow (lesson_visuals.py)
  * narration via edge_tts (free), one clip per scene so picture and voice stay in sync
  * lesson_bank.quality_gate() must pass on the English master script
  * REGION + LANGUAGE editions of the SAME lesson:
        --region us --lang en   US stocks, dollars, US English voice        (global default)
        --region in --lang en   Indian stocks, rupees, Indian English voice
        --region in --lang hi   Indian stocks, rupees, Hindi voice
    A translated edition must keep every number of the English master (checked).
  * also writes an .srt subtitle file and a 1280x720 thumbnail per edition.

THIS VERSION BUILDS LOCAL SAMPLES ONLY. It renders to a local folder and NEVER uploads.
Posting is a separate, owner-approved step (nothing here touches YouTube/Facebook/Telegram).

Usage:  python lesson_engine.py --sample --region us --lang en [--out DIR] [--no-render]
"""

import os, sys, re, asyncio, argparse
from pathlib import Path

import lesson_bank as bank
import lesson_visuals as lv

COST = 0.002

IN_UNIVERSE = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK", "LT", "ITC",
               "HINDUNILVR", "BHARTIARTL", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "ASIANPAINT", "WIPRO",
               "HCLTECH", "TECHM", "BAJFINANCE", "NTPC", "POWERGRID", "ONGC", "COALINDIA", "TATASTEEL",
               "JSWSTEEL", "M&M", "EICHERMOT", "HEROMOTOCO", "CIPLA", "DRREDDY", "DIVISLAB", "GRASIM",
               "BPCL", "HAL", "BEL", "TRENT", "CHOLAFIN", "SIEMENS"]
US_UNIVERSE = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "JPM", "V", "MA", "UNH", "JNJ", "PG", "HD", "XOM",
               "CVX", "KO", "PEP", "WMT", "COST", "DIS", "NFLX", "ADBE", "CRM", "ORCL", "INTC", "AMD", "QCOM", "TXN",
               "BA", "CAT", "GE", "MMM", "HON", "LOW", "MCD", "NKE", "SBUX", "GS", "MS", "PFE", "MRK", "ABBV"]

# Our own 2026-10-18 backtest on the larger Indian universe (194 stocks, Oct 2020 - Oct 2026, 0.2% costs).
BACKTEST_IN = {"trades": 2452, "win_rate": 41, "avg_win": 16.8, "avg_loss": -6.2, "avg_trade": 3.3,
               "random_avg": 1.7, "median": -2.2, "stocks": 194, "years": 5}

REGIONS = {
    "in": {"universe": IN_UNIVERSE, "suffix": ".NS", "ccy": "Rs", "site": "ai360trading.in", "stats": BACKTEST_IN,
           "market": "large Indian"},
    "us": {"universe": US_UNIVERSE, "suffix": "", "ccy": "$", "site": "ai360trading.in", "stats": None,
           "market": "large US"},
}

VOICES = {("us", "en"): ["en-US-AndrewNeural", "en-US-ChristopherNeural"],
          ("in", "en"): ["en-IN-PrabhatNeural", "en-IN-NeerjaNeural"],
          ("in", "hi"): ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]}

# spoken names so the voice says "Bharat Petroleum", not "B P C L"
NAMES = {
    "RELIANCE": ("Reliance Industries", "रिलायंस इंडस्ट्रीज़"), "TCS": ("T C S", "टीसीएस"), "INFY": ("Infosys", "इन्फोसिस"),
    "HDFCBANK": ("H D F C Bank", "एचडीएफसी बैंक"), "ICICIBANK": ("I C I C I Bank", "आईसीआईसीआई बैंक"), "SBIN": ("State Bank of India", "स्टेट बैंक ऑफ़ इंडिया"),
    "AXISBANK": ("Axis Bank", "एक्सिस बैंक"), "KOTAKBANK": ("Kotak Mahindra Bank", "कोटक महिंद्रा बैंक"), "LT": ("Larsen and Toubro", "एलएंडटी"),
    "ITC": ("I T C", "आईटीसी"), "HINDUNILVR": ("Hindustan Unilever", "हिंदुस्तान यूनिलीवर"), "BHARTIARTL": ("Bharti Airtel", "भारती एयरटेल"),
    "MARUTI": ("Maruti Suzuki", "मारुति सुज़ुकी"), "SUNPHARMA": ("Sun Pharma", "सन फ़ार्मा"), "TITAN": ("Titan", "टाइटन"),
    "ULTRACEMCO": ("UltraTech Cement", "अल्ट्राटेक सीमेंट"), "ASIANPAINT": ("Asian Paints", "एशियन पेंट्स"), "WIPRO": ("Wipro", "विप्रो"),
    "HCLTECH": ("H C L Tech", "एचसीएल टेक"), "TECHM": ("Tech Mahindra", "टेक महिंद्रा"), "BAJFINANCE": ("Bajaj Finance", "बजाज फ़ाइनेंस"),
    "NTPC": ("N T P C", "एनटीपीसी"), "POWERGRID": ("Power Grid", "पावर ग्रिड"), "ONGC": ("O N G C", "ओएनजीसी"),
    "COALINDIA": ("Coal India", "कोल इंडिया"), "TATASTEEL": ("Tata Steel", "टाटा स्टील"), "JSWSTEEL": ("J S W Steel", "जेएसडब्ल्यू स्टील"),
    "M&M": ("Mahindra and Mahindra", "महिंद्रा एंड महिंद्रा"), "EICHERMOT": ("Eicher Motors", "आयशर मोटर्स"), "HEROMOTOCO": ("Hero MotoCorp", "हीरो मोटोकॉर्प"),
    "CIPLA": ("Cipla", "सिप्ला"), "DRREDDY": ("Dr Reddy's", "डॉ रेड्डीज़"), "DIVISLAB": ("Divi's Laboratories", "दिविज़ लैबोरेटरीज़"),
    "GRASIM": ("Grasim", "ग्रासिम"), "BPCL": ("Bharat Petroleum", "भारत पेट्रोलियम"), "HAL": ("Hindustan Aeronautics", "हिंदुस्तान एयरोनॉटिक्स"),
    "BEL": ("Bharat Electronics", "भारत इलेक्ट्रॉनिक्स"), "TRENT": ("Trent", "ट्रेंट"), "CHOLAFIN": ("Cholamandalam Finance", "चोलामंडलम फ़ाइनेंस"),
    "SIEMENS": ("Siemens", "सीमेंस"),
    "AAPL": ("Apple", ""), "MSFT": ("Microsoft", ""), "GOOGL": ("Alphabet", ""), "AMZN": ("Amazon", ""), "NVDA": ("Nvidia", ""),
    "META": ("Meta", ""), "JPM": ("J P Morgan", ""), "V": ("Visa", ""), "MA": ("Mastercard", ""), "UNH": ("UnitedHealth", ""),
    "JNJ": ("Johnson and Johnson", ""), "PG": ("Procter and Gamble", ""), "HD": ("Home Depot", ""), "XOM": ("Exxon Mobil", ""),
    "CVX": ("Chevron", ""), "KO": ("Coca-Cola", ""), "PEP": ("PepsiCo", ""), "WMT": ("Walmart", ""), "COST": ("Costco", ""),
    "DIS": ("Disney", ""), "NFLX": ("Netflix", ""), "ADBE": ("Adobe", ""), "CRM": ("Salesforce", ""), "ORCL": ("Oracle", ""),
    "INTC": ("Intel", ""), "AMD": ("A M D", ""), "QCOM": ("Qualcomm", ""), "TXN": ("Texas Instruments", ""), "BA": ("Boeing", ""),
    "CAT": ("Caterpillar", ""), "GE": ("G E", ""), "MMM": ("3M", ""), "HON": ("Honeywell", ""), "LOW": ("Lowe's", ""),
    "MCD": ("McDonald's", ""), "NKE": ("Nike", ""), "SBUX": ("Starbucks", ""), "GS": ("Goldman Sachs", ""), "MS": ("Morgan Stanley", ""),
    "PFE": ("Pfizer", ""), "MRK": ("Merck", ""), "ABBV": ("AbbVie", ""),
}

MONTHS_HI = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]


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


def _simulate(df, i, atr, low20):
    """Same exit logic as our backtest: next-open entry, stop = max(20d low, -12%), 3x ATR chandelier on
    closes, exit at the next open, 120-session cap."""
    o, c = df["Open"].values, df["Close"].values
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
    return e, exit_i, exit_p, path, reason


def find_trades(region, start="2021-06-01", end="2025-06-30"):
    """Signal trades + a random-entry baseline for the region's universe. One yfinance batch call."""
    import yfinance as yf
    cfg = REGIONS[region]
    syms = cfg["universe"]
    raw = yf.download([s + cfg["suffix"] for s in syms], period="6y", interval="1d", group_by="ticker",
                      auto_adjust=False, progress=False, threads=True)
    trades, baseline = [], []
    for s in syms:
        try:
            df = raw[s + cfg["suffix"]].dropna(subset=["Close", "Open", "High", "Low"])
            if len(df) < 300:
                continue
            atr, ema50, cl50, sig, low20 = _indicators(df)
            idx = df.index
            i = 260
            while i < len(df) - 2:
                if sig.iloc[i] and str(start) <= str(idx[i].date()) <= str(end):
                    e, exit_i, exit_p, path, reason = _simulate(df, i, atr, low20)
                    ret = exit_p / e - 1 - COST
                    trades.append({"sym": s, "df": df, "sig_i": i, "entry_i": i + 1, "exit_i": exit_i, "entry": e,
                                   "exit": exit_p, "ret": ret, "level": float(cl50.iloc[i]), "ema": ema50.values.tolist(),
                                   "trail": path, "days": exit_i - (i + 1), "reason": reason})
                    i = exit_i + 1
                else:
                    i += 1
            for j in range(260, len(df) - 130, 10):
                if str(start) <= str(idx[j].date()) <= str(end):
                    e, exit_i, exit_p, _, _ = _simulate(df, j, atr, low20)
                    baseline.append(exit_p / e - 1 - COST)
        except Exception as ex:
            print(f"[LESSON] {s} skipped: {ex}")
    return trades, baseline


def compute_stats(trades, baseline, stocks, years=4):
    import statistics
    r = [t["ret"] * 100 for t in trades]
    wins = [x for x in r if x > 0]
    losses = [x for x in r if x <= 0]
    return {"trades": len(r), "stocks": stocks, "years": years,
            "win_rate": round(len(wins) / len(r) * 100) if r else 0,
            "avg_win": round(sum(wins) / len(wins), 1) if wins else 0.0,
            "avg_loss": round(sum(losses) / len(losses), 1) if losses else 0.0,
            "avg_trade": round(sum(r) / len(r), 1) if r else 0.0,
            "median": round(statistics.median(r), 1) if r else 0.0,
            "random_avg": round(sum(baseline) / len(baseline) * 100, 1) if baseline else 0.0}


def pick_examples(trades):
    """Winner (a typical big winner), a stop-out loser, and a chop trade; all ended by the trailing stop."""
    wins = [t for t in trades if 0.12 <= t["ret"] <= 0.35 and 25 <= t["days"] <= 100 and t["reason"] == "trail"]
    losses = [t for t in trades if -0.09 <= t["ret"] <= -0.04]
    chops = [t for t in trades if abs(t["ret"]) <= 0.03 and 18 <= t["days"] <= 80 and t["reason"] == "trail"]
    if not (wins and losses and chops):
        return None
    w = min(wins, key=lambda t: abs(t["ret"] - 0.20))
    l = min(losses, key=lambda t: abs(t["ret"] + 0.06))
    used = {w["sym"], l["sym"]}
    alt = [t for t in chops if t["sym"] not in used] or chops
    c = max(alt, key=lambda t: t["days"])
    return {"winner": w, "loser": l, "chop": c}


def _window(t, before=60, after=12):
    df = t["df"]
    a = max(0, t["sig_i"] - before)
    b = min(len(df) - 1, t["exit_i"] + after)
    series = [(df.index[i].date(), float(df["Close"].iloc[i])) for i in range(a, b + 1)]
    ema = [t["ema"][i] for i in range(a, b + 1)]
    return a, b, series, ema


# ───────────────────────────── spoken formatting ────────────────────────────

def _num(v):
    return f"{v:,.0f}" if v >= 1000 else f"{v:,.1f}"


def _money(v, region, lang):
    if region == "us":
        return f"${v:,.2f}"
    return f"{_num(v)} rupees" if lang == "en" else f"{_num(v)} रुपये"


def _date(t, i, lang):
    d = t["df"].index[i]
    if lang == "hi":
        return f"{d.day} {MONTHS_HI[d.month - 1]} {d.year}"
    return d.strftime("%d %B %Y")


def _name(sym, lang):
    en, hi = NAMES.get(sym, (sym, ""))
    return hi if (lang == "hi" and hi) else en


# ───────────────────────────── scripts (narration) ──────────────────────────

def build_script(lang, region, ex, st):
    w, l, c = ex["winner"], ex["loser"], ex["chop"]
    M = lambda v: _money(v, region, lang)
    D = lambda t, i: _date(t, i, lang)
    N = lambda t: _name(t["sym"], lang)
    site = "ai three sixty trading dot in"
    thin = (st["avg_trade"] - st["random_avg"]) < 1.0      # be honest when the edge over random is small
    thin_en = " That is only a thin edge over random entries, so costs and discipline matter a lot." if thin else ""
    thin_hi = " ये रैंडम एंट्री पर सिर्फ़ एक पतली बढ़त है, इसलिए लागत और अनुशासन बहुत मायने रखते हैं।" if thin else ""
    if lang == "hi":
        return [
            ("title", "ज़्यादातर ब्रेकआउट फेल हो जाते हैं। फिर भी ट्रेडर इन्हें क्यों इस्तेमाल करते हैं? इस लेसन में हम एक ख़ास नियम देखेंगे, पचास दिन के क्लोज़िंग हाई का ब्रेकआउट, असली चार्ट्स पर। "
                      "हम एक जीत वाला ट्रेड देखेंगे, एक नुकसान वाला, और एक ऐसा ट्रेड जो कहीं पहुँचा ही नहीं। फिर देखेंगे कि पाँच साल का डेटा क्या कहता है, और वह क्या साबित नहीं करता।"),
            ("rule", "नियम ये है। पहला, शेयर पिछले पचास ट्रेडिंग दिनों के सबसे ऊँचे क्लोज़ से ऊपर बंद होता है। ये सुनहरी बिंदीदार लाइन है। दूसरा, शेयर अपने पचास दिन के औसत से ऊपर चल रहा हो, यानी नीली लाइन। "
                     "नियम: क्लोज़ पर काम करें, दिन के बीच की उछाल पर नहीं। जो उछाल क्लोज़ तक टिकती नहीं, वो ब्रेकआउट नहीं है।"),
            ("winner", f"उदाहरण एक: {N(w)}। {D(w, w['sig_i'])} को इसने {M(w['level'])} से ऊपर क्लोज़ किया, और ये अपने पचास दिन के औसत से ऊपर था। हमने मान लिया कि अगले दिन खुलते ही {M(w['entry'])} पर एंट्री हुई। "
                       f"स्टॉप शुरू में हाल के निचले स्तर के नीचे रहता है, फिर सबसे ऊँचे क्लोज़ से तीन गुना ATR नीचे चलता है। ये नारंगी लाइन है, और ध्यान दें, ये सिर्फ़ ऊपर जाती है। "
                       f"ट्रेड {D(w, w['exit_i'])} को {M(w['exit'])} पर बंद हुआ। यानी {w['days']} सत्रों में {w['ret'] * 100:+.1f} प्रतिशत।"),
            ("loser", f"उदाहरण दो: {N(l)}। वही नियम, वही एग्ज़िट प्लान। इस बार भाव {l['days']} सत्रों के बाद ट्रेलिंग स्टॉप के नीचे आ गया, और {abs(l['ret']) * 100:.1f} प्रतिशत का नुकसान हुआ। "
                      "इतना नुकसान नियम में पहले से शामिल है। इसीलिए पोज़िशन का आकार मायने रखता है: अगर एक स्टॉप-आउट से खाते का छोटा हिस्सा ही कटे, तो आप कई स्टॉप-आउट झेल सकते हैं।"),
            ("chop", f"उदाहरण तीन: {N(c)}। कुछ नाटकीय नहीं हुआ। {c['days']} सत्रों के बाद ट्रेड {c['ret'] * 100:+.1f} प्रतिशत पर ख़त्म हुआ। कई ब्रेकआउट बस बग़ल में चलते रहते हैं। "
                     "समय भी एक क़ीमत है, क्योंकि आपकी पूँजी इंतज़ार में बैठी रहती है।"),
            ("bars", f"अब सबूत देखिए। {st['stocks']} बड़े शेयरों पर {st['years']} साल के हमारे टेस्ट में, इस नियम के {st['win_rate']} प्रतिशत ट्रेड जीते। जीतने वाले ट्रेड औसतन {st['avg_win']} प्रतिशत ऊपर गए। "
                     f"हारने वाले औसतन {abs(st['avg_loss'])} प्रतिशत नीचे। औसत ट्रेड ने {st['avg_trade']} प्रतिशत कमाया, जबकि रैंडम एंट्री ने {st['random_avg']} प्रतिशत। "
                     f"बीच का, यानी मीडियन ट्रेड, लगभग {abs(st['median'])} प्रतिशत का छोटा नुकसान था। मुनाफ़ा कुछ बड़े विनर्स से आया।{thin_hi}"),
            ("limits", "ये क्या साबित नहीं करता। ज़्यादातर फ़ायदा एक ही मज़बूत साल, 2023, से आया। हमने सिर्फ़ वही शेयर टेस्ट किए जो आज इंडेक्स में हैं, जिससे नतीजे थोड़े बेहतर दिखते हैं। "
                       "0.2 प्रतिशत की लागत शामिल है, पर असली स्लिपेज़ इससे ज़्यादा हो सकती है। नियम: हर पोज़िशन का आकार ऐसा रखें कि स्टॉप-आउट छोटा रहे, और मानकर चलें कि आप जीतने से ज़्यादा बार ग़लत होंगे। "
                       "ये शिक्षा है, निवेश सलाह नहीं। मौजूदा ब्रेकआउट की लाइव लिस्ट हमारी वेबसाइट पर है।"),
        ]
    mkt = REGIONS[region]["market"]
    return [
        ("title", "Most breakouts fail. So why do traders keep using them? In this lesson we look at one specific rule, the fifty day closing high breakout, on real charts. "
                  "We will see a winner, a loss, and a trade that went nowhere. Then we will look at what five years of data says, including what it does not prove."),
        ("rule", "Here is the rule. First, a stock closes above the highest close of the last fifty trading days. That is the dashed gold line. "
                 "Second, the stock is trading above its fifty day average, the blue line. Rule: act on the close, not on the intraday spike. A spike that fades by the close is not a breakout."),
        ("winner", f"Example one: {N(w)}. On {D(w, w['sig_i'])} it closed above {M(w['level'])}, and it was above its fifty day average. We assume entry at the next open, {M(w['entry'])}. "
                   f"The stop starts under the recent low, then trails three times the average true range below the highest close. That is the orange line, and notice it only moves up. "
                   f"The trade exited on {D(w, w['exit_i'])} at {M(w['exit'])}. That is {w['ret'] * 100:+.1f} percent in {w['days']} sessions."),
        ("loser", f"Example two: {N(l)}. Same rule, same exit plan. This time price slipped back under the trailing stop after {l['days']} sessions, a loss of {abs(l['ret']) * 100:.1f} percent. "
                  "A loss this size is what the rule expects. It is why position size matters: if a stop out costs you a small part of the account, you can survive many of them."),
        ("chop", f"Example three: {N(c)}. Nothing dramatic. After {c['days']} sessions the trade ended at {c['ret'] * 100:+.1f} percent. "
                 "Many breakouts simply drift sideways. Time is a cost too, because your capital sits waiting."),
        ("bars", f"Now the evidence. In our test on {st['stocks']} {mkt} stocks over {st['years']} years, this rule won {st['win_rate']} percent of its trades. "
                 f"Winners averaged plus {st['avg_win']} percent. Losers averaged minus {abs(st['avg_loss'])} percent. The average trade made {st['avg_trade']} percent, against {st['random_avg']} percent for random entries. "
                 f"The typical trade, the median, was a small loss of about {abs(st['median'])} percent. The profit came from a few large winners.{thin_en}"),
        ("limits", "What this does not prove. Most of the gain came from a few strong years. We tested only stocks that are in the index today, which flatters the result. "
                   "Costs of point two percent per trade are included, but real slippage can be higher. Rule: use a breakout as a filter, size every position so a stop out is small, and expect to be wrong more often than right. "
                   f"This is education, not investment advice. The live list of current breakouts is on our website, {site}."),
    ]


def numbers_preserved(master_text, other_text):
    """Every digit-number in the English master must appear in the translation."""
    nums = lambda t: {m.strip(",.").replace(",", "") for m in re.findall(r"\d[\d,\.]*", t)}
    miss = sorted(x for x in nums(master_text) if x and x not in nums(other_text))
    return (not miss), miss


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


def _chart_for_trade(t, label, tag, accent, dur, ccy):
    a, b, series, ema = _window(t)
    rel = lambda i: i - a
    markers = [(rel(t["entry_i"]), "ENTRY", lv.BLUE), (rel(t["exit_i"]), "EXIT", lv.GREEN if t["ret"] >= 0 else lv.RED)]
    trail = [(rel(k), v) for k, v in t["trail"] if a <= k <= b]
    pct = t["ret"] * 100
    ccy_s = "Rs " if ccy == "Rs" else "$"
    panel = [
        ("TRADE", f"{t['sym']}", lv.WHITE),
        ("ENTRY", f"{ccy_s}{_num(t['entry'])}   {t['df'].index[t['entry_i']].strftime('%d %b %Y')}", lv.WHITE),
        ("EXIT", f"{ccy_s}{_num(t['exit'])}   {t['df'].index[t['exit_i']].strftime('%d %b %Y')}", lv.WHITE),
        ("RESULT (after 0.2% costs)", f"{pct:+.1f}%  in {t['days']} sessions", lv.GREEN if pct >= 0 else lv.RED),
    ]
    return lv.chart_scene(f"{label}: {t['sym']}", series, tag=tag, level=t["level"], level_label="50-DAY CLOSING HIGH",
                          ema=ema, markers=markers, trail=trail, panel=panel, accent=accent)(dur)


def _srt_time(s):
    h, m = int(s // 3600), int((s % 3600) // 60)
    return f"{h:02d}:{m:02d}:{int(s % 60):02d},{int((s - int(s)) * 1000):03d}"


def render(script, ex, st, region, lang, out_dir, voice):
    from moviepy.editor import VideoClip, AudioFileClip, concatenate_videoclips
    from PIL import Image
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = REGIONS[region]
    ccy = cfg["ccy"]
    scenes, srt, t0, n = [], [], 0.0, 1
    heading, sub = "The 50-day closing-high breakout", "Real examples, wins and losses, and what the data says"
    for k, (kind, text) in enumerate(script):
        mp3 = str(out_dir / f"scene{k}.mp3")
        v = voice
        try:
            asyncio.run(_tts(text, v, mp3))
        except Exception:
            alt = [x for x in VOICES[(region, lang)] if x != v]
            asyncio.run(_tts(text, alt[0], mp3))
        aud = AudioFileClip(mp3)
        dur = aud.duration + 0.7
        # subtitles: split into sentences, time proportionally across the narration
        sents = [s.strip() for s in re.split(r"(?<=[.?!।])\s+", text) if s.strip()]
        total = sum(len(s) for s in sents) or 1
        tt = t0
        for s in sents:
            seg = aud.duration * len(s) / total
            srt.append(f"{n}\n{_srt_time(tt)} --> {_srt_time(tt + seg)}\n{s}\n")
            n += 1
            tt += seg
        t0 += dur
        if kind == "title":
            if k == 0:
                thumb = lv.title_scene(heading, sub, tag="TRADING LESSON")(3.5)
                Image.fromarray(thumb).save(str(out_dir / "thumbnail.png"))
            mf = lv.title_scene(heading, sub, tag="TRADING LESSON")
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
            mf = _chart_for_trade(ex["winner"], "Example 1 - a winner", "EXAMPLE 1", lv.GREEN, dur, ccy)
        elif kind == "loser":
            mf = _chart_for_trade(ex["loser"], "Example 2 - a stop-out", "EXAMPLE 2", lv.RED, dur, ccy)
        elif kind == "chop":
            mf = _chart_for_trade(ex["chop"], "Example 3 - a trade that went nowhere", "EXAMPLE 3", lv.GOLD, dur, ccy)
        elif kind == "bars":
            mf = lv.bars_scene("What the data says", [
                ("Average winner", st["avg_win"], lv.GREEN, "%"),
                ("Average loser", st["avg_loss"], lv.RED, "%"),
                ("Typical (median) trade", st["median"], lv.RED if st["median"] < 0 else lv.GREEN, "%"),
                ("Average per trade", st["avg_trade"], lv.GOLD, "%"),
                ("Random entry, average", st["random_avg"], lv.MUTED, "%"),
            ], note=f"{st['win_rate']}% of trades won (bars = average return per trade). {st['trades']:,} trades, {st['stocks']} {cfg['market']} stocks, daily data, costs included. Our own test.")
        else:
            mf = lv.text_scene("What this does NOT prove", [
                "Most of the gain came from a few strong years",
                "Only today's index stocks were tested, which flatters results",
                "Real slippage can be higher than the 0.2% we assumed",
                "A breakout is a filter, not a promise",
            ], tag="THE LIMITS", accent=lv.GOLD,
                rule="Rule: size every position so a stop-out is small, and expect to be wrong more often than right.")
        scenes.append(VideoClip(mf, duration=dur).set_audio(aud))
    final = concatenate_videoclips(scenes, method="compose")
    name = f"lesson_{region}_{lang}"
    out = str(out_dir / f"{name}.mp4")
    final.write_videofile(out, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    (out_dir / f"{name}.srt").write_text("\n".join(srt), encoding="utf-8")
    return out, final.duration


# ───────────────────────────── main ─────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--region", default="us", choices=list(REGIONS))
    ap.add_argument("--lang", default="en", choices=["en", "hi"])
    ap.add_argument("--out", default="_drafts_local/lesson_sample")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    if not a.sample:
        print("v1.1 only builds local samples: python lesson_engine.py --sample --region us --lang en")
        return 0
    if (a.region, a.lang) not in VOICES:
        print(f"no voice configured for region={a.region} lang={a.lang}")
        return 1
    topic = next(t for t in bank.TOPICS if t["id"] == "rc01")
    print(f"[LESSON] topic: {topic['id']} - {topic['title']} | region={a.region} lang={a.lang}")
    trades, baseline = find_trades(a.region)
    cfg = REGIONS[a.region]
    st = cfg["stats"] or compute_stats(trades, baseline, len(cfg["universe"]))
    print(f"[LESSON] {len(trades)} trades; stats used: {st}")
    ex = pick_examples(trades)
    if not ex:
        print("[LESSON] could not find three suitable examples")
        return 1
    # English master first: quality gate runs on it; other languages must keep every number
    master = build_script("en", a.region, ex, st)
    mtext = " ".join(t for _, t in master)
    facts = {"win": st["win_rate"], "winner": st["avg_win"], "loser": st["avg_loss"],
             "ex_winner": f"{ex['winner']['ret'] * 100:.1f}", "ex_loser": f"{abs(ex['loser']['ret']) * 100:.1f}"}
    ok, why = bank.quality_gate(mtext, facts)
    print(f"[LESSON] quality gate (English master): {'PASS' if ok else 'FAIL'} {why} | words={len(mtext.split())}")
    if not ok:
        return 1
    script = master if a.lang == "en" else build_script(a.lang, a.region, ex, st)
    if a.lang != "en":
        okn, miss = numbers_preserved(mtext, " ".join(t for _, t in script))
        print(f"[LESSON] numbers preserved in {a.lang}: {okn} {miss}")
        if not okn:
            return 1
    for k, e in ex.items():
        print(f"   {k}: {e['sym']} entry {e['df'].index[e['entry_i']].date()} exit {e['df'].index[e['exit_i']].date()} ret {e['ret'] * 100:+.1f}% days {e['days']}")
    if a.no_render:
        return 0
    path, dur = render(script, ex, st, a.region, a.lang, a.out, VOICES[(a.region, a.lang)][0])
    print(f"[LESSON] rendered {path}  ({dur:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
