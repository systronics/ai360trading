"""
lesson_builders2.py — three more evergreen risk-maths lessons (v1.0, 2026-10-31)
================================================================================
The weekly lesson queue (lesson_builders.QUEUE) was running out on 21 Nov. These add:
    rm03  Expectancy: the number that decides if a system makes money (our own 5-year backtest numbers)
    rm02  Position sizing in one formula (worked example, computed)
    rm04  How likely is a ten-loss streak really (exact probability, computed)
Same contract as lesson_builders.py: English is the master (quality_gate), Hindi must keep every number.
Registered into lesson_builders.BUILDERS / QUEUE at the bottom of that file (fail-open).
"""

import lesson_engine as E
import lesson_visuals as lv


def _scene(kind, en, hi, visual):
    return {"kind": kind, "text": {"en": en, "hi": hi}, "visual": visual}


def _pack(lid, heading, sub, facts, title, desc, tags, en, hi, vis, region):
    scenes = [_scene(k, t, hi[i][1], vis[k]) for i, (k, t) in enumerate(en)]
    return {"id": lid, "heading": heading, "sub": sub, "regions": ["us", "in"],
            "langs": ["en", "hi"] if region == "in" else ["en"], "facts": facts,
            "title": title, "desc": desc, "tags": tags, "scenes": scenes}


# ───────────────────────────── rm03: expectancy ─────────────────────────────

