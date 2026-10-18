"""
lesson_builders.py — the actual evergreen lessons (v1.0, 2026-10-18)
====================================================================
Each builder returns a Lesson dict:
    {"id", "heading", "sub", "regions", "langs", "facts",
     "title": {lang: str}, "desc": {lang: str}, "tags": {lang: [..]},
     "scenes": [ {"kind", "text": {lang: narration}, "visual": factory(duration) -> make_frame} ]}
The ENGLISH text is the master: lesson_bank.quality_gate() runs on it, and every other language
must keep all its numbers (lesson_engine.numbers_preserved).

Lessons (v1.0 queue):
    rc01  The 50-day closing-high breakout: real examples, wins and losses     (regions us, in)
    rm01  Why a 50% loss needs a 100% gain                                      (pure maths, all regions)
    rs01  Does buying a big fall pay? A 12-month test                          (computed live per region)
    au01  Our own best and worst closed paper trades                            (our ledger, India)
Add more builders here (and to QUEUE) to extend the weekly series. When the queue is empty the
runner stops cleanly and alerts the owner instead of repeating content.
"""

import os, re, json
import lesson_engine as E
import lesson_visuals as lv

QUEUE = ["rc01", "rm01", "rs01", "au01"]


def _scene(kind, en, hi, visual):
    return {"kind": kind, "text": {"en": en, "hi": hi}, "visual": visual}


def _fmt_hi_pct(x):
    return f"{x}"


# ───────────────────────────── rc01 ─────────────────────────────────────────

def build_rc01(region):
    trades, baseline = E.find_trades(region)
    cfg = E.REGIONS[region]
    st = cfg["stats"] or E.compute_stats(trades, baseline, len(cfg["universe"]))
    ex = E.pick_examples(trades)
    if not ex:
        raise RuntimeError("rc01: could not find three suitable examples")
    en = E.build_script("en", region, ex, st)
    hi = E.build_script("hi", region, ex, st) if region == "in" else en
    ccy = cfg["ccy"]
    heading, sub = "The 50-day closing-high breakout", "Real examples, wins and losses, and what the data says"
    w = ex["winner"]
    a, b, series, ema = E._window(w)
    sig = w["sig_i"] - a

    def v_title(dur):
        return lv.title_scene(heading, sub, tag="TRADING LESSON")

    def v_rule(dur):
        return lv.chart_scene("The rule on a real chart", series, tag="THE RULE", level=w["level"], level_label="50-DAY CLOSING HIGH", ema=ema,
                              markers=[(sig, "CLOSE ABOVE", lv.GREEN)],
                              panel=[("CONDITION 1", "Close above the 50-day closing high", lv.GOLD), ("CONDITION 2", "Price above its 50-day average", lv.BLUE),
                                     ("WAIT FOR", "The CLOSE, not the spike", lv.WHITE)],
                              accent=lv.GOLD, reveal_to=sig + 4)(dur)

    def v_bars(dur):
        return lv.bars_scene("What the data says", [
            ("Average winner", st["avg_win"], lv.GREEN, "%"), ("Average loser", st["avg_loss"], lv.RED, "%"),
            ("Typical (median) trade", st["median"], lv.RED if st["median"] < 0 else lv.GREEN, "%"),
            ("Average per trade", st["avg_trade"], lv.GOLD, "%"), ("Random entry, average", st["random_avg"], lv.MUTED, "%"),
        ], note=f"{st['win_rate']}% of trades won (bars = average return per trade). {st['trades']:,} trades, {st['stocks']} {cfg['market']} stocks, daily data, costs included. Our own test.")

    def v_limits(dur):
        return lv.text_scene("What this does NOT prove", [
            "Most of the gain came from a few strong years", "Only today's index stocks were tested, which flatters results",
            "Real slippage can be higher than the 0.2% we assumed", "A breakout is a filter, not a promise",
        ], tag="THE LIMITS", accent=lv.GOLD, rule="Rule: size every position so a stop-out is small, and expect to be wrong more often than right.")

    vis = {"title": v_title, "rule": v_rule,
           "winner": lambda d: E._chart_for_trade(ex["winner"], "Example 1 - a winner", "EXAMPLE 1", lv.GREEN, d, ccy),
           "loser": lambda d: E._chart_for_trade(ex["loser"], "Example 2 - a stop-out", "EXAMPLE 2", lv.RED, d, ccy),
           "chop": lambda d: E._chart_for_trade(ex["chop"], "Example 3 - a trade that went nowhere", "EXAMPLE 3", lv.GOLD, d, ccy),
           "bars": v_bars, "limits": v_limits}
    scenes = [_scene(k, t, hi[i][1], vis[k]) for i, (k, t) in enumerate(en)]
    market = "US" if region == "us" else "Indian"
    return {
        "id": "rc01", "heading": heading, "sub": sub, "regions": ["us", "in"], "langs": ["en", "hi"] if region == "in" else ["en"],
        "facts": {"win": st["win_rate"], "winner": st["avg_win"], "loser": st["avg_loss"],
                  "ex_winner": f"{ex['winner']['ret'] * 100:.1f}", "ex_loser": f"{abs(ex['loser']['ret']) * 100:.1f}"},
        "title": {"en": f"The 50-Day Breakout Rule: Real {market} Stock Examples (Wins and Losses)",
                  "hi": "50 दिन के हाई का ब्रेकआउट: असली चार्ट, जीत और हार दोनों | ट्रेडिंग लेसन"},
        "desc": {"en": "One breakout rule, tested honestly on real charts: a winner, a stop-out and a trade that went nowhere, plus what five years of data says and what it does NOT prove.",
                 "hi": "एक ब्रेकआउट नियम, असली चार्ट्स पर ईमानदारी से परखा हुआ: एक जीत, एक स्टॉप-आउट और एक ऐसा ट्रेड जो कहीं नहीं पहुँचा, साथ में पाँच साल का डेटा और वह जो ये साबित नहीं करता।"},
        "tags": {"en": ["trading lesson", "breakout trading", "50 day high", "stock market education", "trading rules", "technical analysis", "risk management"],
                 "hi": ["trading lesson hindi", "breakout trading", "share market hindi", "stock market education", "technical analysis hindi", "risk management"]},
        "scenes": scenes,
    }


