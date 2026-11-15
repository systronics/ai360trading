"""
lesson_builders3.py - three more evergreen lessons (v1.0, 2026-11-15), written before the Claude plan ended (18 Nov 2026) so the weekly lesson queue keeps running into early 2027 without any AI:
    sw01  Do tight stops protect a swing trade? (our own swing exit backtest: hold 20 days vs stop-and-target vs trailing stop)
    ct01  Why tiny stops lose: trading costs measured in R (our own 5-minute intraday backtest)
    sv01  Why every backtest looks better than reality: survivorship bias (a worked imaginary example + our own recent out-of-sample numbers)
Same contract as lesson_builders.py / lesson_builders2.py: English is the master (lesson_bank.quality_gate: a real number from our data, a 'Rule:' line, an honest limit, no hype),
Hindi must keep every number (numbers_preserved). Registered into lesson_builders.BUILDERS / QUEUE at the bottom of lesson_builders.py (fail-open).
All real numbers come from tests recorded in CLAUDE.md (swing_bt.py / intraday_bt.py / publish_signal_lists.py); the survivorship example is labelled imaginary.
"""

import lesson_visuals as lv
from lesson_builders2 import _pack


# ───────────────────────────── sw01: do tight stops protect a swing trade? ─────────────────────────────

def build_sw01(region):
    hold, win, stop_rule, trail = "2.10", 54, "0.52", "0.49"
    heading, sub = "Do tight stop losses protect you?", "We tested one swing signal five ways"
    en = [
        ("title", "Everyone says a stop loss is the first rule of trading. But what does a stop actually do to the results? We tested it on one swing trading signal, with real data, and the answer surprised us."),
        ("setup", "The signal is simple. A stock closes at a new 50 day high, on strong volume, with the market trend up. We tested it on 207 large Indian stocks from 2018 to 2026, and we counted a cost of 0.25 percent on every trade. "
                  "Then we kept the same entries and only changed how we exit."),
        ("result", f"Simply holding for 20 trading days made {hold} percent per trade, and {win} percent of the trades won. When we added a stop about two average daily ranges below the entry, with a target above it, "
                   f"the result fell to {stop_rule} percent per trade. A trailing stop gave {trail} percent. Same entries, far less profit."),
        ("why", "Why did this happen? A tight stop gets hit by ordinary noise, and many of those stocks then recover and move up. Under the stop rule, the typical trade was a loss of about 3 percent. "
                "And the stop did not remove the bad trades. The worst tenth of the trades still lost about 8 percent with stops, against about 10 percent when simply holding, because prices can gap straight through a stop."),
        ("limits", "What this does not prove. This is one signal, tested on stocks that survived to today, with daily prices, so the stop fills here are optimistic. The years 2018 and 2026 so far were negative. "
                   "It does not say that stops are useless for you. Rule: do not rely on a tight stop alone. Keep every position small enough that a 10 percent loss is survivable, and decide your exit before you enter. This is education, not investment advice."),
    ]
    hi = [
        ("title", "सब कहते हैं कि स्टॉप लॉस ट्रेडिंग का पहला नियम है। पर स्टॉप असल में नतीजों पर क्या असर डालता है? हमने एक स्विंग सिग्नल पर असली डेटा से इसे परखा, और जवाब ने हमें चौंका दिया।"),
        ("setup", "सिग्नल सीधा है। कोई शेयर 50 दिन के नए ऊँचे स्तर पर बंद होता है, ज़ोरदार वॉल्यूम के साथ, और बाज़ार का रुख़ ऊपर है। हमने इसे 2018 से 2026 तक 207 बड़े भारतीय शेयरों पर परखा, और हर ट्रेड पर 0.25 प्रतिशत की लागत गिनी। "
                  "फिर वही एंट्री रखीं और सिर्फ़ निकलने का तरीक़ा बदला।"),
        ("result", f"बिना स्टॉप के सिर्फ़ 20 ट्रेडिंग दिन रखने पर हर ट्रेड में औसत {hold} प्रतिशत मिला, और {win} प्रतिशत ट्रेड जीते। जब हमने एंट्री से लगभग दो औसत दैनिक दायरे नीचे स्टॉप और ऊपर टारगेट लगाया, "
                   f"तो नतीजा गिरकर हर ट्रेड में {stop_rule} प्रतिशत रह गया। ट्रेलिंग स्टॉप ने {trail} प्रतिशत दिया। एंट्री वही, मुनाफ़ा बहुत कम।"),
        ("why", "ऐसा क्यों हुआ? तंग स्टॉप रोज़ की सामान्य हलचल में ही लग जाता है, और उनमें से कई शेयर बाद में सँभलकर ऊपर चले जाते हैं। स्टॉप वाले नियम में आम ट्रेड लगभग 3 प्रतिशत का घाटा था। "
                "और स्टॉप ने ख़राब ट्रेड हटाए नहीं। सबसे ख़राब दसवें हिस्से के ट्रेड स्टॉप के साथ भी लगभग 8 प्रतिशत हारे, जबकि बस रखने पर लगभग 10 प्रतिशत, क्योंकि भाव स्टॉप को सीधे लाँघकर गैप में जा सकता है।"),
        ("limits", "ये क्या साबित नहीं करता। ये एक ही सिग्नल है, उन शेयरों पर परखा जो आज तक बचे रहे, और रोज़ के भावों से, इसलिए यहाँ स्टॉप का भराव ज़रूरत से अच्छा दिखता है। 2018 और 2026 अब तक नकारात्मक रहे। "
                   "ये नहीं कहता कि आपके लिए स्टॉप बेकार हैं। नियम: सिर्फ़ तंग स्टॉप के भरोसे मत रहिए। हर पोज़िशन इतनी छोटी रखिए कि 10 प्रतिशत का घाटा सहा जा सके, और एंट्री से पहले ही निकलने की योजना तय कर लीजिए। ये शिक्षा है, निवेश की सलाह नहीं।"),
    ]
    vis = {
        "title": lambda d: lv.title_scene(heading, sub, tag="TRADING LESSON"),
        "setup": lambda d: lv.text_scene("The test", [
            "Signal: new 50 day high, strong volume, market up", "207 large Indian stocks, 2018 to 2026",
            "Cost counted: 0.25% on every trade"], tag="THE SETUP", accent=lv.GOLD,
            rule="Rule: test an exit on the same entries, change one thing."),
        "result": lambda d: lv.bars_scene("Average result per trade, same entries", [
            ("Hold 20 days, no stop", float(hold), lv.GREEN, "%"), ("Stop + target", float(stop_rule), lv.GOLD, "%"),
            ("Trailing stop", float(trail), lv.BLUE, "%")], note="After costs, 2018 to 2026, 207 stocks. Past data, survivors only."),
        "why": lambda d: lv.bars_scene("The bad tail: worst tenth of trades", [
            ("With stops", -8.0, lv.GOLD, "%"), ("Simply holding", -10.0, lv.RED, "%")],
            note="Gaps can jump a stop, so it trims the tail only a little. Median trade under the stop rule: about -3%."),
        "limits": lambda d: lv.text_scene("What this does NOT prove", [
            "One signal, survivors only, daily prices", "Stop fills here are optimistic",
            "2018 and 2026 so far were negative years"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: size every position so a 10% loss is survivable; plan the exit first."),
    }
    facts = {"hold": hold, "win": win, "stop_rule": stop_rule, "trail": trail, "stocks": 207, "cost": 0.25}
    return _pack("sw01", heading, sub, facts,
                 {"en": "Do Tight Stop Losses Protect You? We Tested It on 207 Stocks",
                  "hi": "क्या तंग स्टॉप लॉस आपको बचाता है? हमने 207 शेयरों पर परखा"},
                 {"en": "One swing trading signal, the same entries, five different exits. What a stop loss really did to the results, with our own real numbers and the limits of the test.",
                  "hi": "एक स्विंग सिग्नल, वही एंट्री, पाँच अलग निकासी तरीक़े। स्टॉप लॉस ने नतीजों पर असल में क्या असर डाला, हमारे अपने असली आँकड़ों और टेस्ट की सीमाओं के साथ।"},
                 {"en": ["stop loss", "swing trading", "risk management", "backtest", "trading lesson", "stock market education"],
                  "hi": ["stop loss hindi", "swing trading hindi", "risk management hindi", "trading lesson hindi", "stock market hindi"]},
                 en, hi, vis, region)


# ───────────────────────────── ct01: costs measured in R ─────────────────────────────

def build_ct01(region):
    cost, stop = 0.10, 0.25
    r_small = round(cost / stop, 1)
    r_big = round(cost / 1.0, 1)
    heading, sub = "Why tiny stops lose money", "Costs do not shrink when your stop does"
    en = [
        ("title", "Why do trades with very small stop losses so often end up losing money? The answer is not the market. It is the cost of trading, and it does not shrink when your stop does."),
        ("cost", f"Every trade pays brokerage, taxes and slippage. We assume {cost:.2f} percent for a round trip. Now measure that cost in units of your risk, called R. If your stop is {stop} percent away, the cost alone is {cost:.2f} divided by {stop}, "
                 f"which is {r_small} R. You start the trade {r_small} R behind. With a 1 percent stop the same cost is only {r_big} R."),
        ("ours", "We tested simple intraday rules on real 5 minute candles, on 32 liquid symbols, from April 2022 to 2026. An opening range breakout lost 0.21 R per trade. A break of the previous day high lost 0.09 R. "
                 "Random entries, as a control, lost 0.10 R. A popular 5 EMA alert candle rule lost 0.94 R."),
        ("why", "The stops in these rules were tiny, only 0.16 to 0.35 percent away. So costs took about 0.3 to 0.6 R before the market even moved. A rule needs a real edge just to pay that, and none of the simple ones had it."),
        ("limits", "What this does not prove. We tested only simple long only price rules, on 32 liquid symbols, with an approximate cost. It does not prove that no intraday method can work. It shows that these common ones did not survive costs. "
                   "Rule: before you take a trade with a tiny stop, divide your total cost by the stop distance; if costs take a big share of your risk, widen the plan or skip the trade. This is education, not investment advice."),
    ]
    hi = [
        ("title", "बहुत छोटे स्टॉप लॉस वाले ट्रेड अक्सर घाटे में क्यों खत्म होते हैं? इसका जवाब बाज़ार नहीं है। वजह है ट्रेडिंग की लागत, जो आपका स्टॉप छोटा होने पर भी छोटी नहीं होती।"),
        ("cost", f"हर ट्रेड में ब्रोकरेज, टैक्स और स्लिपेज देना पड़ता है। हम आना-जाना मिलाकर {cost:.2f} प्रतिशत मानते हैं। अब इस लागत को अपने जोखिम की इकाई, यानी आर में नापिए। अगर आपका स्टॉप {stop} प्रतिशत दूर है, तो अकेली लागत {cost:.2f} भाग {stop} हुई, "
                 f"यानी {r_small} आर। आप ट्रेड {r_small} आर पीछे से शुरू करते हैं। 1 प्रतिशत के स्टॉप पर वही लागत सिर्फ़ {r_big} आर है।"),
        ("ours", "हमने असली 5 मिनट की कैंडल पर, 32 आसानी से बिकने वाले सिंबल पर, अप्रैल 2022 से 2026 तक सीधे इंट्राडे नियम परखे। ओपनिंग रेंज ब्रेकआउट हर ट्रेड में 0.21 आर हारा। पिछले दिन के ऊँचे स्तर का ब्रेक 0.09 आर हारा। "
                 "तुलना के लिए रैंडम एंट्री 0.10 आर हारी। एक मशहूर 5 ईएमए अलर्ट कैंडल नियम 0.94 आर हारा।"),
        ("why", "इन नियमों के स्टॉप बहुत छोटे थे, सिर्फ़ 0.16 से 0.35 प्रतिशत दूर। इसलिए बाज़ार के हिलने से पहले ही लागत लगभग 0.3 से 0.6 आर खा गई। इतना चुकाने के लिए ही नियम में असली बढ़त चाहिए, और कोई भी सीधा नियम उसे नहीं दिखा सका।"),
        ("limits", "ये क्या साबित नहीं करता। हमने सिर्फ़ सीधे, सिर्फ़ ख़रीद वाले भाव-नियम परखे, 32 आसानी से बिकने वाले सिंबल पर, अंदाज़े की लागत के साथ। ये साबित नहीं करता कि कोई भी इंट्राडे तरीक़ा काम नहीं कर सकता। ये दिखाता है कि ये आम तरीक़े लागत के बाद टिक नहीं पाए। "
                   "नियम: छोटे स्टॉप वाला ट्रेड लेने से पहले कुल लागत को स्टॉप की दूरी से भाग दीजिए; अगर लागत आपके जोखिम का बड़ा हिस्सा खा जाए, तो योजना बड़ी कीजिए या ट्रेड छोड़ दीजिए। ये शिक्षा है, निवेश की सलाह नहीं।"),
    ]
    vis = {
        "title": lambda d: lv.title_scene(heading, sub, tag="TRADING LESSON"),
        "cost": lambda d: lv.text_scene("Cost measured in R", [
            f"Round trip cost: {cost:.2f}%", f"Stop {stop}% away: cost = {cost:.2f} / {stop} = {r_small} R",
            f"Stop 1% away: cost = {r_big} R"], tag="THE MATHS", accent=lv.GOLD,
            rule="Rule: cost divided by stop distance = how far behind you start."),
        "ours": lambda d: lv.bars_scene("Our 5 minute test, average R per trade", [
            ("Opening range breakout", -0.21, lv.RED, " R"), ("Previous day high break", -0.09, lv.GOLD, " R"),
            ("Random entries (control)", -0.10, lv.BLUE, " R"), ("5 EMA alert candle", -0.94, lv.RED, " R")],
            note="32 liquid symbols, April 2022 to 2026, cost 0.10% per round trip."),
        "why": lambda d: lv.text_scene("Tiny stops, big cost share", [
            "Stops in these rules: 0.16% to 0.35% away", "Costs ate about 0.3 to 0.6 R first",
            "The rule needs a real edge just to break even"], tag="THE WHY", accent=lv.RED,
            rule="Rule: small stops multiply the damage of costs."),
        "limits": lambda d: lv.text_scene("What this does NOT prove", [
            "Simple long only rules, 32 symbols, 2022 to 2026", "Cost is an approximation",
            "It does not prove no intraday method can work"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: divide cost by stop distance before every tiny-stop trade."),
    }
    facts = {"cost": cost, "stop": stop, "r_small": r_small, "orb": 0.21, "pdh": 0.09, "rand": 0.10, "ema5": 0.94, "symbols": 32}
    return _pack("ct01", heading, sub, facts,
                 {"en": "Why Tiny Stop Losses Lose Money: Costs Measured in R",
                  "hi": "छोटे स्टॉप लॉस क्यों घाटा देते हैं: आर में नापी गई लागत"},
                 {"en": "Trading costs do not shrink when your stop does. A worked example in R, and what our own 5 minute intraday test showed after costs.",
                  "hi": "आपका स्टॉप छोटा होने पर ट्रेडिंग की लागत छोटी नहीं होती। आर में एक हल किया हुआ उदाहरण, और हमारे अपने 5 मिनट के इंट्राडे टेस्ट ने लागत के बाद क्या दिखाया।"},
                 {"en": ["trading costs", "intraday trading", "stop loss", "risk management", "trading lesson", "stock market education"],
                  "hi": ["trading cost hindi", "intraday trading hindi", "stop loss hindi", "risk management hindi", "trading lesson hindi"]},
                 en, hi, vis, region)


# ───────────────────────────── sv01: survivorship bias ─────────────────────────────

def build_sv01(region):
    n, bad, avg_all, avg_bad = 100, 20, 10, -40
    surv_avg = round((n * avg_all - bad * avg_bad) / (n - bad), 1)
    heading, sub = "Why every backtest looks too good", "Survivorship bias, with numbers"
    en = [
        ("title", "Almost every backtest you see online looks better than what you will get in real life. One of the biggest reasons is called survivorship bias, and it is easy to understand with a small example."),
        ("example", f"Here is an imaginary example, only to show the mechanism. Take {n} stocks that gained {avg_all} percent on average. {bad} of them fell apart, losing {abs(avg_bad)} percent on average, and then dropped out of the stock list. "
                    f"If you test only the {n - bad} stocks still on the list today, their average gain is {surv_avg} percent. Same market, but the result looks more than double as good."),
        ("ours", "Our own tests have this bias too, because they use today's large stocks. In our five year test on 194 stocks, a 50 day breakout signal made 3.58 percent per trade over 20 days, against 1.14 percent for random entries. "
                 "But in the newer period, 2025 to 2026, it made 1.55 percent against 0.12 percent for random entries, and 2026 so far is negative at minus 0.8 percent."),
        ("trust", "So we trust the newest numbers, which were not used to build the rule, much more than the long history. Expect less in real life than the headline number, and treat any single backtest as a best case."),
        ("limits", "What this does not prove. The imaginary numbers only show the mechanism, and real index changes are smaller. We cannot rebuild the lists of past stocks that disappeared, so we cannot measure our exact bias. "
                   "Rule: treat every backtest as a best case, and give the most recent out of sample result the most weight. This is education, not investment advice."),
    ]
    hi = [
        ("title", "ऑनलाइन दिखने वाला लगभग हर बैकटेस्ट असली ज़िंदगी में मिलने वाले नतीजे से बेहतर दिखता है। इसकी एक बड़ी वजह को सर्वाइवरशिप बायस कहते हैं, और एक छोटे उदाहरण से ये आसानी से समझ आता है।"),
        ("example", f"ये एक काल्पनिक उदाहरण है, सिर्फ़ तरीक़ा समझाने के लिए। मान लीजिए {n} शेयर औसतन {avg_all} प्रतिशत बढ़े। उनमें से {bad} बिखर गए, औसतन {abs(avg_bad)} प्रतिशत गँवाकर, और फिर शेयरों की सूची से बाहर हो गए। "
                    f"अगर आप आज भी सूची में बचे सिर्फ़ {n - bad} शेयरों पर टेस्ट करें, तो उनका औसत फ़ायदा {surv_avg} प्रतिशत आता है। बाज़ार वही, पर नतीजा दोगुने से भी बेहतर दिखता है।"),
        ("ours", "हमारे अपने टेस्ट में भी ये झुकाव है, क्योंकि वो आज के बड़े शेयरों पर चलते हैं। 194 शेयरों पर हमारे पाँच साल के टेस्ट में 50 दिन के ब्रेकआउट सिग्नल ने 20 दिन में हर ट्रेड में 3.58 प्रतिशत कमाया, जबकि रैंडम एंट्री ने 1.14 प्रतिशत। "
                 "पर नए दौर, 2025 से 2026 में, उसने 1.55 प्रतिशत कमाया और रैंडम एंट्री ने 0.12 प्रतिशत, और 2026 अब तक नकारात्मक है, घटा 0.8 प्रतिशत।"),
        ("trust", "इसलिए हम लंबे इतिहास से ज़्यादा नए आँकड़ों पर भरोसा करते हैं, जो नियम बनाने में इस्तेमाल नहीं हुए थे। असली ज़िंदगी में सुर्ख़ी वाले आँकड़े से कम की उम्मीद रखिए, और किसी भी अकेले बैकटेस्ट को सबसे अच्छी हालत मानिए।"),
        ("limits", "ये क्या साबित नहीं करता। काल्पनिक आँकड़े सिर्फ़ तरीक़ा दिखाते हैं, और असली सूचकांक में बदलाव इससे छोटे होते हैं। हम पुराने, गायब हो चुके शेयरों की सूचियाँ दोबारा नहीं बना सकते, इसलिए अपने सटीक झुकाव को नाप नहीं सकते। "
                   "नियम: हर बैकटेस्ट को सबसे अच्छी हालत मानिए, और सबसे ताज़ा, नए डेटा वाले नतीजे को सबसे ज़्यादा वज़न दीजिए। ये शिक्षा है, निवेश की सलाह नहीं।"),
    ]
    vis = {
        "title": lambda d: lv.title_scene(heading, sub, tag="TRADING LESSON"),
        "example": lambda d: lv.bars_scene("Imaginary example: the same market", [
            (f"All {n} stocks", float(avg_all), lv.BLUE, "%"), (f"Only the {n - bad} survivors", surv_avg, lv.GOLD, "%")],
            note=f"Imaginary numbers: {bad} stocks lost {abs(avg_bad)}% and left the list. The sample now looks more than double as good."),
        "ours": lambda d: lv.bars_scene("Our 50 day breakout signal, 20 days", [
            ("Five year test, signal", 3.58, lv.GREEN, "%"), ("Five year test, random", 1.14, lv.BLUE, "%"),
            ("2025 to 2026, signal", 1.55, lv.GOLD, "%"), ("2025 to 2026, random", 0.12, lv.BLUE, "%")],
            note="After costs. Today's large stocks only (survivors). 2026 so far: -0.8%."),
        "trust": lambda d: lv.text_scene("What to trust", [
            "The newest numbers, not used to build the rule", "Expect less than the headline number",
            "Treat one backtest as a best case"], tag="THE TAKEAWAY", accent=lv.GREEN,
            rule="Rule: weight recent out of sample results most."),
        "limits": lambda d: lv.text_scene("What this does NOT prove", [
            "The example is imaginary, only the mechanism is real", "We cannot rebuild lists of vanished stocks",
            "So our exact bias is unknown"], tag="THE LIMITS", accent=lv.GOLD,
            rule="Rule: every backtest is a best case; trust the newest result most."),
    }
    facts = {"survivors_avg": surv_avg, "signal_5y": 3.58, "random_5y": 1.14, "signal_new": 1.55, "random_new": 0.12, "stocks": 194}
    return _pack("sv01", heading, sub, facts,
                 {"en": "Why Every Backtest Looks Too Good: Survivorship Bias Explained",
                  "hi": "हर बैकटेस्ट ज़रूरत से अच्छा क्यों दिखता है: सर्वाइवरशिप बायस"},
                 {"en": "Survivorship bias in one worked example, and what it means for our own five year test: the long history looks good, the newest numbers are much smaller.",
                  "hi": "सर्वाइवरशिप बायस एक हल किए हुए उदाहरण में, और हमारे अपने पाँच साल के टेस्ट के लिए इसका मतलब: लंबा इतिहास अच्छा दिखता है, पर सबसे नए आँकड़े बहुत छोटे हैं।"},
                 {"en": ["survivorship bias", "backtesting", "trading mistakes", "risk management", "trading lesson", "stock market education"],
                  "hi": ["survivorship bias hindi", "backtesting hindi", "trading lesson hindi", "stock market hindi", "risk management hindi"]},
                 en, hi, vis, region)


BUILDERS = {"sw01": build_sw01, "ct01": build_ct01, "sv01": build_sv01}
QUEUE = ["sw01", "ct01", "sv01"]