def build_rm03(region):
    s = E.BACKTEST_IN
    w, aw, al = s["win_rate"], s["avg_win"], abs(s["avg_loss"])
    lw = 100 - w
    a = round(w / 100 * aw, 1)
    b = round(lw / 100 * al, 1)
    exp = round(a - b, 1)
    trap = round(0.70 * 2 - 0.30 * 6, 1)
    heading, sub = "Expectancy: does your system make money?", "Win rate is not the point"
    en = [
        ("title", "Most traders chase a high win rate. The number that really decides whether a system makes money is called expectancy. It tells you how much you earn, on average, every time you take a trade."),
        ("formula", "Expectancy equals win rate times average win, minus loss rate times average loss. It is one line of arithmetic. If the result is positive, the system makes money over many trades. If it is negative, the system loses, however good it feels on the days it wins."),
        ("ours", f"Here are our own numbers, from a {s['years']} year test of {s['trades']} trades on {s['stocks']} large Indian stocks. Only {w} percent of the trades won. But the average win was {aw} percent and the average loss was {al} percent. "
                 f"So 0.{w} times {aw} is {a}, and 0.{lw} times {al} is {b}. The difference is about {exp} percent per trade. The measured average was {s['avg_trade']} percent, and the small gap is rounding."),
        ("trap", f"Now the trap. A system that wins 70 percent of the time, with an average win of 2 percent and an average loss of 6 percent, has an expectancy of {trap} percent per trade. It wins most days and still loses money. "
                 "A coin flip with wins and losses of 5 percent each sits at exactly 0."),
        ("limits", "What this does not prove. These numbers come from past data on stocks that survived to today, they ignore brokerage and slippage, and one very strong year pulled the average up, so the future may not look the same. "
                   "Rule: judge a system by its expectancy and the size of its losses, not by its win rate, and always test it with costs included. This is education, not investment advice."),
    ]
    hi = [
        ("title", "ज़्यादातर ट्रेडर ऊँचा जीत प्रतिशत ढूँढते हैं। असली फ़ैसला एक संख्या करती है जिसे एक्स्पेक्टेंसी कहते हैं। ये बताती है कि हर ट्रेड पर औसतन आप कितना कमाते हैं।"),
        ("formula", "एक्स्पेक्टेंसी बराबर जीत प्रतिशत गुणा औसत मुनाफ़ा, घटा हार प्रतिशत गुणा औसत नुकसान। ये गणित की एक पंक्ति है। नतीजा धनात्मक है तो सिस्टम बहुत ट्रेडों में कमाता है। ऋणात्मक है तो घाटा देता है, चाहे जीत वाले दिन कितने भी अच्छे लगें।"),
        ("ours", f"ये हमारे अपने आँकड़े हैं, {s['stocks']} बड़े भारतीय शेयरों के {s['trades']} ट्रेडों के {s['years']} साल के टेस्ट से। सिर्फ़ {w} प्रतिशत ट्रेड जीते। लेकिन औसत मुनाफ़ा {aw} प्रतिशत था और औसत नुकसान {al} प्रतिशत। "
                 f"तो 0.{w} गुणा {aw} हुआ {a}, और 0.{lw} गुणा {al} हुआ {b}। फ़र्क़ लगभग {exp} प्रतिशत प्रति ट्रेड है। नापा हुआ औसत {s['avg_trade']} प्रतिशत था, ये छोटा फ़र्क़ राउंडिंग का है।"),
        ("trap", f"अब जाल देखिए। जो सिस्टम 70 प्रतिशत बार जीतता है, पर औसत मुनाफ़ा 2 प्रतिशत और औसत नुकसान 6 प्रतिशत है, उसकी एक्स्पेक्टेंसी {trap} प्रतिशत प्रति ट्रेड है। वो ज़्यादातर दिन जीतकर भी पैसा गँवाता है। "
                 "5 प्रतिशत के बराबर जीत और हार वाला सिक्का उछालना ठीक 0 पर रहता है।"),
        ("limits", "ये क्या साबित नहीं करता। ये आँकड़े पुराने डेटा से हैं, उन शेयरों के जो आज तक बचे रहे, इनमें ब्रोकरेज और स्लिपेज शामिल नहीं है, और एक बहुत अच्छे साल ने औसत ऊपर खींचा, इसलिए भविष्य ऐसा न भी हो। "
                   "नियम: सिस्टम को उसकी एक्स्पेक्टेंसी और नुकसान के आकार से परखें, जीत प्रतिशत से नहीं, और टेस्ट हमेशा लागत जोड़कर करें। ये शिक्षा है, निवेश सलाह नहीं।"),
    ]
    vis = {
        "title": lambda d: lv.title_scene(heading, sub, tag="TRADING LESSON"),
        "formula": lambda d: lv.text_scene("The one-line formula", [
            "Expectancy = win rate x average win", "          minus loss rate x average loss",
            "Positive over many trades = it makes money"], tag="THE FORMULA", accent=lv.GOLD,
            rule="Rule: a system is judged by expectancy, not by how often it wins."),
        "ours": lambda d: lv.bars_scene("Our 5-year breakout test (per trade)", [
            (f"Wins ({w}% of trades)", aw, lv.GREEN, "%"), (f"Losses ({lw}% of trades)", -al, lv.RED, "%"),
            ("Expectancy", exp, lv.GOLD, "%")], note=f"Expectancy = {w / 100:.2f} x {aw} - {lw / 100:.2f} x {al}. Past data, costs excluded."),
        "trap": lambda d: lv.bars_scene("A high win rate can still lose", [
            ("Win 70%, small wins", trap, lv.RED, "%"), ("Coin flip, 5% each", 0.0, lv.GOLD, "%"),
            (f"Our test, win {w}%", exp, lv.GREEN, "%")], note="Expectancy per trade. Big winners beat a high win rate."),
        "limits": lambda d: lv.text_scene("What this does NOT prove", [
            "Past data on surviving stocks (survivorship bias)", "Brokerage and slippage are not included",
            "One strong year lifted the average"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: judge a system by expectancy and loss size, with costs included."),
    }
    facts = {"win": w, "avg_win": aw, "avg_loss": al, "exp": exp, "trades": s["trades"], "trap": trap}
    return _pack("rm03", heading, sub, facts,
                 {"en": "Expectancy: The Number That Decides If Your Trading System Makes Money",
                  "hi": "एक्स्पेक्टेंसी: वो संख्या जो तय करती है कि आपका ट्रेडिंग सिस्टम कमाएगा या नहीं"},
                 {"en": "Why win rate is not the point: expectancy explained with the numbers from our own five year breakout test, and why a 70 percent win rate can still lose money.",
                  "hi": "जीत प्रतिशत क्यों असली बात नहीं है: हमारे अपने पाँच साल के ब्रेकआउट टेस्ट के आँकड़ों से एक्स्पेक्टेंसी, और 70 प्रतिशत जीत के बावजूद नुकसान क्यों।"},
                 {"en": ["expectancy trading", "win rate vs risk reward", "trading system", "risk management", "trading lesson", "stock market education"],
                  "hi": ["expectancy hindi", "risk management hindi", "trading lesson hindi", "stock market hindi", "win rate"]},
                 en, hi, vis, region)


# ───────────────────────────── rm02: position sizing ────────────────────────

def build_rm02(region):
    c = E.REGIONS[region]["ccy"]
    cu = "rupees" if region == "in" else "dollars"
    acct, risk_pct, price = 100000, 1, 100
    risk_amt = acct * risk_pct // 100
    rows = {}
    for stop in (2, 5, 10):
        sh = risk_amt // stop
        rows[stop] = (sh, sh * price)
    heading, sub = "Position sizing in one formula", f"Risk {risk_pct}% of the account per trade"
    s5, s2, s10 = rows[5], rows[2], rows[10]
    en = [
        ("title", "Most traders decide how many shares to buy by feel, or by how much money they have. Professionals do it the other way round. They first decide how much they can afford to lose on the trade, and the number of shares follows from that."),
        ("formula", "The formula is one line. Number of shares equals the money you are willing to lose on this trade, divided by the loss per share if your stop is hit. The stop decides the size, not your excitement."),
        ("example", f"A worked example. Your account is {c} {acct}. You risk {risk_pct} percent per trade, so you can lose {c} {risk_amt}. A stock trades at {price} and your stop is {stop_gap(5)} below the entry. "
                    f"The loss per share is {stop_gap(5)}. So {risk_amt} divided by {stop_gap(5)} gives {s5[0]} shares, a position worth {c} {s5[1]}."),
        ("compare", f"Now change only the stop. With a tight stop of {stop_gap(2)}, the same {c} {risk_amt} of risk allows {s2[0]} shares, worth {c} {s2[1]}. With a wide stop of {stop_gap(10)}, it allows only {s10[0]} shares, worth {c} {s10[1]}. "
                    f"In all three cases, if the stop is hit, you lose {c} {risk_amt}. The risk stays fixed, and the position size adjusts."),
        ("limits", "What this does not prove. Sizing protects you, but it does not create profit, and it does not guarantee the stop will fill at your price: gaps and slippage can make a real loss bigger than planned. "
                   "Rule: shares equal the money you can lose divided by the loss per share, and keep the risk to about 1 percent of the account or less. This is education, not investment advice."),
    ]
    hi = [
        ("title", "ज़्यादातर ट्रेडर शेयरों की संख्या अंदाज़े से या जेब में पड़े पैसे से तय करते हैं। पेशेवर उल्टा करते हैं। वो पहले तय करते हैं कि इस ट्रेड में कितना नुकसान सह सकते हैं, और शेयरों की संख्या उसी से निकलती है।"),
        ("formula", "सूत्र एक पंक्ति का है। शेयरों की संख्या बराबर इस ट्रेड में जितना नुकसान सहने को तैयार हैं, भाग स्टॉप लगने पर प्रति शेयर होने वाला नुकसान। साइज़ स्टॉप तय करता है, आपका उत्साह नहीं।"),
        ("example", f"एक उदाहरण। आपका खाता {c} {acct} का है। आप हर ट्रेड में {risk_pct} प्रतिशत जोखिम लेते हैं, यानी {c} {risk_amt} तक गँवा सकते हैं। शेयर {price} पर है और स्टॉप एंट्री से {stop_gap(5)} नीचे है। "
                    f"प्रति शेयर नुकसान {stop_gap(5)} है। तो {risk_amt} भाग {stop_gap(5)} हुआ {s5[0]} शेयर, यानी {c} {s5[1]} की पोज़िशन।"),
        ("compare", f"अब सिर्फ़ स्टॉप बदलिए। {stop_gap(2)} के तंग स्टॉप पर उतने ही {c} {risk_amt} के जोखिम में {s2[0]} शेयर आते हैं, यानी {c} {s2[1]}। {stop_gap(10)} के चौड़े स्टॉप पर सिर्फ़ {s10[0]} शेयर, यानी {c} {s10[1]}। "
                    f"तीनों हालात में स्टॉप लगा तो आप {c} {risk_amt} ही गँवाते हैं। जोखिम तय रहता है, और पोज़िशन का साइज़ बदलता है।"),
        ("limits", "ये क्या साबित नहीं करता। साइज़िंग आपकी रक्षा करती है, पर मुनाफ़ा नहीं बनाती, और ये गारंटी नहीं देती कि स्टॉप आपकी कीमत पर ही भरेगा: गैप और स्लिपेज से असली नुकसान योजना से बड़ा हो सकता है। "
                   "नियम: शेयर बराबर जितना नुकसान सह सकते हैं भाग प्रति शेयर नुकसान, और जोखिम खाते का लगभग 1 प्रतिशत या कम रखें। ये शिक्षा है, निवेश सलाह नहीं।"),
    ]
    vis = {
        "title": lambda d: lv.title_scene(heading, sub, tag="TRADING LESSON"),
        "formula": lambda d: lv.text_scene("The one-line formula", [
            "Shares = money you can lose", "         / loss per share at the stop",
            "The stop decides the size"], tag="THE FORMULA", accent=lv.GOLD,
            rule="Rule: fix the loss first, then let the stop size the position."),
        "example": lambda d: lv.text_scene("A worked example", [
            f"Account {c} {acct}, risk {risk_pct}% = {c} {risk_amt}", f"Price {price}, stop {stop_gap(5)} below",
            f"{risk_amt} / {stop_gap(5)} = {s5[0]} shares ({c} {s5[1]})"], tag="THE EXAMPLE", accent=lv.GREEN,
            rule="Rule: shares = risk amount / loss per share."),
        "compare": lambda d: lv.bars_scene("Same risk, different stops: shares allowed", [
            (f"Stop {stop_gap(2)} (tight)", s2[0], lv.GOLD, " sh"), (f"Stop {stop_gap(5)}", s5[0], lv.GREEN, " sh"),
            (f"Stop {stop_gap(10)} (wide)", s10[0], lv.BLUE, " sh")], note=f"Each case risks {c} {risk_amt}. Wider stop = smaller position."),
        "limits": lambda d: lv.text_scene("What this does NOT prove", [
            "Sizing does not create profit", "Gaps and slippage can make the loss bigger",
            "A stop is not a guaranteed fill price"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: shares = loss you can afford / loss per share; risk about 1% or less."),
    }
    facts = {"acct": acct, "risk": risk_amt, "shares5": s5[0], "shares2": s2[0], "shares10": s10[0]}
    return _pack("rm02", heading, sub, facts,
                 {"en": "Position Sizing in One Formula: How Many Shares Should You Buy?",
                  "hi": "पोज़िशन साइज़िंग एक सूत्र में: कितने शेयर ख़रीदें?"},
                 {"en": f"How professionals size a trade: fix the loss first, then let the stop decide the number of shares. A worked example with a {c} {acct} account.",
                  "hi": f"पेशेवर ट्रेड का साइज़ कैसे तय करते हैं: पहले नुकसान तय करें, फिर स्टॉप शेयरों की संख्या तय करता है। {c} {acct} के खाते का एक उदाहरण।"},
                 {"en": ["position sizing", "how many shares to buy", "risk management", "stop loss", "trading lesson", "stock market education"],
                  "hi": ["position sizing hindi", "kitne share kharide", "risk management hindi", "stop loss", "trading lesson hindi"]},
                 en, hi, vis, region)


def stop_gap(n):
    return n


# ───────────────────────────── rm04: losing streaks ─────────────────────────

def streak_prob(n, k, p_loss):
    """Exact probability of at least one run of k losses in n trades (dynamic programming)."""
    cur = [0.0] * k          # cur[j] = P(current run of j losses, no k-run yet)
    cur[0] = 1.0
    hit = 0.0
    for _ in range(n):
        nxt = [0.0] * k
        for j, pr in enumerate(cur):
            if not pr:
                continue
            nxt[0] += pr * (1 - p_loss)
            if j + 1 == k:
                hit += pr * p_loss
            else:
                nxt[j + 1] += pr * p_loss
        cur = nxt
    return hit


def build_rm04(region):
    s = E.BACKTEST_IN
    w = s["win_rate"]
    pl = (100 - w) / 100
    n = 100
    p5, p8, p10 = (round(streak_prob(n, k, pl) * 100) for k in (5, 8, 10))
    q10 = round(streak_prob(n, 10, 0.40) * 100)
    heading, sub = "How likely is a ten-loss streak?", "Exact odds, not feelings"
    en = [
        ("title", "Every trader fears a long losing streak, and most believe it means their system has broken. So how likely is a streak, really? Let us calculate it exactly instead of guessing."),
        ("idea", f"Take our breakout test, where {w} percent of trades won. That means each trade has a {100 - w} percent chance of losing. Losses do not arrive evenly spaced, they cluster by pure chance, just like heads and tails in a row."),
        ("odds", f"Over {n} trades, the chance of at least one run of 5 losses in a row is {p5} percent. For 8 losses in a row it is {p8} percent. And for 10 losses in a row it is {p10} percent. "
                 f"A trader who wins 60 percent of the time still faces a {q10} percent chance of seeing 10 losses in a row over {n} trades."),
        ("size", "So a long streak is not proof that something broke. It is part of the normal distribution. What decides whether you survive it is position size. "
                 "Risk 1 percent per trade and ten straight losses leave you about 9.6 percent down, which is painful but recoverable. Risk 10 percent per trade and the same streak takes about 65 percent of the account."),
        ("limits", "What this does not prove. The calculation assumes every trade is independent with a fixed win rate, and real markets can cluster losses even more, especially in a bad regime. "
                   "Rule: expect a long losing streak, size every trade so that ten losses in a row would not end your account, and never judge a system by a handful of trades. This is education, not investment advice."),
    ]
    hi = [
        ("title", "हर ट्रेडर लंबे घाटे की लड़ी से डरता है, और ज़्यादातर मानते हैं कि इसका मतलब है कि सिस्टम टूट गया। तो असल में ऐसी लड़ी कितनी संभावित है? अंदाज़े की जगह इसे सटीक गणित से निकालते हैं।"),
        ("idea", f"हमारे ब्रेकआउट टेस्ट को लीजिए, जहाँ {w} प्रतिशत ट्रेड जीते। यानी हर ट्रेड के हारने की संभावना {100 - w} प्रतिशत है। हार बराबर दूरी पर नहीं आतीं, वो संयोग से गुच्छों में आती हैं, जैसे सिक्के में लगातार चित या पट।"),
        ("odds", f"{n} ट्रेडों में, लगातार कम से कम 5 हार की संभावना {p5} प्रतिशत है। लगातार 8 हार की {p8} प्रतिशत। और लगातार 10 हार की {p10} प्रतिशत। "
                 f"जो ट्रेडर 60 प्रतिशत बार जीतता है, उसके सामने भी {n} ट्रेडों में लगातार 10 हार देखने की {q10} प्रतिशत संभावना रहती है।"),
        ("size", "इसलिए लंबी लड़ी का मतलब ये नहीं कि कुछ टूट गया। ये सामान्य वितरण का हिस्सा है। आप बचेंगे या नहीं, ये पोज़िशन साइज़ तय करता है। "
                 "हर ट्रेड में 1 प्रतिशत जोखिम लें तो लगातार दस हार के बाद लगभग 9.6 प्रतिशत नीचे होंगे, जो दर्दनाक है पर भरपाई हो सकती है। हर ट्रेड में 10 प्रतिशत जोखिम लें तो वही लड़ी खाते का लगभग 65 प्रतिशत ले जाती है।"),
        ("limits", "ये क्या साबित नहीं करता। गणना मानती है कि हर ट्रेड स्वतंत्र है और जीत प्रतिशत तय है, जबकि असली बाज़ार में हार और ज़्यादा गुच्छों में आ सकती हैं, ख़ासकर बुरे दौर में। "
                   "नियम: लंबी हार की लड़ी की उम्मीद रखें, हर ट्रेड का साइज़ ऐसा रखें कि लगातार दस हार भी खाता न ख़त्म करें, और कुछ ट्रेडों से सिस्टम को कभी न परखें। ये शिक्षा है, निवेश सलाह नहीं।"),
    ]
    vis = {
        "title": lambda d: lv.title_scene(heading, sub, tag="TRADING LESSON"),
        "idea": lambda d: lv.text_scene("Losses cluster by chance", [
            f"{w}% of our breakout trades won", f"So each trade loses {100 - w}% of the time",
            "Losses arrive in clumps, like heads in a row"], tag="THE IDEA", accent=lv.GOLD,
            rule="Rule: a losing streak is normal, not proof of a broken system."),
        "odds": lambda d: lv.bars_scene(f"Chance of a losing streak in {n} trades", [
            ("5 losses in a row", p5, lv.GOLD, "%"), ("8 losses in a row", p8, lv.GOLD, "%"),
            ("10 losses in a row", p10, lv.RED, "%")], note=f"Exact calculation, {w}% win rate, independent trades."),
        "size": lambda d: lv.bars_scene("After ten losses in a row", [
            ("Risking 1% per trade", -9.6, lv.GREEN, "%"), ("Risking 10% per trade", -65.1, lv.RED, "%")],
            note="Account change: 1 - (1 - risk)^10. Position size decides survival."),
        "limits": lambda d: lv.text_scene("What this does NOT prove", [
            "Assumes independent trades and a fixed win rate", "Real markets can cluster losses even more",
            "A few trades prove nothing about a system"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: size every trade so ten losses in a row are survivable."),
    }
    facts = {"win": w, "p5": p5, "p8": p8, "p10": p10, "q10": q10, "trades": n}
    return _pack("rm04", heading, sub, facts,
                 {"en": "How Likely Is a 10-Loss Streak? The Exact Odds Every Trader Should Know",
                  "hi": "लगातार 10 हार कितनी संभावित है? हर ट्रेडर को जाननी चाहिए सटीक संभावना"},
                 {"en": f"The exact probability of a losing streak over {n} trades, using the {w} percent win rate from our own breakout test, and why position size decides who survives it.",
                  "hi": f"{n} ट्रेडों में लगातार हार की सटीक संभावना, हमारे अपने ब्रेकआउट टेस्ट के {w} प्रतिशत जीत दर से, और पोज़िशन साइज़ कैसे तय करता है कि कौन बचेगा।"},
                 {"en": ["losing streak", "trading psychology", "risk management", "win rate", "trading lesson", "stock market education"],
                  "hi": ["losing streak hindi", "risk management hindi", "trading lesson hindi", "stock market hindi", "win rate"]},
                 en, hi, vis, region)


BUILDERS = {"rm03": build_rm03, "rm02": build_rm02, "rm04": build_rm04}
QUEUE = ["rm03", "rm02", "rm04"]