# ───────────────────────────── rm01 (pure maths) ────────────────────────────

def build_rm01(region):
    losses = [10, 20, 30, 40, 50, 60, 70]
    need = {L: round(1 / (1 - L / 100) - 1, 3) * 100 for L in losses}
    need = {L: round(v, 1) for L, v in need.items()}
    risks = [1, 2, 5, 10]
    down = {r: round((1 - (1 - r / 100) ** 10) * 100, 1) for r in risks}
    rec10 = round((1 / (1 - down[10] / 100) - 1) * 100, 1)
    heading, sub = "Why a 50% loss needs a 100% gain", "The arithmetic every trader must respect"

    en = [
        ("title", "A fifty percent loss needs a one hundred percent gain just to get back to even. This is not an opinion, it is arithmetic, and it explains why serious traders think about losses before they think about profits."),
        ("idea", "Start with one hundred. Lose fifty percent and you have fifty left. To get back to one hundred you must double that fifty, which is a gain of 100 percent. The loss and the gain are not the same size. The deeper the hole, the steeper the climb."),
        ("need", f"Here is the pattern. A 10 percent loss needs an {need[10]} percent gain to recover. A 20 percent loss needs {need[20]}. A 30 percent loss needs {need[30]}. A 50 percent loss needs {need[50]}. And a 70 percent loss needs {need[70]} percent. "
                 "Notice how the bars bend upward. After about thirty percent, recovery becomes very hard."),
        ("streak", f"Now see why risk per trade matters. Every trader eventually loses ten trades in a row. If you risk 1 percent per trade, ten losses leave you down {down[1]} percent. Risk 2 percent, and you are down {down[2]} percent. Risk 5 percent, down {down[5]} percent. "
                   f"Risk 10 percent per trade, and you are down {down[10]} percent, which needs a {rec10} percent gain just to recover."),
        ("limits", "What this does not prove. The arithmetic is exact, but it does not tell you whether your system has an edge. Real markets add gaps and slippage, so an actual loss can be larger than the one you planned. "
                   "Rule: decide your maximum loss before you enter, keep it small, usually 1 percent of your account or less per trade, and let the arithmetic protect you. This is education, not investment advice."),
    ]
    hi = [
        ("title", "पचास प्रतिशत के नुकसान की भरपाई के लिए सौ प्रतिशत का मुनाफ़ा चाहिए। ये राय नहीं, गणित है, और इसी वजह से गंभीर ट्रेडर मुनाफ़े से पहले नुकसान के बारे में सोचते हैं।"),
        ("idea", "सौ से शुरू कीजिए। पचास प्रतिशत गँवाइए तो पचास बचते हैं। वापस सौ तक पहुँचने के लिए इन पचास को दोगुना करना होगा, यानी 100 प्रतिशत का मुनाफ़ा। नुकसान और मुनाफ़ा बराबर नहीं होते। गड्ढा जितना गहरा, चढ़ाई उतनी तीखी।"),
        ("need", f"पैटर्न देखिए। 10 प्रतिशत के नुकसान की भरपाई के लिए {need[10]} प्रतिशत मुनाफ़ा चाहिए। 20 प्रतिशत के लिए {need[20]}। 30 प्रतिशत के लिए {need[30]}। 50 प्रतिशत के लिए {need[50]}। और 70 प्रतिशत के नुकसान के लिए {need[70]} प्रतिशत। "
                 "देखिए बार कैसे ऊपर की ओर मुड़ते हैं। लगभग तीस प्रतिशत के बाद वापसी बहुत मुश्किल हो जाती है।"),
        ("streak", f"अब समझिए कि हर ट्रेड में जोखिम क्यों मायने रखता है। हर ट्रेडर कभी न कभी लगातार दस ट्रेड हारता है। अगर आप हर ट्रेड में 1 प्रतिशत का जोखिम लेते हैं, तो दस हार के बाद आप {down[1]} प्रतिशत नीचे होते हैं। 2 प्रतिशत जोखिम पर {down[2]} प्रतिशत नीचे। 5 प्रतिशत पर {down[5]} प्रतिशत नीचे। "
                   f"और 10 प्रतिशत पर {down[10]} प्रतिशत नीचे, जिसकी भरपाई के लिए {rec10} प्रतिशत का मुनाफ़ा चाहिए।"),
        ("limits", "ये क्या साबित नहीं करता। गणित सटीक है, पर ये नहीं बताता कि आपके सिस्टम में बढ़त है या नहीं। असली बाज़ार में गैप और स्लिपेज होते हैं, इसलिए असली नुकसान आपकी योजना से बड़ा हो सकता है। "
                   "नियम: एंट्री से पहले तय करें कि अधिकतम नुकसान कितना होगा, उसे छोटा रखें, आमतौर पर हर ट्रेड में खाते का 1 प्रतिशत या उससे कम, और गणित को अपनी रक्षा करने दें। ये शिक्षा है, निवेश सलाह नहीं।"),
    ]
    vis = {
        "title": lambda d: lv.title_scene(heading, sub, tag="TRADING LESSON"),
        "idea": lambda d: lv.text_scene("Losses and gains are not symmetric", [
            "Start with 100. Lose 50% and you have 50.", "To get back to 100 you must gain 100% on that 50.",
            "The deeper the hole, the steeper the climb."], tag="THE IDEA", accent=lv.GOLD,
            rule="Rule: avoiding a deep loss is worth more than chasing a big win."),
        "need": lambda d: lv.bars_scene("The gain needed to get back to even", [
            (f"After a {L}% loss", need[L], lv.RED if L >= 50 else lv.GOLD, "%") for L in (10, 20, 30, 50, 70)],
            note="Recovery needed = 1 / (1 - loss) - 1. Pure arithmetic, no market data."),
        "streak": lambda d: lv.bars_scene("After ten losses in a row", [
            (f"Risking {r}% per trade", -down[r], lv.RED if r >= 5 else lv.GOLD, "%") for r in risks],
            note="Account change after 10 straight losing trades: 1 - (1 - risk)^10. Smaller risk keeps you in the game."),
        "limits": lambda d: lv.text_scene("What this does NOT prove", [
            "It does not show that your system has an edge", "Real losses can exceed the planned size (gaps, slippage)",
            "Position sizing protects you; it does not create profit"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: set the maximum loss before you enter, usually 1% of the account or less per trade."),
    }
    scenes = [_scene(k, t, hi[i][1], vis[k]) for i, (k, t) in enumerate(en)]
    return {
        "id": "rm01", "heading": heading, "sub": sub, "regions": ["us", "in"], "langs": ["en", "hi"] if region == "in" else ["en"],
        "facts": {"need50": 100.0, "need10": need[10], "need70": need[70], "down1": down[1], "down10": down[10]},
        "title": {"en": "Why a 50% Loss Needs a 100% Gain (The Math Every Trader Must Know)",
                  "hi": "50% नुकसान की भरपाई के लिए 100% मुनाफ़ा क्यों चाहिए | हर ट्रेडर को ये गणित जानना ज़रूरी"},
        "desc": {"en": "The arithmetic of losses: why recovery gets harder than the loss itself, and how risk per trade decides whether ten bad trades are a bruise or a disaster.",
                 "hi": "नुकसान का गणित: भरपाई नुकसान से ज़्यादा मुश्किल क्यों होती है, और हर ट्रेड का जोखिम कैसे तय करता है कि दस बुरे ट्रेड एक खरोंच हैं या तबाही।"},
        "tags": {"en": ["risk management", "position sizing", "trading psychology", "drawdown", "trading lesson", "stock market education"],
                 "hi": ["risk management hindi", "position sizing", "trading lesson hindi", "stock market hindi", "drawdown"]},
        "scenes": scenes,
    }


# ───────────────────────────── rs01 (computed live) ─────────────────────────

def _dd_study(region):
    """Next-12-month return by distance below the 52-week high, on the region's universe."""
    import yfinance as yf, statistics
    cfg = E.REGIONS[region]
    syms = cfg["universe"]
    raw = yf.download([s + cfg["suffix"] for s in syms], period="6y", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
    rows = []
    for s in syms:
        try:
            df = raw[s + cfg["suffix"]].dropna(subset=["Close", "High"])
            if len(df) < 520:
                continue
            c, h = df["Close"].values, df["High"].rolling(252, min_periods=200).max().values
            for i in range(252, len(df) - 250, 21):
                dd = (c[i] / h[i] - 1) * 100
                fwd = (c[i + 250] / c[i] - 1) * 100
                worst = (min(c[i:i + 251]) / c[i] - 1) * 100
                rows.append((dd, fwd, worst))
        except Exception:
            continue
    if len(rows) < 200:
        raise RuntimeError("rs01: too few samples")
    def grp(lo, hi):
        g = [r for r in rows if lo < r[0] <= hi]
        return {"n": len(g), "avg": round(sum(r[1] for r in g) / len(g), 1), "neg": round(sum(1 for r in g if r[1] < 0) / len(g) * 100),
                "worst": round(sum(r[2] for r in g) / len(g), 1)} if g else None
    allg = {"n": len(rows), "avg": round(sum(r[1] for r in rows) / len(rows), 1), "neg": round(sum(1 for r in rows if r[1] < 0) / len(rows) * 100),
            "worst": round(sum(r[2] for r in rows) / len(rows), 1)}
    return {"shallow": grp(-10, 1), "mid": grp(-30, -10), "deep": grp(-100, -30), "all": allg, "stocks": len(syms)}


def build_rs01(region):
    d = _dd_study(region)
    sh, mi, de, al = d["shallow"], d["mid"], d["deep"], d["all"]
    if not (sh and mi and de):
        raise RuntimeError("rs01: an empty bucket")
    mk = E.REGIONS[region]["market"]
    if de["avg"] < al["avg"]:
        concl_en, concl_hi = "The deepest discounts did not beat the average. A bigger fall was not a better entry.", "सबसे गहरी गिरावट वाले शेयर औसत से बेहतर नहीं निकले। ज़्यादा गिरावट बेहतर एंट्री साबित नहीं हुई।"
    elif de["avg"] > al["avg"] + 3:
        concl_en, concl_hi = "The deepest discounts did better on average, but that is probably flattered by survivorship, because we only include companies that recovered enough to still be large today.", "सबसे गहरी गिरावट वाले शेयरों ने औसतन बेहतर किया, पर ये शायद बचे हुए शेयरों की वजह से बेहतर दिख रहा है, क्योंकि हमने सिर्फ़ वही कंपनियाँ लीं जो उबरकर आज भी बड़ी हैं।"
    else:
        concl_en, concl_hi = "There was no clear difference between deep discounts and the average stock.", "गहरी गिरावट वाले शेयरों और औसत शेयर में कोई साफ़ फ़र्क़ नहीं दिखा।"
    heading, sub = "Does buying a big fall pay?", f"A 12-month test on {d['stocks']} {mk} stocks"
    en = [
        ("title", f"Buying a stock after a big fall feels smart. It feels like a discount. We tested whether it actually pays, on {d['stocks']} {mk} stocks, using the next twelve months of returns."),
        ("idea", "The method is simple. Every month, for every stock, we measured how far it sat below its 52 week high. Then we looked at what it returned over the following year. We grouped the results into three buckets: close to the high, ten to thirty percent below, and more than thirty percent below."),
        ("avg", f"Here are the averages. Stocks within 10 percent of their high returned {sh['avg']} percent over the next year. Those 10 to 30 percent below returned {mi['avg']} percent. Those more than 30 percent below returned {de['avg']} percent. The average across all {al['n']:,} samples was {al['avg']} percent. {concl_en}"),
        ("risk", f"Now the risk. After twelve months, {sh['neg']} percent of the close to high group were down, against {de['neg']} percent of the deep discount group. During the year the deepest group dipped about {abs(de['worst'])} percent on average from its starting price. A discount can keep getting cheaper."),
        ("limits", "What this does not prove. We tested only large stocks that exist today, so companies that collapsed are missing, and that flatters the deep discount results. Averages also hide big differences between individual stocks. "
                   "Rule: do not buy a stock only because it fell. Look for a reason, such as the trend turning up, and size the position small. This is education, not investment advice."),
    ]
    hi = [
        ("title", f"बड़ी गिरावट के बाद शेयर ख़रीदना समझदारी लगता है। जैसे छूट मिल रही हो। हमने {d['stocks']} बड़े शेयरों पर अगले बारह महीनों के रिटर्न से परखा कि क्या ये सच में फ़ायदा देता है।"),
        ("idea", "तरीक़ा सीधा है। हर महीने, हर शेयर के लिए हमने देखा कि वो अपने 52 हफ़्ते के ऊँचे स्तर से कितना नीचे है। फिर देखा कि अगले एक साल में उसने कितना रिटर्न दिया। नतीजों को तीन हिस्सों में बाँटा: ऊँचे स्तर के पास, दस से तीस प्रतिशत नीचे, और तीस प्रतिशत से ज़्यादा नीचे।"),
        ("avg", f"औसत देखिए। ऊँचे स्तर के 10 प्रतिशत के भीतर वाले शेयरों ने अगले साल {sh['avg']} प्रतिशत दिया। 10 से 30 प्रतिशत नीचे वालों ने {mi['avg']} प्रतिशत। 30 प्रतिशत से ज़्यादा नीचे वालों ने {de['avg']} प्रतिशत। सभी {al['n']:,} नमूनों का औसत {al['avg']} प्रतिशत रहा। {concl_hi}"),
        ("risk", f"अब जोखिम। बारह महीने बाद, ऊँचे स्तर के पास वाले समूह के {sh['neg']} प्रतिशत मामले नुकसान में थे, जबकि गहरी गिरावट वाले समूह के {de['neg']} प्रतिशत। साल के दौरान सबसे गहरे समूह में शुरुआती भाव से औसतन करीब {abs(de['worst'])} प्रतिशत की और गिरावट आई। सस्ता शेयर और सस्ता हो सकता है।"),
        ("limits", "ये क्या साबित नहीं करता। हमने सिर्फ़ वही बड़े शेयर परखे जो आज मौजूद हैं, इसलिए जो कंपनियाँ डूब गईं वो गायब हैं, और इससे गहरी गिरावट वाले नतीजे बेहतर दिखते हैं। औसत अलग-अलग शेयरों के बड़े फ़र्क़ को भी छिपा देते हैं। "
                   "नियम: सिर्फ़ इसलिए शेयर न ख़रीदें कि वो गिरा है। कोई वजह ढूँढें, जैसे ट्रेंड का पलटना, और पोज़िशन छोटी रखें। ये शिक्षा है, निवेश सलाह नहीं।"),
    ]
    vis = {
        "title": lambda dd: lv.title_scene(heading, sub, tag="RESEARCH"),
        "idea": lambda dd: lv.text_scene("How we tested it", [
            "Every month, every stock: how far below its 52-week high?", "Then: what did it return over the next 12 months?",
            "Three buckets: near the high, 10-30% below, 30%+ below"], tag="THE METHOD", accent=lv.GOLD),
        "avg": lambda dd: lv.bars_scene("Average return over the next 12 months", [
            ("Near the high (0-10% below)", sh["avg"], lv.GREEN, "%"), ("10-30% below", mi["avg"], lv.GOLD, "%"),
            ("30%+ below", de["avg"], lv.RED if de["avg"] < al["avg"] else lv.GREEN, "%"), ("All samples", al["avg"], lv.MUTED, "%")],
            note=f"{al['n']:,} stock-months, {d['stocks']} {mk} stocks, daily data. Our own test."),
        "risk": lambda dd: lv.bars_scene("The risk side", [
            ("Down after 12m: near the high", -sh["neg"], lv.GOLD, "%"), ("Down after 12m: 10-30% below", -mi["neg"], lv.GOLD, "%"),
            ("Down after 12m: 30%+ below", -de["neg"], lv.RED, "%"), ("Avg dip in the year: 30%+ below", de["worst"], lv.RED, "%")],
            note="Negative bars = share of cases that ended the year lower, and the average dip along the way."),
        "limits": lambda dd: lv.text_scene("What this does NOT prove", [
            "Only large stocks that exist today were tested (survivorship bias)", "Averages hide big differences between stocks",
            "Past results do not guarantee future results"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: never buy only because a stock fell. Need a reason, and keep the size small."),
    }
    scenes = [_scene(k, t, hi[i][1], vis[k]) for i, (k, t) in enumerate(en)]
    return {
        "id": "rs01", "heading": heading, "sub": sub, "regions": ["us", "in"], "langs": ["en", "hi"] if region == "in" else ["en"],
        "facts": {"shallow": sh["avg"], "mid": mi["avg"], "deep": de["avg"], "all": al["avg"], "samples": al["n"]},
        "title": {"en": f"Does Buying a Big Fall Pay? We Tested {d['stocks']} {mk} Stocks Over 12 Months",
                  "hi": f"क्या गिरावट में ख़रीदना फ़ायदेमंद है? {d['stocks']} बड़े शेयरों पर 12 महीने का टेस्ट"},
        "desc": {"en": "Is a stock that has fallen a lot a bargain or a trap? Our own 12-month test, with the risk side and the limits stated honestly.",
                 "hi": "बहुत गिरा हुआ शेयर सौदा है या जाल? हमारा अपना 12 महीने का टेस्ट, जोखिम और सीमाओं के साथ, पूरी ईमानदारी से।"},
        "tags": {"en": ["buy the dip", "stock market research", "52 week high", "value investing", "trading lesson", "stock market education"],
                 "hi": ["buy the dip hindi", "share market research", "stock market hindi", "trading lesson hindi", "investing"]},
        "scenes": scenes,
    }


# ───────────────────────────── au01 (our own ledger) ────────────────────────

_EXIT_EN = [("TARGET", "it reached its target"), ("TRAIL", "the trailing stop was hit"), ("TIME", "the time limit ended the trade"),
            ("CAP", "the loss cap was hit"), ("HARD STOP", "the stop-loss was hit"), ("STOP", "the stop-loss was hit")]
_EXIT_HI = {"it reached its target": "ट्रेड अपने टार्गेट तक पहुँचा", "the trailing stop was hit": "ट्रेलिंग स्टॉप लग गया", "the stop-loss was hit": "स्टॉप-लॉस लग गया",
            "the time limit ended the trade": "समय-सीमा ख़त्म होने पर ट्रेड बंद हुआ", "the loss cap was hit": "नुकसान की सीमा लग गई"}


def _ledger_rows():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)
    v = gspread.authorize(creds).open("Ai360tradingAlgo").worksheet("History").get_all_values()
    head, rows = v[0], v[1:]
    return [dict(zip(head, r)) for r in rows if r and r[0].strip()]


def _f(x):
    try:
        return float(str(x).replace("%", "").replace(",", "").strip())
    except Exception:
        return None


def build_au01(region):
    if region != "in":
        raise RuntimeError("au01 is India-only (our ledger)")
    import yfinance as yf
    rows = []
    for r in _ledger_rows():
        p, ep, xp = _f(r.get("P/L %")), _f(r.get("Entry Price")), _f(r.get("Exit Price"))
        if p is None or not ep or not xp or "NSE:" not in r.get("Symbol", ""):
            continue
        if not r.get("Entry Date") or not r.get("Exit Date") or "Swing" not in (r.get("Trade Type", "") + r.get("Strategy", "")) and "STRONG" not in r.get("Strategy", "") and "RETEST" not in r.get("Strategy", ""):
            continue
        rows.append((p, r, ep, xp))
    if len(rows) < 8:
        raise RuntimeError("au01: not enough closed swing trades")
    best, worst = max(rows, key=lambda x: x[0]), min(rows, key=lambda x: x[0])
    n, wins = len(rows), sum(1 for x in rows if x[0] > 0)
    import datetime as dt

    def reason(r):
        txt = re.sub(r"[^A-Za-z ]", " ", r.get("Exit Reason", "")).upper()
        for k, v in _EXIT_EN:
            if k in txt:
                return v
        return "the exit rule closed the trade"

    def chart(item, label, accent):
        p, r, ep, xp = item
        sym = r["Symbol"].replace("NSE:", "")
        d0 = dt.date.fromisoformat(r["Entry Date"][:10]) - dt.timedelta(days=75)
        d1 = dt.date.fromisoformat(r["Exit Date"][:10]) + dt.timedelta(days=14)
        df = yf.download(sym + ".NS", start=str(d0), end=str(d1), interval="1d", progress=False, auto_adjust=False)
        df.columns = df.columns.get_level_values(0)
        c = df["Close"].dropna()
        series = [(i.date(), float(v)) for i, v in c.items()]
        def idx(day):
            day = dt.date.fromisoformat(day[:10])
            best_i, best_d = 0, 10 ** 9
            for k, (d, _) in enumerate(series):
                if abs((d - day).days) < best_d:
                    best_i, best_d = k, abs((d - day).days)
            return best_i
        ie, ix = idx(r["Entry Date"]), idx(r["Exit Date"])
        sl = _f(r.get("Initial SL"))
        panel = [("TRADE", sym, lv.WHITE), ("ENTRY", f"Rs {E._num(ep)}   {r['Entry Date'][:10]}", lv.WHITE), ("EXIT", f"Rs {E._num(xp)}   {r['Exit Date'][:10]}", lv.WHITE),
                 ("RESULT (paper trade)", f"{p:+.1f}%", lv.GREEN if p >= 0 else lv.RED)]
        return lambda dur: lv.chart_scene(f"{label}: {sym}", series, tag="OUR OWN LEDGER", level=sl, level_label="INITIAL STOP-LOSS" if sl else "",
                                          markers=[(ie, "ENTRY", lv.BLUE), (ix, "EXIT", lv.GREEN if p >= 0 else lv.RED)], panel=panel, accent=accent)(dur), sym, r

    vb, sb, rb = chart(best, "Our best closed trade", lv.GREEN)
    vw, sw, rw = chart(worst, "Our worst closed trade", lv.RED)
    D = lambda r, k: r[k][:10]
    en = [
        ("title", "Most trading channels show you their winners. We are going to show you our best closed trade and our worst, from our own live paper ledger, with the numbers exactly as they were logged."),
        ("best", f"Our best closed swing trade: {sb}. Entered on {D(rb, 'Entry Date')} at {best[2]:.1f} rupees, with the initial stop-loss under the entry. It closed on {D(rb, 'Exit Date')} at {best[3]:.1f} rupees, a gain of {best[0]:.1f} percent, because {reason(rb)}."),
        ("worst", f"Our worst closed swing trade: {sw}. Entered on {D(rw, 'Entry Date')} at {worst[2]:.1f} rupees. It closed on {D(rw, 'Exit Date')} at {worst[3]:.1f} rupees, a loss of {abs(worst[0]):.1f} percent, because {reason(rw)}. "
                  "The stop did its job. It turned a possible bigger loss into a known, small one."),
        ("ledger", f"Zoom out. We have {n} closed swing and positional trades in this ledger. {wins} of them were winners, which is {round(wins / n * 100)} percent. A trade ledger is only honest if the bad trades are in it."),
        ("limits", "What this does not prove. This is a paper ledger, not real money, so real fills and emotions would be different. It is also a small sample, so these results may not repeat. "
                   "Rule: judge any strategy, ours included, by its whole ledger and not by its best trade. This is education, not investment advice."),
    ]
    hi = [
        ("title", "ज़्यादातर ट्रेडिंग चैनल सिर्फ़ अपने विनर्स दिखाते हैं। हम आपको अपना सबसे अच्छा बंद ट्रेड और सबसे बुरा दोनों दिखाएँगे, अपने लाइव पेपर लेजर से, उन्हीं आँकड़ों के साथ जैसे वे दर्ज हुए थे।"),
        ("best", f"हमारा सबसे अच्छा बंद स्विंग ट्रेड: {sb}। {D(rb, 'Entry Date')} को {best[2]:.1f} रुपये पर एंट्री हुई, एंट्री के नीचे शुरुआती स्टॉप-लॉस के साथ। {D(rb, 'Exit Date')} को ये {best[3]:.1f} रुपये पर बंद हुआ, {best[0]:.1f} प्रतिशत का मुनाफ़ा, क्योंकि {_EXIT_HI.get(reason(rb), 'एग्ज़िट नियम से ट्रेड बंद हुआ')}।"),
        ("worst", f"हमारा सबसे बुरा बंद स्विंग ट्रेड: {sw}। {D(rw, 'Entry Date')} को {worst[2]:.1f} रुपये पर एंट्री हुई। {D(rw, 'Exit Date')} को ये {worst[3]:.1f} रुपये पर बंद हुआ, {abs(worst[0]):.1f} प्रतिशत का नुकसान, क्योंकि {_EXIT_HI.get(reason(rw), 'एग्ज़िट नियम से ट्रेड बंद हुआ')}। "
                  "स्टॉप ने अपना काम किया। उसने संभावित बड़े नुकसान को एक तय, छोटे नुकसान में बदल दिया।"),
        ("ledger", f"अब पूरी तस्वीर देखिए। इस लेजर में हमारे {n} बंद स्विंग और पोज़िशनल ट्रेड हैं। इनमें से {wins} विनर थे, यानी {round(wins / n * 100)} प्रतिशत। ट्रेड लेजर तभी ईमानदार है जब उसमें बुरे ट्रेड भी हों।"),
        ("limits", "ये क्या साबित नहीं करता। ये पेपर लेजर है, असली पैसा नहीं, इसलिए असली फ़िल और भावनाएँ अलग होंगी। ये छोटा नमूना भी है, तो ये नतीजे दोहराए न भी जाएँ। "
                   "नियम: किसी भी रणनीति को, हमारी भी, उसके पूरे लेजर से परखें, सबसे अच्छे ट्रेड से नहीं। ये शिक्षा है, निवेश सलाह नहीं।"),
    ]
    heading, sub = "Our best and worst closed trades", "From our own live paper ledger, nothing hidden"
    vis = {
        "title": lambda d_: lv.title_scene(heading, sub, tag="TRADING LESSON"),
        "best": vb, "worst": vw,
        "ledger": lambda d_: lv.bars_scene("Our swing and positional ledger", [
            ("Closed trades", n, lv.MUTED, ""), ("Winners", wins, lv.GREEN, ""), ("Losers", -(n - wins), lv.RED, "")],
            note=f"Win rate {round(wins / n * 100)}%. Paper trading, every closed trade included."),
        "limits": lambda d_: lv.text_scene("What this does NOT prove", [
            "It is a paper ledger, not real money", "It is a small sample, results may not repeat",
            "One best trade says little about a whole strategy"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: judge a strategy by its whole ledger, not its best trade."),
    }
    scenes = [_scene(k, t, hi[i][1], vis[k]) for i, (k, t) in enumerate(en)]
    return {
        "id": "au01", "heading": heading, "sub": sub, "regions": ["in"], "langs": ["en", "hi"],
        "facts": {"best": f"{best[0]:.1f}", "worst": f"{abs(worst[0]):.1f}", "n": n, "wins": wins},
        "title": {"en": "Our Best and Worst Closed Trades (Real Ledger, Nothing Hidden)", "hi": "हमारे सबसे अच्छे और सबसे बुरे ट्रेड (असली लेजर, कुछ भी छिपा नहीं)"},
        "desc": {"en": "A trading channel that shows its losers. Our best and worst closed paper trades from the live ledger, with the stop-loss and exit reason explained.",
                 "hi": "एक ट्रेडिंग चैनल जो अपने हारे हुए ट्रेड भी दिखाता है। हमारे लाइव लेजर के सबसे अच्छे और सबसे बुरे बंद पेपर ट्रेड, स्टॉप-लॉस और एग्ज़िट वजह के साथ।"},
        "tags": {"en": ["trading ledger", "trade review", "stop loss", "swing trading", "trading lesson", "stock market india"],
                 "hi": ["trading ledger", "trade review hindi", "stop loss", "swing trading hindi", "share market hindi"]},
        "scenes": scenes,
    }


BUILDERS = {"rc01": build_rc01, "rm01": build_rm01, "rs01": build_rs01, "au01": build_au01}
LESSON_REGIONS = {"rc01": ["us", "in"], "rm01": ["us", "in"], "rs01": ["us", "in"], "au01": ["in"]}   # which regions each lesson supports
