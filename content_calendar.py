"""
AI360Trading — Content Calendar v3.0
======================================
v3.0 CHANGES (May 2026):

ADDED: 52-week education course — get_todays_education_topic()
  - Returns topic WITH "week" number calculated from COURSE_START
  - Week auto-advances every 7 days from May 15, 2026
  - Progressive: Basics → Technical → Fundamental → Advanced → Expert
  - Each topic has slides for generate_education.py
  - Title format: "Stock Market Kya Hai | Week 1 | AI360 Trading"

KEPT: All day-based topics for generate_articles.py and other generators
  - MONDAY_TOPICS, TUESDAY_TOPICS etc. unchanged
  - get_todays_article_topic() unchanged

WHY 52-week course is better:
  - Viewers come back every week to continue the series
  - YouTube recommends series content (watch time increases)
  - "Week 1" in title creates urgency (catch up!)
  - Beginner → Advanced progression builds loyal audience

Target countries: India, USA, UK, UAE, Canada, Australia, Brazil

Author: AI360Trading Automation
Last Updated: May 2026
"""

from datetime import date, datetime

# ══════════════════════════════════════════════════════════════════════
# 52-WEEK EDUCATION COURSE
# Starts: May 15, 2026 (COURSE_START)
# Week auto-calculated daily — never needs manual update
# ══════════════════════════════════════════════════════════════════════

COURSE_START = date(2026, 5, 15)  # Week 1 start — NEVER change this

COURSE_52_WEEKS = [
    # ── PHASE 1: FOUNDATIONS (Weeks 1-10) ─────────────────────────────
    {
        "title": "Stock Market Kya Hai",
        "title_en": "What is the Stock Market",
        "category": "Stock Market Basics",
        "level": "Beginner",
        "description": "Basics: Shares, NSE, BSE explained simply",
        "target_audience": "Complete beginners — India, USA, UK, Global",
        "slides": [
            {"heading": "Stock Market Kya Hota Hai",
             "points": ["Companies shares issue karti hain paise raise karne ke liye", "Aap shares khareedte hain toh company ke hisse ke maalik ban jaate hain", "NSE aur BSE India ke do major stock exchanges hain", "New York Stock Exchange duniya ka sabse bada exchange hai", "Stock market ek aisa platform hai jahan buyers aur sellers milte hain"]},
            {"heading": "Share Kya Hota Hai",
             "points": ["Share company ki ownership ka ek chhota hissa hota hai", "Agar Reliance ke 1 lakh shares hain aur aapke paas 100 hain", "Toh aap 0.001% ke maalik hain", "Share price supply aur demand se decide hoti hai", "Jab zyada log khareedte hain price badhti hai — simple economics"]},
            {"heading": "NSE vs BSE — Kya Antar Hai",
             "points": ["BSE 1875 mein bana — Asia ka sabse purana exchange", "NSE 1992 mein bana — technology aur speed mein aage", "Nifty 50 = NSE ka index, top 50 companies", "Sensex = BSE ka index, top 30 companies", "Dono pe same stocks trade hote hain — price almost same rehti hai"]},
            {"heading": "Stock Market Mein Paisa Kaise Banta Hai",
             "points": ["Capital appreciation: share ki price badhne se profit", "Dividends: company apne profit ka hissa shareholders ko deti hai", "Example: Infosys 2010 mein Rs.100, 2024 mein Rs.1500 — 15x return", "FD mein 6-7% annual vs good stocks mein 12-15% annual potential", "Risk hai — isliye samajhke invest karo, blindly nahi"]},
            {"heading": "Kaise Shuru Karein — Step by Step",
             "points": ["Step 1: Demat account kholein — Zerodha ya Dhan — 10 minute mein online", "Step 2: PAN card aur Aadhaar se KYC complete karein", "Step 3: Bank account link karein", "Step 4: Small amount se shuru karein — Rs.1000 bhi chalega", "Step 5: Pehle 1 mahina sirf dekhein, samjhein, fir invest karein"]},
        ],
    },
    {
        "title": "Demat Account Kaise Kholein",
        "title_en": "How to Open a Demat Account",
        "category": "Getting Started",
        "level": "Beginner",
        "description": "Complete demat account opening guide for Indians",
        "target_audience": "First-time investors India",
        "slides": [
            {"heading": "Demat Account Kya Hota Hai", "points": ["Demat = dematerialised — physical share certificates ki jagah digital record", "Jaise bank account mein paise safe rehte hain, demat mein shares safe rehte hain", "India mein NSDL aur CDSL do depositories hain jahan shares store hote hain", "Zerodha, Groww, Dhan, Upstox — sab demat account providers hain", "Bina demat account ke stock market mein invest karna possible nahi"]},
            {"heading": "Best Broker Kaunsa Hai — 2026", "points": ["Zerodha: India ka no.1 broker, Rs.20 per trade flat fee", "Dhan: best for options traders, good app, free delivery trades", "Groww: beginners ke liye simple, mutual funds bhi", "Upstox: Ratan Tata backed, good for beginners", "Paytm Money: direct mutual funds, low cost"]},
            {"heading": "Account Kholne ke Liye Kya Chahiye", "points": ["PAN card — mandatory, no exceptions", "Aadhaar card — for address proof", "Bank account — for fund transfer", "Mobile number linked to Aadhaar", "Selfie ya photo — for video KYC"]},
            {"heading": "Account Kholne ka Process — Step by Step", "points": ["Broker app download karein ya website pe jaayein", "Mobile number se register karein", "PAN aur Aadhaar details fill karein", "Video KYC complete karein — takes 5 minutes", "Bank account link karein — IFSC code se", "24-48 hours mein account active ho jaata hai"]},
            {"heading": "Important Charges Jo Aapko Pata Hone Chahiye", "points": ["Brokerage: Zerodha Rs.20 per trade, delivery free", "STT — Securities Transaction Tax: government ka charge", "GST: 18% on brokerage only", "DP charge: Rs.13-15 when you SELL shares only", "Annual maintenance: Rs.300-500 per year depending on broker"]},
        ],
    },
    {
        "title": "Mutual Funds vs Direct Stocks",
        "title_en": "Mutual Funds vs Direct Stocks — Which is Better For You",
        "category": "Investment Basics",
        "level": "Beginner",
        "description": "Complete comparison for Indian investors",
        "target_audience": "Beginners deciding between MF and direct stocks",
        "slides": [
            {"heading": "Mutual Fund Kya Hota Hai", "points": ["Mutual fund = aap aur hazaaron investors milke ek pool mein paisa daalte hain", "Professional fund manager decide karta hai kahan invest karna hai", "Diversification automatic milti hai — ek fund mein 30-50 stocks", "NAV = Net Asset Value — ek unit ki price", "SIP se Rs.500 se shuru kar sakte hain"]},
            {"heading": "Direct Stocks Kya Hote Hain", "points": ["Aap khud Reliance, TCS, HDFC jaisi companies ke shares khareedenge", "Aap khud research karenge — ya kisi analyst ko follow karenge", "Higher potential return — agar sahi stocks chunen", "Higher risk bhi — agar galat chunen ya galat time pe", "More involvement required — time aur knowledge dono"]},
            {"heading": "Mutual Fund Ke Fayde", "points": ["Professional management — expert decide karta hai", "Diversification — ek fund mein 30-50 stocks", "Rs.500 se SIP shuru possible — very accessible", "Tax efficient — ELSS funds mein 80C benefit", "Liquid — redemption 1-3 business days mein"]},
            {"heading": "Direct Stocks Ke Fayde", "points": ["Higher return potential — right stocks 5x-20x ho sakti hain", "Full control — aap khud decide karte ho", "Dividend income directly aata hai aapke account mein", "No expense ratio — mutual fund 0.5-2% annually charge karta hai", "Thrill of picking winners — very satisfying when right"]},
            {"heading": "Kisko Kya Chunna Chahiye", "points": ["Beginner + time nahi hai: index mutual fund se shuru karein", "Intermediate + thoda time hai: 50% MF + 50% direct stocks", "Active trader + research time hai: direct stocks with proper system", "Both can work together — do not choose, use both wisely", "Remember: best investment is one you actually understand and stick with"]},
        ],
    },
    {
        "title": "SIP — Systematic Investment Plan Complete Guide",
        "title_en": "SIP Complete Guide — How to Build Wealth Automatically",
        "category": "Wealth Building",
        "level": "Beginner",
        "description": "SIP explained with real numbers and compounding power",
        "target_audience": "Young professionals India — USA 401k parallel",
        "slides": [
            {"heading": "SIP Kya Hai — Simple Explanation", "points": ["SIP = har mahine fixed amount automatically invest hota hai", "Jaise EMI ka ulta — EMI mein paisa jaata hai, SIP mein paisa aata hai", "Market upar ho ya neeche — SIP automatically chalta rehta hai", "Rupee cost averaging: kabhi kam units, kabhi zyada units milte hain", "Long term mein average cost kam hoti hai — yeh magic hai SIP ka"]},
            {"heading": "Compounding — The 8th Wonder of the World", "points": ["Einstein ne compounding ko 8th wonder kaha tha", "Rs.5000/month SIP, 12% annual return, 20 saal baad = Rs.50 lakh", "Rs.10000/month SIP, 15% return, 25 saal = Rs.3.3 crore", "Key: start early, stay consistent, never stop in market crash", "Every year you delay costs you lakhs of rupees in the future"]},
            {"heading": "Best SIP Funds 2026 — Categories to Consider", "points": ["Nifty 50 Index Fund: lowest cost, matches market, best for beginners", "Flexicap Fund: fund manager chooses across all caps", "Small Cap Fund: highest risk, highest potential — 10+ year horizon", "ELSS Fund: tax saving under 80C + wealth creation", "Start with Nifty 50 index, add others as knowledge grows"]},
            {"heading": "SIP Kaise Shuru Karein — 3 Steps", "points": ["Step 1: Groww ya Kuvera pe account kholein — 5 minute process", "Step 2: Risk profile decide karein: conservative, moderate, aggressive", "Step 3: SIP amount set karein — even Rs.500 is fine to start", "Set auto-pay from bank — never miss an installment", "Review once a year — not every week, SIP needs patience not monitoring"]},
            {"heading": "SIP Ke Baare Mein Common Mistakes", "points": ["Galti 1: Market crash mein SIP band karna — biggest wealth killer", "Galti 2: Bahut saari funds mein invest karna — 2-3 enough hai", "Galti 3: Returns check karna har roz — SIP 10+ year investment hai", "Galti 4: Emergency fund banane se pehle SIP shuru karna", "Galti 5: Inflation ko ignore karna — 6% inflation khaata hai return"]},
        ],
    },
    {
        "title": "Technical Analysis Introduction",
        "title_en": "Technical Analysis Introduction — Reading Stock Charts",
        "category": "Technical Analysis",
        "level": "Beginner",
        "description": "Charts, price action, and why technical analysis works",
        "target_audience": "Beginners who want to understand charts",
        "slides": [
            {"heading": "Technical Analysis Kya Hai", "points": ["Price history use karke future price predict karne ki kala", "Charts pe patterns dekhna — jab yeh pattern aaya toh aaage kya hua", "Fundamental analysis = company ka value judge karna", "Technical analysis = price aur volume se timing judge karna", "Best traders dono use karte hain — FA quality ke liye, TA timing ke liye"]},
            {"heading": "Candlestick Chart Kaise Padhein", "points": ["Har candle 4 prices dikhati hai: Open, High, Low, Close", "Green/white candle = close > open = buyers jeet gaye", "Red/black candle = close < open = sellers jeet gaye", "Long wick = price tried to go there but was rejected", "Body size = strength of move — bada body = strong conviction"]},
            {"heading": "Trend — Sabse Important Concept", "points": ["Uptrend: higher highs aur higher lows — bulls control mein hain", "Downtrend: lower highs aur lower lows — bears control mein hain", "Sideways: range bound — neither side winning", "Rule: never fight the trend — trade WITH the trend", "Trend is your friend until it ends — classic wisdom"]},
            {"heading": "Volume — The Lie Detector of Charts", "points": ["Volume = kitne shares trade hue us session mein", "High volume pe price move = strong, institutional backed move", "Low volume pe price move = weak, may reverse", "Breakout pe high volume chahiye — warna false breakout", "Volume decreasing in trend = trend weakening — caution signal"]},
            {"heading": "Support aur Resistance — Foundation of TA", "points": ["Support = price jahan buyers dominant hain, price bounce karta hai", "Resistance = price jahan sellers dominant hain, price fall karta hai", "These levels exist because orders accumulate at round numbers", "Once support breaks it becomes resistance — role reversal", "Draw these on weekly chart first — most powerful levels"]},
        ],
    },
    {
        "title": "Candlestick Patterns Jo Actually Kaam Aate Hain",
        "title_en": "Candlestick Patterns That Actually Work",
        "category": "Technical Analysis",
        "level": "Beginner",
        "description": "5 most reliable candlestick patterns with real examples",
        "target_audience": "Chart beginners globally",
        "slides": [
            {"heading": "Kaunse Patterns Actually Kaam Karte Hain", "points": ["80+ patterns hain textbooks mein — sirf 5 kaam ke hain", "Reliability comes from context — not pattern alone", "Always need: right location, right volume, right trend", "Pattern without context = random noise", "Master 5 patterns well vs learn 50 patterns poorly"]},
            {"heading": "Bullish Engulfing — Institutional Buying Signal", "points": ["Chhota red candle — fir ek bada green candle jo pehle ko poora dhak le", "Matlab: sellers thak gaye, buyers ne strong entry li", "Most powerful at major support levels after downtrend", "High volume on green candle = confirmation of institutional buy", "Works on Nifty daily, US stocks weekly, Bitcoin 4-hour — everywhere"]},
            {"heading": "Pin Bar — Rejection Candle", "points": ["Chhota body, bahut lamba wick — price gaya wahan aur reject hua", "Hammer at support: buyers ne sellers ko crush kiya", "Shooting star at resistance: sellers ne buyers ko crush kiya", "Rule: wick should be 2.5x size of body minimum", "Stop loss just beyond the wick tip — very tight, very clean"]},
            {"heading": "Morning Star — Three Candle Reversal", "points": ["Teen candles ka pattern — powerful downtrend reversal signal", "Candle 1: big red — sellers in full control", "Candle 2: small candle or doji — indecision, selling slowing", "Candle 3: big green closing above midpoint of candle 1", "Volume should increase on candle 3 — confirmation needed"]},
            {"heading": "Inside Bar — The Coiled Spring", "points": ["Second candle ka range poori tarah first candle ke andar", "Market consolidating after big move — building energy", "Breakout above: buy, stop at inside bar low", "Breakout below: sell/short, stop at inside bar high", "Daily chart pe best — works great after strong trend moves"]},
        ],
    },
    {
        "title": "Support aur Resistance Masterclass",
        "title_en": "Support and Resistance Masterclass",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "Drawing levels that actually hold, role reversal concept",
        "target_audience": "Traders globally",
        "slides": [
            {"heading": "Support aur Resistance — True Understanding", "points": ["Support: price zone jahan buyers ne baar baar buying ki hai", "Resistance: price zone jahan sellers ne baar baar selling ki hai", "These are memory of the market — institutional orders sit at levels", "Round numbers are always major levels: Nifty 22000, Bitcoin 50000", "Weekly aur monthly levels daily levels se zyada powerful hote hain"]},
            {"heading": "Level Kaise Draw Karein", "points": ["Weekly chart pe pehle teen obvious turning points dhundho", "Ek level pe minimum 2-3 touches chahiye validity ke liye", "Candle bodies use karo wicks nahi — body shows where price settled", "Zones draw karo exact lines nahi — price zone mein react karta hai", "Fewer, stronger levels better hain than many weak ones"]},
            {"heading": "Role Reversal — Trading Ka Sabse Powerful Concept", "points": ["Jab resistance toot jaata hai — woh support ban jaata hai", "Jab support toot jaata hai — woh resistance ban jaata hai", "Yeh retest trade highest probability setups mein se ek hai", "Nifty 18000 was resistance for years — broke above, became perfect support", "This concept alone can make a trader profitable if applied correctly"]},
            {"heading": "High Probability Entry Method", "points": ["Step 1: Weekly chart pe major S/R mark karo", "Step 2: Wait karo price wahan aane ka — patience is key", "Step 3: Rejection candle dekho at the level — pin bar, engulfing", "Step 4: Enter on next candle open — stop just beyond the level", "Step 5: Target next major level — this is your profit zone"]},
            {"heading": "Common Mistakes When Using S/R", "points": ["Galti 1: Too many levels drawing — clutters the chart, confuses", "Galti 2: Trading level alone without trend confirmation", "Galti 3: Not adjusting for volatility — zyada volatile stock, wider zone", "Galti 4: Ignoring higher timeframe levels for day trading entries", "Galti 5: Giving up when first touch doesn't work — levels need patience"]},
        ],
    },
    {
        "title": "Moving Averages — EMA aur SMA Explained",
        "title_en": "Moving Averages — EMA and SMA Complete Guide",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "How to use moving averages for entries, exits, and trend",
        "target_audience": "Traders and investors globally",
        "slides": [
            {"heading": "Moving Average Kya Hoti Hai", "points": ["Moving average = last N days ka average price — smooths out noise", "SMA = Simple Moving Average — all days equal weight", "EMA = Exponential Moving Average — recent days get more weight", "EMA reacts faster to price changes — preferred by traders", "SMA smoother, better for investors — less false signals"]},
            {"heading": "Key Moving Average Levels Used By Professionals", "points": ["9 EMA: very short term — day traders aur swing traders use it", "21 EMA: short-medium term — excellent for entries in trends", "50 EMA: medium term — major support in uptrends", "200 EMA/SMA: long term trend line — used by institutions globally", "Death cross (50 below 200): bearish long term signal everywhere"]},
            {"heading": "How to Use EMA for Entries", "points": ["In uptrend: wait for price to pull back to 21 EMA, buy the bounce", "In downtrend: wait for rally to 21 EMA, sell/short the bounce", "Bounce off 50 EMA in strong uptrend = highest conviction buy", "Price far above 200 EMA = extended, be careful buying", "All professional swing traders use 21 EMA — learn this one first"]},
            {"heading": "Moving Average Crossovers — The Simple Strategy", "points": ["Golden cross: 50 EMA crosses above 200 EMA = long term bull signal", "Death cross: 50 EMA crosses below 200 EMA = long term bear signal", "On weekly chart these signals are very reliable — months of trend", "Nifty 50 golden cross 2023: perfectly called the bull run", "Not for short term trading — best on weekly or monthly chart only"]},
            {"heading": "Multiple Moving Averages Together — The System", "points": ["9/21/50/200 EMA system used by most professional traders", "All four aligned up = strongest bull trend — aggressive buying zone", "Price bouncing off 21 in strong trend = buy with small stop", "Price below all four EMAs = avoid buying — bear market", "AI360 Trading uses 9/21/50/200 EMA on all stock charts — this is proven"]},
        ],
    },
    {
        "title": "RSI aur MACD — Indicators Jo Actually Kaam Karte Hain",
        "title_en": "RSI and MACD — Indicators That Actually Work",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "How to use RSI and MACD correctly, not the wrong way",
        "target_audience": "Active traders globally",
        "slides": [
            {"heading": "RSI — The Most Misused Indicator in Trading", "points": ["RSI measures momentum — how fast price is moving", "Scale of 0-100: above 70 overbought, below 30 oversold", "Most traders sell at 70 and buy at 30 — this is WRONG in strong trends", "In bull market RSI stays 50-80 for months — selling at 70 loses money", "Correct use: trend first, then RSI in direction of trend"]},
            {"heading": "RSI Divergence — The Professional Signal", "points": ["Price makes new high but RSI makes lower high = bearish divergence", "Price makes new low but RSI makes higher low = bullish divergence", "Bitcoin 2021 top: perfect bearish RSI divergence weeks before crash", "Nifty 2024 bottom: bullish RSI divergence called the reversal perfectly", "This signal has more value than any other RSI reading — learn this"]},
            {"heading": "MACD — Trend and Momentum Together", "points": ["MACD = 12 EMA minus 26 EMA — crossing signal line triggers signals", "MACD above zero = bullish momentum, below zero = bearish", "MACD crossover above signal line = buy signal in uptrend", "MACD crossover below signal line = sell signal in downtrend", "Best on daily and weekly charts — very noisy on intraday"]},
            {"heading": "RSI aur MACD Combined — The Setup That Works", "points": ["Uptrend confirmed on weekly chart — this is the filter", "RSI on daily chart pulls back to 40-50 zone", "MACD on daily chart crosses bullish while RSI at 40-50", "Price simultaneously at 21 EMA or key support", "Enter here — this is the highest probability swing entry setup"]},
            {"heading": "Indicators Ki Limitations — Honest Truth", "points": ["No indicator works 100% of the time — all lag price", "Indicators are derived from price — price leads, indicators follow", "Two traders using same indicator can take opposite trades", "Use indicators to confirm what price action already shows", "Price action is the primary signal — indicators are secondary confirmation"]},
        ],
    },
    {
        "title": "Volume Analysis — Market Ka Lie Detector",
        "title_en": "Volume Analysis — The Truth Behind Price Moves",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "How to read volume to confirm moves and catch fakeouts",
        "target_audience": "Active traders globally",
        "slides": [
            {"heading": "Volume Kyu Important Hai", "points": ["Volume = kitne shares trade hue — yeh market ka lie detector hai", "Price bina volume ke move kare = weak move, reverse ho sakta hai", "Price zyada volume ke saath move kare = strong, institutional backed", "You can move price easily on low volume — can't fake volume", "Stocks, crypto, Forex — volume analysis everywhere applies"]},
            {"heading": "High Volume Breakout — The Real Thing", "points": ["Stock 6 months se Rs.500 pe resistance mein tha", "Aaj breakout hua Rs.510 pe lekin volume average ka 300%", "Yeh real breakout hai — institutions were waiting and buying", "Pehle hafte mein Rs.550 tak move possible", "Low volume breakout at Rs.510: very likely to fail and come back"]},
            {"heading": "Volume Price Analysis — 4 Key Combinations", "points": ["Price up + Volume up = strong bullish — buy the dip", "Price up + Volume down = weak rally — be cautious, may reverse", "Price down + Volume up = strong bearish — sell rallies", "Price down + Volume down = weak selloff — may reverse soon", "These four combinations tell you 80% of what you need to know"]},
            {"heading": "Volume at Support and Resistance", "points": ["High volume at support + price bounce = institutional buying confirmed", "Low volume bounce at support = weak, likely to fail", "High volume rejection at resistance = strong sellers, avoid buying", "Breakout of resistance on 3x+ average volume = very reliable signal", "This is how to distinguish real moves from traps"]},
            {"heading": "Free Volume Tools for Indian Traders", "points": ["NSE website: free volume data for all stocks", "TradingView free: volume bars built in on all charts", "Screener.in: filter stocks by volume surge — completely free", "Money control: volume data with delivery percentage", "Delivery percentage: high delivery = long term investors buying — very bullish"]},
        ],
    },

    # ── PHASE 2: FUNDAMENTAL ANALYSIS (Weeks 11-18) ───────────────────
    {
        "title": "Fundamental Analysis Introduction",
        "title_en": "Fundamental Analysis — How to Find Great Companies",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "How to evaluate a company's true value",
        "target_audience": "Investors globally",
        "slides": [
            {"heading": "Fundamental Analysis Kya Hai", "points": ["Company ki actual value judge karna — not just price", "Warren Buffett, Rakesh Jhunjhunwala — both used FA", "Buy great companies at fair price and hold for years", "TA tells you WHEN to buy — FA tells you WHAT to buy", "Best investors combine both — FA for stock selection, TA for timing"]},
            {"heading": "4 Key Financial Statements", "points": ["Balance Sheet: company ki assets, liabilities, equity ka snapshot", "Income Statement (P&L): revenue, expenses, profit over a period", "Cash Flow Statement: actual cash in aur out — most important", "Notes to Accounts: important details that hide in fine print", "Free at NSE website, company investor relations page, Screener.in"]},
            {"heading": "P/E Ratio — Price to Earnings", "points": ["P/E = Stock Price divided by Earnings Per Share", "P/E 20 means you pay Rs.20 for every Rs.1 of annual earnings", "Low P/E = potentially undervalued — but check WHY it is low", "High P/E = growth expectations priced in — dangerous if growth disappoints", "Compare P/E to industry peers — not absolute numbers"]},
            {"heading": "Revenue aur Profit Growth", "points": ["Revenue growth 15%+ year on year = strong growing business", "Net profit growing faster than revenue = improving margins", "3+ years of consistent growth = reliable business model", "One quarter slump: may be temporary — check if trend is intact", "Look for companies growing profit 20%+ with improving margins"]},
            {"heading": "Debt aur Cash Flow — The Reality Check", "points": ["High debt = company paying interest instead of growing", "Debt/Equity ratio below 0.5 preferred — company not overleveraged", "Positive operating cash flow = company actually making real money", "Net profit can be manipulated — cash flow is much harder to fake", "Company with zero debt + high cash = fortress balance sheet"]},
        ],
    },
    {
        "title": "P/E Ratio aur Stock Valuation",
        "title_en": "P/E Ratio and Stock Valuation — How to Know If a Stock is Cheap or Expensive",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "Complete valuation guide for Indian and global stocks",
        "target_audience": "Investors globally",
        "slides": [
            {"heading": "Valuation Kyu Zaroori Hai", "points": ["Great company bhi bad investment ho sakti hai agar overvalued kharido", "Amazon 2000 mein 200x P/E pe crash hua — great company, wrong price", "Valuation = quality ka price judna — both matter equally", "Benjamin Graham: margin of safety — buy 30% below intrinsic value", "This is what separates investors from speculators"]},
            {"heading": "P/E Ratio Deep Dive", "points": ["P/E of 15 was considered fair value historically in India", "IT sector: P/E 25-35 normal — high growth premium justified", "Banking: P/E 10-15 normal — mature industry, stable profits", "Small caps can have P/E 50+ if growing 30%+ per year", "Always compare to sector peers — not cross-sector comparison"]},
            {"heading": "PEG Ratio — P/E ka Upgraded Version", "points": ["PEG = P/E divided by Earnings Growth Rate", "PEG below 1 = potentially undervalued for its growth rate", "PEG above 2 = likely overvalued relative to growth", "Example: P/E 30, growth rate 30%, PEG = 1 — fairly valued", "Lynch's rule: PEG below 1 = buy opportunity in high quality company"]},
            {"heading": "Price to Book Ratio — For Banking Stocks", "points": ["P/B = Price divided by Book Value per share", "Book value = what company would be worth if liquidated today", "P/B below 1 = buying assets cheaper than accounting value", "Banking stocks best valued on P/B — HDFC Bank 4x P/B = premium quality", "P/B above 5-6 = very richly valued — need exceptional growth to justify"]},
            {"heading": "Intrinsic Value — Warren Buffett Ka Method", "points": ["Intrinsic value = present value of all future cash flows", "Simplified: Fair P/E times normalised EPS = rough intrinsic value", "Buffett: buy when price is 30-40% below intrinsic value", "This margin of safety protects from wrong estimates", "You don't need to be exact — just need to know cheap vs expensive"]},
        ],
    },
    {
        "title": "Sector Analysis aur Sector Rotation",
        "title_en": "Sector Analysis and Sector Rotation Strategy",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "How to identify leading sectors and rotate capital",
        "target_audience": "Active investors and traders globally",
        "slides": [
            {"heading": "Sector Rotation Kya Hai", "points": ["Different sectors outperform at different stages of economic cycle", "Early recovery: Financials, Consumer Discretionary lead", "Mid expansion: Technology, Industrials, Materials lead", "Late cycle: Energy, Healthcare, Utilities lead", "Recession: Consumer Staples, Healthcare, Gold outperform"]},
            {"heading": "Indian Market Ke Major Sectors", "points": ["IT: Infosys TCS Wipro — largest market cap sector", "Banking: HDFC ICICI SBI — most traded, highly liquid", "Auto: Maruti Tata Motors M&M — India's manufacturing story", "Pharma: Sun Cipla DrReddy — global generics opportunity", "Infrastructure: L&T Siemens — India's capex boom story"]},
            {"heading": "FII aur Sector Rotation", "points": ["FIIs bring billions into India — they create sector trends", "When FII buys banking sector heavily — bank stocks outperform", "FII data free on NSE website — check every day", "Domestic institutional data too — LIC, mutual funds — all on NSE", "Follow the smart money — they have research teams you cannot match"]},
            {"heading": "How to Identify the Leading Sector", "points": ["Screener: find sector with most stocks hitting 52-week highs", "Check sector ETF performance: BANK NIFTY vs IT vs PHARMA", "Media coverage: what sectors are getting most analyst upgrades", "FII net buying: which sector seeing most foreign money inflow", "Leading sector: buy best 2-3 stocks from it — sector tailwind helps"]},
            {"heading": "Practical Sector Rotation Strategy", "points": ["Every quarter review which 3 sectors are strongest", "Check RSI of sector index — above 50 = momentum, below 50 = weak", "Overweight strongest 2 sectors, underweight weakest 2", "Rebalance quarterly — not more often than that", "This simple approach beats most active fund managers over time"]},
        ],
    },
    {
        "title": "FII aur DII — Institutional Activity Samjho",
        "title_en": "FII and DII — Understanding Institutional Activity",
        "category": "Market Intelligence",
        "level": "Intermediate",
        "description": "How to track and follow smart money in Indian markets",
        "target_audience": "Indian traders and investors",
        "slides": [
            {"heading": "FII aur DII Kya Hote Hain", "points": ["FII = Foreign Institutional Investor — videshi bade funds", "DII = Domestic Institutional Investor — Indian LIC, mutual funds", "Together they control 30-40% of Indian market float", "Their buying/selling creates major market moves", "You cannot beat them — so track them and go with them"]},
            {"heading": "FII Activity Ka Market Pe Impact", "points": ["FII heavy buying = market strong, sectors they buy outperform", "FII selling = market weakness, especially midcaps and smallcaps", "FII sell panic sells can create massive buying opportunities", "October 2024: FII sold Rs.90000 crore — Nifty fell 10%", "Then DII bought heavily — market recovered strongly in December"]},
            {"heading": "FII Data Kaise Dekhen — Free", "points": ["NSE website: market/reports/fii-dii-data — updated daily", "SEBI website: FII activity report monthly", "Money Control: FII/DII tracker with daily updates", "Check: net buying or selling, which segments (equity/FnO)", "Pattern: 10+ consecutive days of FII buying = strong signal"]},
            {"heading": "Delivery Percentage — Hidden Smart Money Signal", "points": ["Delivery % = of total traded shares, how many actually delivered", "High delivery 60%+ = long term investors buying, holding", "Low delivery 20% = intraday traders speculating — ignore this", "Rising delivery % over weeks = accumulation by institutions", "NSE bhav copy has delivery data for every stock free every day"]},
            {"heading": "FII In Options — The Real Signal", "points": ["FII options positions tell you what they expect next", "FII buying CALL options: they expect market to go up", "FII buying PUT options: they expect market to fall — hedge or bearish", "NSE publishes FII options positions daily in participant-wise data", "When FII net long in futures: very bullish for short term market"]},
        ],
    },
    {
        "title": "Interest Rates aur Stock Market",
        "title_en": "Interest Rates and Stock Market — How They Are Connected",
        "category": "Macroeconomics",
        "level": "Intermediate",
        "description": "RBI, US Fed, and their impact on Indian stock market",
        "target_audience": "Investors globally — India, USA, UK",
        "slides": [
            {"heading": "Interest Rate Kyu Stocks Ko Affect Karta Hai", "points": ["Interest rate up = borrowing costly = companies earn less = stocks fall", "Interest rate down = cheap money = companies grow faster = stocks rise", "This connection is universal — India, USA, UK, everywhere same", "RBI rate affects Indian market most directly", "US Fed rate affects global markets including India significantly"]},
            {"heading": "RBI Monetary Policy — What to Watch", "points": ["RBI MPC meets every 6 weeks — date published well in advance", "Repo rate: rate at which RBI lends to banks", "When RBI cuts repo rate: EMIs cheaper, more spending, stocks rise", "When RBI hikes repo rate: inflation fighting, stocks usually fall initially", "Rate decision day = high volatility — options prices spike always"]},
            {"heading": "US Federal Reserve — Global Market Driver", "points": ["US Fed is the most powerful central bank in the world", "When Fed hikes: global money flows back to USA — emerging markets like India suffer", "When Fed cuts: money flows to emerging markets — India benefits strongly", "Fed meeting 8 times per year — watch FOMC dot plot carefully", "India-US correlation has increased: Fed hawkish = Nifty weak often"]},
            {"heading": "Yield Curve aur Stock Market", "points": ["Yield curve: plot of bond yields from 1 month to 30 years", "Normal: long term rates higher than short term — healthy", "Inverted: short term higher than long term — recession warning signal", "US yield curve inverted 2022: recession fears, stocks fell globally", "When curve normalises after inversion: stocks usually recover strongly"]},
            {"heading": "Practical Impact — What to Do When Rates Change", "points": ["Rate hike cycle: reduce cyclical stocks, increase defensives", "Rate cut cycle: increase financials, real estate, growth stocks", "HDFC Bank profits when rates are elevated — NIM increases", "IT companies hurt by US recession fear when Fed hikes aggressively", "Keep an eye on RBI and Fed calendars — plan trades around them"]},
        ],
    },
    {
        "title": "Inflation aur Portfolio Protection",
        "title_en": "Inflation and Portfolio Protection Strategy",
        "category": "Macroeconomics",
        "level": "Intermediate",
        "description": "How inflation erodes wealth and how to protect against it",
        "target_audience": "Investors globally especially India and USA",
        "slides": [
            {"heading": "Inflation Kya Hai aur Kyu Dangerous Hai", "points": ["Inflation = har saal aapke paise ki buying power kam hoti hai", "India 6% inflation means Rs.100 aaj Rs.94 ki power rakhta hai next year", "FD mein 7% aur inflation 6% = real return sirf 1%", "Real return = nominal return minus inflation — always calculate this", "Sab se badi galti: sirf nominal returns dekhna, real returns ignore karna"]},
            {"heading": "Inflation Se Protect Karne Wali Assets", "points": ["Equities: best long term inflation hedge — companies raise prices", "Gold: traditional inflation hedge — especially in India", "Real estate: land mein limited supply — prices rise with inflation", "Commodities: crude, metals — their prices rise in inflationary environment", "TIPS in USA, Inflation-indexed bonds in India — government protection"]},
            {"heading": "Equities — Best Inflation Hedge Over Long Term", "points": ["S&P 500 last 100 years: 10% nominal return, 7% real after inflation", "Nifty 50 last 25 years: 14% nominal, ~8% real after Indian inflation", "Companies pass cost increases to consumers — revenue grows with inflation", "Pricing power = best inflation shield — look for companies with it", "FMCG, pharma, IT services — high pricing power sectors in India"]},
            {"heading": "Gold — The Fear Asset", "points": ["Gold has been store of value for 5000 years across all civilisations", "Rises in fear, uncertainty, inflation, currency weakness", "India loves gold culturally — largest gold consumer globally", "Portfolio allocation: 10-15% in gold as insurance, not speculation", "Sovereign Gold Bond: best way to own gold — earns 2.5% interest + appreciation"]},
            {"heading": "Your Inflation-Proof Portfolio", "points": ["60% equities (mix of large cap and midcap)", "15% gold (SGBs or gold ETF)", "10% real estate (REITs in India — liquid form of real estate)", "10% short term debt (liquid funds for emergency)", "5% international equity (USA tech via NASDAQ ETF for diversification)"]},
        ],
    },
    {
        "title": "Risk Management — Trading Ka Sabse Important Chapter",
        "title_en": "Risk Management — The Most Important Chapter in Trading",
        "category": "Risk Management",
        "level": "All Levels",
        "description": "How to protect capital and survive in markets long term",
        "target_audience": "All traders and investors globally",
        "slides": [
            {"heading": "Risk Management Kyu Sab Se Important Hai", "points": ["95% traders lose money — almost all because of poor risk management", "Best trading strategy means nothing if you blow up your account", "Warren Buffett Rule 1: Never lose money. Rule 2: See Rule 1", "Preserve capital above all else — opportunities come every day", "A 50% loss needs a 100% gain just to break even — asymmetric danger"]},
            {"heading": "Position Sizing — How Much to Risk Per Trade", "points": ["Professional rule: never risk more than 1-2% of account per trade", "Rs.1 lakh account: max Rs.1000-2000 risk per trade only", "Position size = Risk Amount divided by Distance to Stop Loss", "Example: Rs.1000 risk, stop loss Rs.10 below entry = 100 shares", "This formula ensures one bad trade cannot destroy your account"]},
            {"heading": "Stop Loss — Non-Negotiable Rule", "points": ["Stop loss banao BEFORE entering any trade — not after", "Mental stop losses never work — emotions take over always", "Hard stop: direct order in broker system — price hits = automatic exit", "ATR-based stop: 2x ATR below entry for swing trades", "Once set, only move stop in your favor — never widen it"]},
            {"heading": "RR Ratio — Risk Reward Ratio", "points": ["Minimum 1:2 RR for every trade — risk Rs.1 to make Rs.2", "With 1:2 RR you can lose 60% of trades and still be profitable", "Example: 10 trades, 4 wins × Rs.2000, 6 losses × Rs.1000 = net profit Rs.2000", "Most profitable traders win only 40-50% of trades — RR saves them", "AI360 Trading system requires minimum 1.8 RR before any entry"]},
            {"heading": "Maximum Drawdown aur Account Protection Rules", "points": ["Set a monthly loss limit: if down 10% this month, stop trading", "Set a daily loss limit: if down 2% today, no more trades that day", "Never revenge trade — emotional trading after losses always makes it worse", "Correlation risk: don't have 8 trades all in same sector — diversify", "These rules are why some traders survive 20 years — most quit in 2"]},
        ],
    },

    # ── PHASE 3: ADVANCED STRATEGIES (Weeks 19-30) ────────────────────
    {
        "title": "Options Trading Introduction",
        "title_en": "Options Trading Introduction — The Complete Beginner Guide",
        "category": "Options",
        "level": "Beginner",
        "description": "What are options, how they work, Indian market specifics",
        "target_audience": "Beginners wanting to start options trading",
        "slides": [
            {"heading": "Option Contract Kya Hai", "points": ["Option = right but not obligation to buy or sell at a fixed price", "Call option: right to BUY at strike price — profits when stock rises", "Put option: right to SELL at strike price — profits when stock falls", "Premium: price you pay for this right — this is your maximum loss", "Expiry: date after which option becomes worthless if not exercised"]},
            {"heading": "Call Option Example — Real Numbers", "points": ["Nifty currently at 22000", "Buy 22200 Call option at Rs.50 premium", "If Nifty rises to 22500: call may be worth Rs.300 — 6x profit", "If Nifty stays at 22000 or falls: you lose only Rs.50 premium", "This is leverage without borrowing — maximum loss defined upfront"]},
            {"heading": "Put Option — Market Crash Ka Insurance", "points": ["Buy put when you think price will fall", "Portfolio insurance: own stocks + buy put options on Nifty", "If market crashes 20%, your put options may 5-10x in value", "This protects your portfolio like car insurance protects your car", "Every large investor globally uses puts as portfolio protection"]},
            {"heading": "India Mein Options Trading Kaise Kaam Karta Hai", "points": ["Nifty and Bank Nifty: most liquid options in India", "Weekly expiry: every Thursday for Nifty", "Monthly expiry: last Thursday of month", "Lot size: Nifty 50 = 25 shares per lot — minimum trade unit", "F&O segment activation needed — broker se request karo"]},
            {"heading": "Option Buyer Ka Success Formula", "points": ["Only buy options in direction of trend — never fight the trend", "Minimum 20 days to expiry — more theta protection", "Maximum loss predetermined: only invest what you can afford to lose", "Exit at 50-100% profit — greed kills option traders", "Stop loss at 40-50% of premium — strict, no exceptions"]},
        ],
    },
    {
        "title": "Option Selling — Premium Collect Karo",
        "title_en": "Option Selling — How to Collect Premium Like Insurance Companies",
        "category": "Options",
        "level": "Intermediate",
        "description": "Covered calls, cash secured puts, income generation",
        "target_audience": "Intermediate traders India and globally",
        "slides": [
            {"heading": "Option Sellers Kyu Long Term Jeet te Hain", "points": ["80% options expire worthless — sellers collect all that premium", "Time decay works FOR sellers — money comes in while doing nothing", "Like being the casino: house edge wins over thousands of bets", "Warren Buffett has sold billions in put options throughout his career", "Risk is higher per trade but managed properly = consistent income"]},
            {"heading": "Covered Call — Monthly Income Kaise Generate Karein", "points": ["Step 1: Own 1 lot (25 shares) of a stock like Infosys", "Step 2: Every month sell 1 call option above current price", "Step 3: Collect premium — Infosys 1500 CE may give Rs.2000/month", "If Infosys stays below 1500: keep full Rs.2000, sell again next month", "If Infosys rises above 1500: sell at 1500, still made Rs.2000 extra"]},
            {"heading": "Cash Secured Put — Buy Stocks at Discount", "points": ["Pick a stock you genuinely want to own: say HDFC Bank at Rs.1600", "Sell Rs.1500 put option, collect Rs.1500 premium (hypothetical)", "If HDFC stays above 1500: keep premium, repeat next month", "If HDFC falls below 1500: buy at Rs.1500 — price you wanted!", "Effectively getting paid to buy your favourite stock at a discount"]},
            {"heading": "Risk Management for Option Sellers", "points": ["Always buy further OTM option to cap unlimited loss risk", "This creates a spread — limits maximum possible loss", "Example: sell 22000 put, buy 21500 put — maximum loss is Rs.500×25=Rs.12500", "Never sell naked options — especially in small accounts", "Exit when loss = 2x premium collected — before it gets worse"]},
            {"heading": "Best Market Conditions for Option Selling", "points": ["High VIX: premiums are elevated — best time to sell", "Sideways market: options expire worthless most often", "Trending market: option selling riskier — use spreads only", "Avoid selling options before major events: RBI policy, budget, earnings", "Best: sell options 2 weeks after big event when VIX calms down"]},
        ],
    },
    {
        "title": "Options Greeks — Delta Theta Vega Explained Simply",
        "title_en": "Options Greeks — Delta Theta Vega Made Simple",
        "category": "Options",
        "level": "Advanced",
        "description": "Understanding the four Greeks for better options trading",
        "target_audience": "Intermediate to advanced options traders",
        "slides": [
            {"heading": "Greeks Kyu Sikhne Chahiye", "points": ["Greeks tell you exactly how your option will behave — before it moves", "Without Greeks you are guessing — with Greeks you are calculating", "Same Greeks apply to Nifty options and US SPY options identically", "Professional options traders think entirely in terms of Greeks", "Spend 2 hours learning these — save 2 years of painful lessons"]},
            {"heading": "Delta — Directional Exposure", "points": ["Delta tells you how much option price changes per Rs.1 stock move", "ATM option delta: approximately 0.5 always — moves Rs.50 per Rs.100 stock move", "Deep ITM: delta approaches 1.0 — moves almost like owning stock", "Far OTM: delta approaches 0 — barely moves even if stock moves", "Your total delta across all positions = net market direction bet"]},
            {"heading": "Theta — Daily Value Erosion", "points": ["Theta = how much premium you lose every single day sitting still", "ATM weekly option: may lose 20-30% of value in last 3 days", "Time decay is NOT linear — accelerates massively near expiry", "Option buyer vs theta: like racing against a melting ice cube", "Option seller earns theta: money comes in every day — even holidays"]},
            {"heading": "Vega — Volatility's Impact", "points": ["Vega measures how much option price changes with implied volatility", "India VIX high (above 20): options expensive — good time to sell", "India VIX low (below 14): options cheap — good time to buy", "Buy options before major events when VIX is still low", "After VIX spike from news: sell options — inflated premium normalises"]},
            {"heading": "Using Greeks Together — Practical Application", "points": ["Before buying: check delta (direction), theta (time cost), vega (volatility)", "Buy option: want high delta, low theta, positive vega", "Sell option: want theta working for you, vega exposure manageable", "Sensibull.com free: see all Greeks for any Indian option live", "Spend 30 days on paper trading watching Greeks move — invaluable education"]},
        ],
    },
    {
        "title": "Swing Trading Complete Strategy",
        "title_en": "Swing Trading Strategy — How to Capture 5-15% Moves",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "Complete swing trading system with entry, exit, and risk rules",
        "target_audience": "Working professionals who can't day trade",
        "slides": [
            {"heading": "Swing Trading Kya Hai", "points": ["Hold trades for 3-15 days — not intraday, not long term", "Perfect for people with regular jobs — check charts once a day", "Catch 5-15% moves in individual stocks — very achievable", "Requires less time than day trading, less patience than investing", "Most successful traders use swing trading as their primary strategy"]},
            {"heading": "Stock Selection For Swing Trading", "points": ["Step 1: Market regime check — Nifty above or below 20DMA", "Step 2: Find sectors with strong momentum — FII buying, sector tailwind", "Step 3: In that sector find stocks breaking out or at key support", "Step 4: Volume confirmation — 150%+ average volume on setup", "Step 5: FII accumulation data confirms — smart money is with you"]},
            {"heading": "Entry Rules — Non-Negotiable", "points": ["Enter only in direction of trend — never buy in downtrend", "RSI below 65 at entry — not overbought yet", "Price above 21 EMA — trend structure intact", "Volume must be above average — confirms conviction of move", "Minimum 1:2 risk reward — if not achievable, skip the trade"]},
            {"heading": "Exit Rules — How to Take Profits", "points": ["Trailing stop loss: move stop up as trade profits — lock in gains", "Target: next major resistance or 2x the risk amount", "Time stop: if after 7 days not working — exit, find better opportunity", "Partial exit: take 50% profit at first target, let rest run", "Hard rule: if original stop hits — exit immediately, no second guessing"]},
            {"heading": "The AI360 Trading Swing System", "points": ["This is exactly how AI360 Trading paper trades are generated", "11-gate filter selects only highest quality breakout stocks", "RR ratio minimum 1.8 for every trade — no exceptions", "TSL (trailing stop loss) automatically moves in your favour", "3 wins in first week: BSE +3.87%, IDEA +5.94%, ADANIPORTS +5.58%"]},
        ],
    },
    {
        "title": "Position Trading — Long Term Wealth Builder",
        "title_en": "Position Trading — Building Wealth Over Months and Years",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "How to hold winning trades for 3-12 months and multiply wealth",
        "target_audience": "Investors wanting market-beating returns",
        "slides": [
            {"heading": "Position Trading vs Investing vs Swing Trading", "points": ["Position trading: hold 1-12 months, capture major trend moves", "Not day trading (intraday), not investing (10+ years)", "Can generate 30-100%+ returns on individual stocks in one trend", "Uses both technical AND fundamental analysis — best of both worlds", "Famous position traders: Mark Minervini, William O'Neil — both billionaires"]},
            {"heading": "What Stocks to Position Trade", "points": ["Stage 2 uptrend: stock making higher highs and higher lows consistently", "Earnings growing 20%+ per year — fundamental strength driving technical", "FII accumulation: institutions buying for weeks or months", "Near 52-week high: strongest stocks make new highs first", "Sector leader: #1 or #2 stock in a leading sector — go with the best"]},
            {"heading": "The VCP — Volatility Contraction Pattern", "points": ["Developed by Mark Minervini — the best stock pattern for position traders", "Stock makes series of contracting price swings — getting tighter", "Volume also contracts as price tightens — professional accumulation", "Then: explosive breakout on massive volume — big move begins", "Infosys, HDFC, Reliance — all showed VCP before biggest moves"]},
            {"heading": "Position Sizing for Long Holds", "points": ["Maximum 15-20% of portfolio in any single position", "Use wider stop loss — 8-10% below buy point for position trades", "Start with 50% of planned position, add as it works", "Pyramid into strength: add more shares only when price rises, never average down", "Cut losses at 8% maximum — no holding and hoping in declining stocks"]},
            {"heading": "Exit Strategy for Position Trades", "points": ["Exit when: stock violates 10-week moving average on high volume", "Exit when: fundamental deterioration — earnings miss two quarters", "Exit when: stock underperforms for 8+ weeks while market rises", "Partial exit: sell 1/3 at 25% gain, 1/3 at 50% gain, hold rest", "Let winners run: biggest position traders hold winners 6-18 months"]},
        ],
    },
    {
        "title": "Breakout Trading — Momentum Stocks Ko Pakdo",
        "title_en": "Breakout Trading — How to Catch Momentum Stocks",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "How to identify and trade breakouts before they become obvious",
        "target_audience": "Active traders globally",
        "slides": [
            {"heading": "Breakout Kya Hota Hai", "points": ["Stock ne ek important resistance level break kiya high volume pe", "Yeh market ka signal hai: supply absorbed, demand winning", "Breakout stocks often move 20-50% in short time after confirmation", "This is how many 10x stocks begin their major moves", "William O'Neil CANSLIM: breakout from sound base = golden opportunity"]},
            {"heading": "Sound Base Kya Hoti Hai", "points": ["Stock 4-8+ weeks se ek tight range mein consolidate kar raha ho", "Volume declining in base — sellers exhausted, no more supply", "Fundamentals strong — earnings growing, sector in tailwind", "Near 52-week high but not extended — room to run above breakout", "At least one previous contraction — VCP or cup and handle pattern"]},
            {"heading": "Breakout Entry — Exact Timing", "points": ["Entry: when stock closes above the resistance on volume 150%+ average", "Buy point: pivot high plus 5-10 paise — not below, not far above", "Never chase: if stock already moved 5%+ from pivot — skip, wait for next", "Morning entry: 9:30-10:00 AM after confirmation of gap or early strength", "Not every breakout works — only trade where fundamentals also support"]},
            {"heading": "Volume Confirmation — The Most Important Filter", "points": ["Breakout without volume: very likely to fail — 70%+ pullback chance", "Breakout with 2-3x average volume: high institutional participation", "Delivery percentage above 60% on breakout day: long term buyers coming", "Institutions cannot hide — they need volume to move their large positions", "This single filter will save you from most false breakouts"]},
            {"heading": "What to Do After Breakout Entry", "points": ["Set initial stop at low of breakout day — below the pivot", "Move stop to breakeven once stock is 3%+ in profit", "First target: 10-15% above entry — potential profit zone", "If stock holds breakout level for 3 days: high probability trade continuing", "If stock falls back below breakout: exit immediately — failed breakout signal"]},
        ],
    },
    {
        "title": "Trading Psychology — Fear aur Greed Ko Samjho",
        "title_en": "Trading Psychology — Understanding Fear and Greed",
        "category": "Psychology",
        "level": "All Levels",
        "description": "Why most traders fail psychologically and how to fix it",
        "target_audience": "All traders and investors globally",
        "slides": [
            {"heading": "Psychology Kyu Trading Ka Sabse Important Part Hai", "points": ["Market strategies exist everywhere — psychology separates winners from losers", "Same strategy, two traders: one profitable, one losing — psychology is why", "Emotions make you: buy tops, sell bottoms, hold losers, sell winners early", "Trading is the only profession where being emotional is career ending", "The enemy is not the market — the enemy is you staring at the screen"]},
            {"heading": "Fear — How It Destroys Traders", "points": ["Fear of missing out (FOMO): chasing stocks after big move — buying the top", "Fear of loss: not cutting losses, hoping for recovery — letting losers run", "Fear of being wrong: adding to losing positions — averaging down disaster", "Fear after a loss: hesitating on next perfectly valid setup — lost opportunity", "Solution: process-based trading — follow rules regardless of feelings"]},
            {"heading": "Greed — The Silent Portfolio Killer", "points": ["Not taking profits at target because 'it could go higher' — loses profit", "Oversizing positions because you are 'sure' about a trade — dangerous", "Revenge trading: doubling down after a loss to win it back fast", "Holding a winning trade too long — winner becomes a loser", "Solution: pre-defined exit rules followed mechanically, no discretion"]},
            {"heading": "Building a Trading Mindset", "points": ["Think in probabilities: no trade is certain — any outcome is possible", "Journal every trade: why you entered, what happened, what you learned", "Accept losses as cost of doing business — like a restaurant pays for ingredients", "Focus on process: if you followed your rules perfectly, it was a good trade", "Success = following your system consistently, not any one trade's outcome"]},
            {"heading": "Practical Psychology Tools", "points": ["Rule: never check P/L while in a trade — check charts not money", "Rule: 10-minute rule after a loss — no new trades for 10 minutes minimum", "Rule: pre-market plan — write what you will buy, at what price, why", "Rule: trading journal — 5 minutes after each trade to record feelings", "Rule: monthly review — am I following my rules or letting emotions decide"]},
        ],
    },

    # ── PHASE 4: ADVANCED AND EXPERT (Weeks 29-40) ────────────────────
    {
        "title": "Iron Condor Strategy — Advanced Options",
        "title_en": "Iron Condor — The Advanced Options Strategy for Sideways Markets",
        "category": "Advanced Options",
        "level": "Advanced",
        "description": "Complete iron condor setup for Indian Nifty market",
        "target_audience": "Advanced options traders India",
        "slides": [
            {"heading": "Iron Condor Kya Hai", "points": ["Iron condor = 4 option legs = profit when market stays sideways", "Sell OTM call + Buy further OTM call = bear call spread", "Sell OTM put + Buy further OTM put = bull put spread", "Combined: profit zone in the middle — like a bird with wings", "Maximum profit when market stays between your two short strikes"]},
            {"heading": "Why Iron Condor Works in Sideways Markets", "points": ["Market stays in a range 60-70% of the time historically", "Both theta and time decay work for you from both sides", "High probability strategy: often 70-80% probability of profit", "VIX high: collect more premium on both sides", "Nifty expiry week: often finds max pain level — ideal for condor"]},
            {"heading": "Setting Up Nifty Iron Condor — Step by Step", "points": ["Check Nifty range: where is it likely to stay for next 2 weeks", "Sell 22500 call, buy 22700 call (bear call spread above)", "Sell 21500 put, buy 21300 put (bull put spread below)", "Collect net premium from both spreads combined", "Maximum loss: width of spread minus premium collected × lot size"]},
            {"heading": "Managing the Iron Condor", "points": ["If Nifty moves toward one side: adjust or close that spread early", "Delta hedging: if position delta non-zero, buy/sell futures to neutralise", "Close at 50% profit — do not wait for full premium to decay", "If loss reaches 2x premium collected: close the entire position", "Best months to run: low volatility environment, VIX below 16"]},
            {"heading": "Tax and Charges for Options in India", "points": ["STT on options: 0.0625% on sell side — small but add up on many trades", "GST on brokerage: 18%", "SEBI charges and exchange charges: very small", "Short term capital gains on F&O profits: income tax slab rate applies", "F&O is treated as business income — file ITR-3, show profit/loss"]},
        ],
    },
    {
        "title": "Algo Trading Introduction",
        "title_en": "Algorithmic Trading — Introduction for Indian Markets",
        "category": "Advanced",
        "level": "Advanced",
        "description": "What is algo trading, can retail traders use it, free tools",
        "target_audience": "Tech-savvy traders globally",
        "slides": [
            {"heading": "Algo Trading Kya Hai", "points": ["Rules likho, computer automatically trades — no emotion, no hesitation", "Algorithm: if condition A met then buy X shares, exit at target Y", "Institutions use algos for 70%+ of all trades globally", "Retail traders can now access algo tools — Zerodha Streak, Dhan", "Not for everyone — needs patience to set up but runs 24/7"]},
            {"heading": "Algo Trading Ke Advantages", "points": ["Zero emotional bias — follows rules mechanically every time", "Speed: executes in milliseconds — faster than human reaction", "Backtesting: test strategy on 10 years of data before risking money", "Can monitor 100 stocks simultaneously — impossible manually", "Consistency: same rules applied equally to every opportunity"]},
            {"heading": "Free Algo Tools for Indian Retail Traders", "points": ["Zerodha Streak: create strategies without coding — free for basic", "Dhan Algo: simple algo setup, works with Dhan account", "TradingView Pine Script: write custom strategies, backtest free", "Chartink.com: screener-based alerts, semi-automated", "Python with Zerodha Kite API: full automation, needs coding knowledge"]},
            {"heading": "Creating Your First Simple Algo — Step by Step", "points": ["Define entry rule: EMA 9 crosses above EMA 21 on daily chart", "Define exit rule: stock falls below EMA 21 or hits 10% stop loss", "Backtest on 2 years data on Zerodha Streak", "Paper trade the algo for 1 month — observe without risking money", "If results consistent: go live with minimum capital first"]},
            {"heading": "Algo Trading Ki Limitations — Honest Truth", "points": ["Algo does what you code: garbage strategy in = garbage results", "Market regime change: algo that worked 2021 may fail 2024", "Black swan events: algo cannot understand news — sudden crashes hurt", "Requires ongoing monitoring: set and forget is dangerous", "AI360 Trading AppScript is an algo: 11 gates filter 200+ stocks automatically"]},
        ],
    },
    {
        "title": "Portfolio Construction — Poora Portfolio Kaise Banao",
        "title_en": "Portfolio Construction — Building a Complete Investment Portfolio",
        "category": "Portfolio Management",
        "level": "Intermediate",
        "description": "Asset allocation, diversification, and rebalancing strategy",
        "target_audience": "Investors globally wanting structured approach",
        "slides": [
            {"heading": "Portfolio Kya Hota Hai", "points": ["Portfolio = aapke saare investments ka combined collection", "Not just stocks: bonds, gold, real estate, cash — all included", "Diversification: different assets zyada stable return dete hain", "Asset allocation: kahan kitna daalein — yeh most important decision", "Your portfolio should match your: age, income, risk tolerance, goals"]},
            {"heading": "Age-Based Asset Allocation Rule", "points": ["100 minus age = equity allocation (traditional rule)", "Age 25: 75% equity, 25% debt and gold", "Age 40: 60% equity, 40% debt and gold", "Age 60: 40% equity, 60% debt and stable assets", "Young investors should take more equity risk — time to recover from dips"]},
            {"heading": "Equity Portfolio Construction", "points": ["Large caps: 50% of equity — stability, liquidity, sleep peacefully", "Mid caps: 30% of equity — higher growth, some volatility", "Small caps: 20% of equity — highest potential, highest risk", "Sector diversification: not more than 20-25% in any one sector", "Maximum 15-20% in any single stock — even your favourite"]},
            {"heading": "Rebalancing — The Discipline Most Investors Skip", "points": ["If equity rises 20% in a year: sell some to restore original allocation", "If equity falls: buy more to restore allocation — buying at discount", "Rebalance once per year — not more, not less", "This forces: sell high, buy low — automatically and emotionlessly", "Studies show: rebalanced portfolio beats non-rebalanced by 1-2% annually"]},
            {"heading": "Your Complete Portfolio Checklist", "points": ["Emergency fund: 6 months expenses in liquid fund — before investing", "Insurance: adequate term life and health insurance — before investing", "Core equity: index funds (50%) + quality direct stocks (50%) = equity portion", "Gold: 10-15% in SGB or gold ETF", "Review annually: are investments matching your changing life goals"]},
        ],
    },
    {
        "title": "Tax on Trading aur Investing India",
        "title_en": "Tax on Trading and Investing in India — Complete Guide",
        "category": "Tax and Legal",
        "level": "All Levels",
        "description": "STCG, LTCG, F&O tax, ITR filing for traders and investors",
        "target_audience": "Indian traders and investors",
        "slides": [
            {"heading": "Kyu Tax Samajhna Zaroori Hai", "points": ["Taxes can eat 15-30% of your profits if not managed properly", "Tax planning legally reduces your burden — not tax evasion", "ITR filing required if capital gains above exempt limit", "F&O income classified as business income — different rules apply", "Understand taxes before you start trading — not after year-end surprise"]},
            {"heading": "STCG vs LTCG — Short vs Long Term", "points": ["STCG: sell within 1 year of buying — flat 20% tax on equity profits", "LTCG: sell after 1 year — 12.5% tax but first Rs.1.25 lakh exempt per year", "Strategy: hold good stocks 1+ year to get LTCG benefit", "ELSS mutual funds: 3 year lock-in, save 80C, LTCG applies after 3 years", "Losses can be set off against gains — plan year-end tax harvesting"]},
            {"heading": "F&O Trading — Business Income Tax", "points": ["F&O profits are NOT capital gains — treated as business income", "You pay income tax at your slab rate: 30%+ if high earner", "But: expenses can be deducted — brokerage, software, internet", "If F&O turnover above Rs.10 crore: tax audit mandatory", "File ITR-3 for F&O income — consult CA for first time filing"]},
            {"heading": "Tax Loss Harvesting — Legal Tax Saving Strategy", "points": ["Sell loss-making investments before March 31 every year", "This realized loss can offset capital gains from winners", "Buy the same asset back after 30 days if you still like it", "Example: sell stock at Rs.50000 loss — saves Rs.10000 tax at 20% STCG", "Systematic tax harvesting over years saves significant money"]},
            {"heading": "Practical Tax Tips for Traders", "points": ["Keep records: every trade logged with date, price, brokerage paid", "Annual statement: Zerodha Dhan provide tax P&L report automatically", "Set aside 20-30% of profits in liquid fund for advance tax payment", "Advance tax due dates: 15 June, 15 Sept, 15 Dec, 15 March", "Consult a CA who specialises in stock market taxation — worth the fee"]},
        ],
    },
    {
        "title": "Global Markets — USA, UK aur India Connection",
        "title_en": "Global Markets — How USA UK and India Are Connected",
        "category": "Global Investing",
        "level": "Intermediate",
        "description": "Why global markets matter for Indian investors and how to invest globally",
        "target_audience": "Indian investors wanting global exposure — USA, UK, UAE audiences",
        "slides": [
            {"heading": "Global Markets Ka Indian Market Pe Impact", "points": ["Nifty follows S&P 500 direction approximately 60-70% of the time", "US Fed decision: interest rate hike India mein FII outflow karta hai", "Global risk-off events: India mein FII sell karte hain — Nifty falls", "Geopolitical crisis: oil prices rise, India imports oil, companies suffer", "This connection increasing: India now global market, cannot ignore world"]},
            {"heading": "US Stock Market — World Ka Most Important", "points": ["S&P 500: 500 largest US companies, best performing index historically", "NASDAQ: technology heavy — Apple Microsoft Google Amazon — global brands", "Apple alone bigger than entire Indian stock market capitalization", "US market 10% return annually for 100 years — most reliable in world", "Indian investors can invest in US stocks via international mutual funds or LRS"]},
            {"heading": "UK Market — Stable Dividend Income", "points": ["FTSE 100: 100 largest UK companies — heavy in energy, banking, mining", "Higher dividend yields than India or USA — income focused market", "British Pound second most traded currency — matters for NRI investors", "UK-India trade corridor growing post-Brexit — opportunities in both ways", "Indian pharma companies have large UK presence — sector correlation"]},
            {"heading": "UAE Dubai — NRI Investor Hub", "points": ["UAE: zero income tax for residents — tax-free investing advantage", "Dubai Gold and Commodities Exchange: gold, energy trading hub", "Indian diaspora biggest in UAE — remittances and investment both flow", "UAE dirham pegged to USD — no currency risk against dollar", "Indian real estate, Indian mutual funds: NRIs invest back in India significantly"]},
            {"heading": "How to Invest Globally From India", "points": ["International mutual funds: Motilal NASDAQ 100, Mirae US Stocks — easiest", "LRS — Liberalized Remittance Scheme: $250000 per year overseas investment", "Platforms: Vested Finance, Groww US, INDmoney — direct US stock purchase", "ETFs on Indian exchange: Nifty Nasdaq 100 ETF, HANGSENG ETF — very easy", "Start with international index fund — diversify geography just like sectors"]},
        ],
    },
    {
        "title": "Dividend Investing — Passive Income Kaise Banao",
        "title_en": "Dividend Investing — Building Passive Income From Stocks",
        "category": "Wealth Building",
        "level": "Beginner",
        "description": "How dividends work, best dividend stocks India, income strategy",
        "target_audience": "Income-seeking investors globally",
        "slides": [
            {"heading": "Dividend Kya Hota Hai", "points": ["Company apne profit ka kuch hissa shareholders ko cash mein deta hai", "Dividend yield = Annual dividend divided by stock price × 100", "Coal India, Power Grid: 5-8% dividend yield — better than FD", "You earn money WHILE holding the stock — double benefit", "Aristocrat companies: 25+ years of growing dividends — most reliable"]},
            {"heading": "Best Dividend Stocks India 2026", "points": ["Coal India: government-backed, massive cash flows, 7-9% yield historically", "Power Grid: regulated returns, consistent dividend, infrastructure backbone", "ITC: diversified FMCG, growing dividend, also has capital appreciation", "ONGC: oil company, cyclical dividend but high when oil prices elevated", "Infosys TCS: lower yield but consistent, growing dividend every year"]},
            {"heading": "Dividend Reinvestment — DRIP Strategy", "points": ["Take all dividends received and buy more shares", "Compounding accelerates: more shares = more dividends = even more shares", "Rs.10 lakh in Coal India at 8% yield: Rs.80000 year 1, reinvested = accelerating", "20 years of DRIP often doubles or triples wealth vs taking dividends as cash", "SIPs do this automatically — dividend option reinvests for you"]},
            {"heading": "Dividend Safety — How to Check", "points": ["Payout ratio: dividend as % of profits — below 75% is safe", "Cash flow: dividends must be covered by operating cash flow", "Debt level: highly indebted companies cut dividends first in crisis", "History: 10+ years of uninterrupted dividends = reliable company", "Avoid: high yield stocks with falling profits — dividend will be cut"]},
            {"heading": "Building a Dividend Income Portfolio", "points": ["Target: Rs.50000/month passive income = need Rs.75 lakh at 8% yield", "Mix: 40% high yield (Coal India, Power Grid), 60% growth + moderate yield", "Start small: even Rs.5000/month SIP in dividend-focused stocks", "Time is the key: 10-15 years of consistent investing builds real passive income", "This is how financial freedom is actually built — systematically, patiently"]},
        ],
    },
    {
        "title": "Value Investing — Warren Buffett Style",
        "title_en": "Value Investing — The Warren Buffett Way",
        "category": "Investment Philosophy",
        "level": "Intermediate",
        "description": "Graham-Buffett value investing applied to Indian stocks",
        "target_audience": "Long-term investors globally",
        "slides": [
            {"heading": "Value Investing Kya Hai", "points": ["Great companies buy karo when they are temporarily undervalued by market", "Benjamin Graham: stock market is a voting machine short term, weighing machine long term", "Short term: price driven by emotion and news", "Long term: price converges toward real business value — always", "Buy businesses, not stock tickers — this mindset changes everything"]},
            {"heading": "Warren Buffett Ka 4-Filter System", "points": ["Filter 1: Business understandable — can you explain it to a 10-year-old", "Filter 2: Durable competitive advantage — moat that protects profits", "Filter 3: Honest and capable management — integrity above all", "Filter 4: Attractive price — margin of safety, buy below intrinsic value", "All 4 must be satisfied — skip any one and you might be wrong"]},
            {"heading": "Economic Moat — Buffett Ka Favourite Concept", "points": ["Moat = sustainable competitive advantage that is very hard to replicate", "Brand moat: Nestle Maggi, Asian Paints — consumers pay premium forever", "Cost moat: Jio disrupted telcos by being cheapest — hard to undercut", "Network moat: stock exchanges NSE BSE — more users = more valuable", "Switching cost: Tally software — businesses hate switching, very sticky"]},
            {"heading": "Applying Value Investing to Indian Stocks", "points": ["Rakesh Jhunjhunwala: Titan bought at Rs.3, sold years later at Rs.3000 — 1000x", "He found: growing middle class + gifting culture + Tata brand moat", "Simple insight: India getting richer = more watches sold", "Your edge: understanding Indian consumer better than foreign investors", "Look for: growing Indian consumption plays with pricing power and moat"]},
            {"heading": "Common Value Traps — Stocks That Look Cheap But Aren't", "points": ["Value trap: stock cheap because business fundamentally broken", "Watch out: declining industry, management integrity issues, high debt", "Avoid: P/E of 5 with declining revenue for 3+ years", "True value: P/E reasonable + growing profits + strong balance sheet + moat", "Question: why is this stock cheap? If you can't answer — avoid it"]},
        ],
    },
    {
        "title": "Building Your Own Trading System",
        "title_en": "Building Your Own Trading System — Step by Step",
        "category": "Systems and Process",
        "level": "Intermediate",
        "description": "How to create a systematic, rule-based trading approach",
        "target_audience": "Serious traders globally",
        "slides": [
            {"heading": "Kyu Trading System Zaroori Hai", "points": ["Without system: you make different decisions in same situation every time", "With system: same input = same action = consistency = data", "System removes emotion: you follow rules, not feelings", "Backtestable: 10 years of data tells you if system works — before real money", "AI360 Trading is a complete system — 11 gates, RSI filter, TSL automation"]},
            {"heading": "Components of a Trading System", "points": ["Universe: which stocks will I trade — Nifty 200, S&P 500, only midcaps", "Filter: what conditions must be met before even considering entry", "Entry rule: exact price or condition that triggers buy", "Stop loss: where exactly does the trade become wrong", "Exit rule: target hit, TSL hit, time-based, or fundamental change"]},
            {"heading": "Building Your Filters", "points": ["Market regime filter: only buy in bullish market — Nifty above 20DMA", "Quality filter: FII accumulation, strong sector, earnings growth", "Technical filter: RSI below 65, price above 21 EMA, volume above average", "Risk filter: entry must offer 1:2 minimum risk reward", "These 4 filters eliminate 90% of bad trades before they happen"]},
            {"heading": "Backtesting Your System", "points": ["Take your rules and apply them to last 3 years of historical data", "Record every signal: entry price, stop, target, outcome", "Calculate: win rate, average win, average loss, max drawdown", "If win rate 45%+ and average win 2x average loss: system is viable", "Tools: TradingView Pine Script, AmiBroker, Excel — all work for backtesting"]},
            {"heading": "System Evolution — Never Stop Improving", "points": ["Record every live trade with reasoning in journal", "Monthly review: are system rules being followed, what can improve", "Add new filters when you identify new patterns causing losses", "Example: AI360 Trading added RSI filter after SAIL loss in May 2026", "A trading system is never finished — always learning, always improving"]},
        ],
    },

    # ── PHASE 5: MASTERY (Weeks 41-52) ────────────────────────────────
    {
        "title": "Gold aur Silver — Smart Investment Ya Nahi",
        "title_en": "Gold and Silver — Smart Investment or Not?",
        "category": "Alternative Investments",
        "level": "Beginner",
        "description": "Gold and silver investment in India — SGB, ETF, physical gold",
        "target_audience": "Indian investors and global precious metal investors",
        "slides": [
            {"heading": "Gold Kyu Special Hai", "points": ["5000 years ka store of value — no paper currency has lasted that long", "Limited supply: all gold ever mined fits in 3 Olympic swimming pools", "No counterparty risk: unlike bonds or bank deposits", "Universally accepted globally: from India to USA to anywhere", "Hedge against inflation, currency debasement, geopolitical crisis"]},
            {"heading": "Best Way to Own Gold in India", "points": ["Sovereign Gold Bond (SGB): best option — earns 2.5% interest + appreciation", "Gold ETF: liquid, no storage risk, trade like a stock on exchange", "Digital gold on Groww or PhonePe: convenient but slightly higher charges", "Physical gold: jewellery has making charges, difficult to sell precisely", "Gold mutual funds: invest in gold mining companies — higher risk than gold ETF"]},
            {"heading": "Silver — The Poor Man's Gold", "points": ["Silver has both monetary value AND industrial demand — more volatile", "Used in solar panels, electronics, electric vehicles — industrial demand growing", "Silver ratio to gold: historically 1:60-80 — silver often outperforms in rallies", "Lower cost to start: accessible to smaller investors", "More volatile than gold: can rise 50% and fall 40% in same year — higher risk"]},
            {"heading": "How Much Gold in Your Portfolio", "points": ["Traditional advice: 10-15% of total portfolio in gold", "Gold is insurance — you don't hope insurance pays out, but glad when it does", "When everything else falls: gold often rises — true diversification", "Rebalance: if gold rises too much, sell some and buy more stocks", "Gold SGB: 8-year tenure, option to exit after 5 years at prevailing market price"]},
            {"heading": "Gold vs Bitcoin — The New Question", "points": ["Bitcoin called 'digital gold' — limited supply, no central control", "Gold: 5000 year track record. Bitcoin: 15 year track record", "Bitcoin more volatile: 80% drops have happened multiple times", "Some investors: 5-10% Bitcoin as gold alternative in modern portfolio", "Conservative advice: stick with physical gold and SGB — proven protection"]},
        ],
    },
    {
        "title": "Real Estate vs Stocks — Kahan Invest Karein",
        "title_en": "Real Estate vs Stocks — Which Is Better For Building Wealth",
        "category": "Investment Comparison",
        "level": "Beginner",
        "description": "Complete comparison of real estate and stock market investment in India",
        "target_audience": "Indian investors making the choice, global parallel with USA/UK market",
        "slides": [
            {"heading": "Real Estate vs Stocks — The Great Debate", "points": ["Both have created millionaires in India — both can create for you too", "Correct answer depends on: your income, time, knowledge, location", "Most Indians prefer real estate: tangible, emotional security", "Most financial experts prefer stocks: liquidity, compound returns, no maintenance", "Truth: both in portfolio is the smartest long-term approach"]},
            {"heading": "Real Estate Ke Fayde", "points": ["Tangible asset: can see, touch, live in — emotional peace", "Leverage: Rs.20 lakh down payment, buy Rs.1 crore property", "Rental income: passive cash flow every month", "Status: property = social recognition in India still strong", "Inflation hedge: land supply limited, cities growing — prices tend to rise"]},
            {"heading": "Real Estate Ki Limitations", "points": ["Illiquid: selling takes months, cannot sell part of a house", "High transaction costs: registration, stamp duty, brokerage — 8-10%", "Maintenance cost: repairs, property tax, society charges ongoing", "Location risk: buying in wrong area = property stuck for years", "Black money still prevalent — not fully transparent market"]},
            {"heading": "Stocks Ke Fayde — What Real Estate Cannot Offer", "points": ["Liquidity: sell Rs.1 lakh of stocks in seconds — real estate takes months", "Fractional ownership: invest Rs.500 in Reliance — no minimum threshold", "Diversification: own 20 companies across 10 sectors easily", "Transparency: price discovered live, every transaction recorded", "No maintenance: stock doesn't need plumber, painter, or tenant management"]},
            {"heading": "The Smart Investor's Approach", "points": ["Home ownership: yes — emotional and practical anchor for family", "Investment real estate: only if you understand the local market deeply", "REITs in India: Embassy Office Parks, Nexus Malls — invest in real estate like stocks", "Core wealth: stocks and equity mutual funds for long-term compounding", "Simple rule: home to live in + systematic equity investing = solid foundation"]},
        ],
    },
    {
        "title": "Emergency Fund aur Financial Safety Net",
        "title_en": "Emergency Fund and Financial Safety Net — The Foundation of Wealth",
        "category": "Personal Finance",
        "level": "Beginner",
        "description": "Why emergency fund is essential before any investment",
        "target_audience": "Global beginners starting financial journey",
        "slides": [
            {"heading": "Emergency Fund Kya Hai aur Kyu Zaroori Hai", "points": ["6 months of living expenses saved in liquid, accessible account", "Not for investment — only for true emergencies: job loss, medical", "Without it: forced to sell investments at wrong time during crisis", "With it: market crash = buying opportunity, not panic selling", "This is the foundation — build this BEFORE starting any investment"]},
            {"heading": "Kitna Emergency Fund Chahiye", "points": ["Minimum: 3 months expenses for single person with stable income", "Recommended: 6 months for married with dependents", "Maximum: 12 months for self-employed or variable income", "Calculate your monthly essential expenses: rent, food, EMIs, utilities, insurance", "Keep that amount × 6 in liquid fund — not in stocks, not locked in FD"]},
            {"heading": "Where to Keep Emergency Fund", "points": ["Liquid mutual fund: best option — 7-8% returns, same day withdrawal", "Savings account with high interest: 4-7% at some small finance banks", "Fixed deposit with premature withdrawal allowed: slightly lower return", "NOT in stocks: stocks can fall 40% exactly when you need the money most", "NOT in physical cash: inflation eats it, not safe, no returns"]},
            {"heading": "Building Emergency Fund Systematically", "points": ["Start small: Rs.5000 per month into liquid fund — habit more important than amount", "Before any other investment — this comes first, always", "Tax: liquid fund gains taxed at income slab rate — small cost for peace of mind", "Replenish immediately: if you use it for emergency, rebuild it first priority", "Treat it as sacred: do not touch it except for genuine emergency"]},
            {"heading": "Beyond Emergency Fund — Full Safety Net", "points": ["Term insurance: 10-20x annual income covered — family protected if you die", "Health insurance: Rs.5-10 lakh minimum — healthcare costs rising fast in India", "Disability insurance: often overlooked — disability more common than death", "Will: make sure your assets go to right people after you", "With this safety net complete: invest aggressively for wealth creation"]},
        ],
    },
    {
        "title": "Retirement Planning — 60 Saal Mein Aaram",
        "title_en": "Retirement Planning — How to Retire Comfortably at 60",
        "category": "Retirement",
        "level": "All Levels",
        "description": "NPS, EPF, and retirement corpus calculation for Indians",
        "target_audience": "Working professionals India — global parallel for USA UK",
        "slides": [
            {"heading": "Retirement Planning Kyu Early Start Karna Chahiye", "points": ["At 25: invest Rs.5000/month, retire at 60 = Rs.5 crore+ at 12% return", "At 35: invest Rs.15000/month to reach same amount — 3x the amount", "At 45: invest Rs.50000/month — 10x the amount for same result", "Every decade you delay = exponentially more needed later", "Compounding is most powerful with time — time is your most valuable asset"]},
            {"heading": "NPS — National Pension System", "points": ["Government-backed retirement account — very low cost (0.01% expense ratio)", "80CCD deduction: Rs.2 lakh additional tax saving beyond normal 80C", "Partial withdrawal allowed for specified purposes before retirement", "At retirement: 60% lump sum withdrawal, 40% compulsory annuity", "Equity option in NPS: up to 75% in stocks — best for young investors"]},
            {"heading": "EPF — Employee Provident Fund", "points": ["Mandatory for salaried employees: 12% of basic salary from you + employer match", "Government guaranteed 8.15% interest — risk-free guaranteed return", "Tax-free on contribution, interest, and withdrawal after 5 years", "EPFO portal: check your balance monthly — ensure employer depositing on time", "Do NOT withdraw EPF when changing jobs — let it compound for retirement"]},
            {"heading": "How Much Corpus Do You Need", "points": ["Monthly expense today Rs.50000: at 60 with 6% inflation = Rs.2.5 lakh/month", "To generate Rs.2.5 lakh/month at 8% withdrawal rate: need Rs.3.75 crore", "Inflation significantly increases the number — always calculate with it", "Online calculators: ET Money, Groww retirement calculator — free and accurate", "Review your retirement goal every 5 years as income and expenses change"]},
            {"heading": "Building Your Retirement Portfolio", "points": ["Young (25-40): 80% equity, 20% debt — aggressive growth needed", "Middle (40-55): 60% equity, 30% debt, 10% gold — balance", "Near retirement (55-60): 40% equity, 40% debt, 20% stable — capital protection", "Post retirement: 30% equity (for growth), 70% income-generating assets", "Systematic withdrawal plan: take only what you need, let rest compound longer"]},
        ],
    },
    {
        "title": "Trading Mistakes Jo Sabne Ki — Aur Aapko Nahi Karni",
        "title_en": "Trading Mistakes Everyone Makes — And How to Avoid Them",
        "category": "Psychology",
        "level": "All Levels",
        "description": "The most costly trading mistakes with exact fixes for each",
        "target_audience": "All traders globally",
        "slides": [
            {"heading": "Galti 1 — No Stop Loss", "points": ["Sabse common aur sabse costly galti: trade enter karna bina stop loss ke", "Hope is not a strategy: hoping stock will come back = recipe for disaster", "Solution: stop loss set karo BEFORE entering — never after", "Hard stop: order place karo broker system mein — automatic exit", "Rule: if you cannot define your stop loss, you should not enter the trade"]},
            {"heading": "Galti 2 — Revenge Trading", "points": ["After a loss: immediately trying to 'win back' the money — disaster", "Emotional state after loss = worst time to make any trading decision", "Revenge trader doubles size, lowers standards — compound the loss", "Solution: 30 minute rule — no new trades for 30 minutes after a loss", "Daily loss limit: if down 2% today — close laptop, done for the day"]},
            {"heading": "Galti 3 — Averaging Down Losing Position", "points": ["Buying more when price falls — feels like getting a bargain", "Reality: you were wrong, price is telling you — listen to the market", "Averaging down multiplies your loss on the side that is already losing", "Exception: only for high conviction long-term investments, not trading", "Solution: cut losses at predefined stop — never add to a losing trade"]},
            {"heading": "Galti 4 — FOMO Buying at Tops", "points": ["Stock already moved 20%, friends all talking about it — you want in", "This is exactly when smart money is selling to you — the late buyer", "Messi's goal made more beautiful because you watched it — no need to have been on field", "Solution: if stock already moved 10%+ from pivot without you — skip it", "There is always another opportunity — patience prevents FOMO disasters"]},
            {"heading": "Galti 5 — Ignoring Position Sizing", "points": ["Putting 50% of account in one stock 'because you are sure' — deadly", "Even the best trade can go wrong — no certainty exists in markets", "Maximum 15-20% of account in any one position — always", "Even Warren Buffett with all his resources maintains diversification", "Solution: position sizing calculator — Rs. amount to risk ÷ stop distance = shares"]},
        ],
    },
    {
        "title": "Financial Independence — FIRE Movement India",
        "title_en": "Financial Independence — Retire Early FIRE Movement India",
        "category": "Financial Freedom",
        "level": "All Levels",
        "description": "How to achieve financial independence in India, FIRE numbers",
        "target_audience": "Ambitious young investors globally",
        "slides": [
            {"heading": "FIRE Kya Hai", "points": ["FIRE = Financial Independence Retire Early", "Not about retiring at 30 to do nothing — about having CHOICE", "Work because you want to, not because you have to — massive freedom", "Growing movement globally: India, USA, UK all have active FIRE communities", "Core idea: save and invest aggressively for 10-20 years, live off returns"]},
            {"heading": "Your FIRE Number — How Much Do You Need", "points": ["25x annual expenses = your FIRE number (4% safe withdrawal rule)", "Monthly expense Rs.50000 = Rs.6 lakh/year × 25 = Rs.1.5 crore FIRE number", "Monthly expense Rs.1 lakh = Rs.12 lakh/year × 25 = Rs.3 crore FIRE number", "At 8% return on corpus: withdraw 4%, leave 4% to inflation-proof the corpus", "Run your own numbers: FIRE Calculator at FIRECalc or ET Money"]},
            {"heading": "How to Reach FIRE Faster — The Levers", "points": ["Lever 1: Increase income — skills, promotion, side business, freelance", "Lever 2: Reduce expenses — lifestyle choices matter enormously here", "Lever 3: Increase investment returns — better allocation, reduce costs", "Save rate 50%+: reach FIRE in 15-17 years from any income level", "Save rate 75%+: reach FIRE in 7-10 years — extremely aggressive but possible"]},
            {"heading": "Indian FIRE Portfolio Strategy", "points": ["Accumulation phase: 80-90% equity, 10% gold, 10% debt", "At FIRE: 50% equity (for growth), 30% dividend stocks, 10% gold, 10% debt", "Rental income: real estate can provide inflation-indexed passive income stream", "Freelance or consulting: even 20-30 hours per month covers expenses comfortably", "Many FIREd Indians: do meaningful work on own terms — not full retirement"]},
            {"heading": "Your Action Plan — Start This Week", "points": ["This week: calculate your monthly essential expenses precisely", "This week: open demat account if not yet — Zerodha or Dhan", "This month: start SIP of minimum 30% of income — non-negotiable", "This year: build 3-6 month emergency fund fully", "This decade: follow the course, apply the knowledge, build real wealth"]},
        ],
    },
    {
        "title": "52-Week Course Review — Aapki Journey Yahaan Tak",
        "title_en": "52-Week Course Review — Your Complete Investment Journey",
        "category": "Course Completion",
        "level": "All Levels",
        "description": "Review of entire 52-week course, next steps, what to do now",
        "target_audience": "All students who completed the course",
        "slides": [
            {"heading": "52 Weeks Mein Kya Sikha", "points": ["Phase 1: Foundation — stock market basics, demat, SIP, technical analysis", "Phase 2: Fundamental — company analysis, valuation, sector rotation, macro", "Phase 3: Strategies — swing trading, options, breakout, position trading", "Phase 4: Advanced — Iron Condor, algo trading, portfolio construction, tax", "Phase 5: Mastery — gold, real estate, retirement, FIRE, common mistakes avoided"]},
            {"heading": "Theory Se Action Pe Aao", "points": ["Knowledge without action = zero result", "Open your demat account today if not done — 10 minutes", "Start your first SIP today — even Rs.500 is enough to begin", "Watch charts for 30 minutes every evening — this builds pattern recognition", "Paper trade for 30 days before risking real money — AI360 system available"]},
            {"heading": "Your 90-Day Action Plan", "points": ["Day 1-7: Open demat account, start emergency fund SIP", "Day 8-30: Paper trade with AI360 system, track every trade in journal", "Day 31-60: Start small real investment — Rs.5000 max in one quality stock", "Day 61-90: Review results, adjust, add second position if first working", "After 90 days: you will have more real trading experience than most Indians"]},
            {"heading": "Resources to Continue Learning", "points": ["Books: The Intelligent Investor (Graham), Market Wizards (Schwager)", "YouTube: AI360 Trading daily education videos — free, new content every week", "Telegram: t.me/ai360trading — free daily signals and market updates", "Website: ai360trading.in — articles, tools, membership for premium signals", "Community: join our growing community — learn from others' experiences too"]},
            {"heading": "Final Message — Aapki Journey Shuru Hoti Hai Yahaan Se", "points": ["Financial education is the highest-returning investment you will ever make", "Most people spend more time researching phones than their investments", "You have now invested time in the most important knowledge — money management", "Stock market is not gambling if approached with knowledge and system", "Go build your wealth — the market is open, the tools are in your hands, start now"]},
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════
# DAY-BASED TOPICS FOR ARTICLES AND OTHER GENERATORS
# These are unchanged — used by generate_articles.py etc.
# ══════════════════════════════════════════════════════════════════════

MONDAY_TOPICS = [
    {
        "title": "Options Trading Complete Beginner Guide",
        "category": "Options",
        "level": "Beginner",
        "target_primary": "India",
        "target_secondary": ["USA", "UK", "Brazil"],
        "seo_seed": "options trading for beginners India 2026 step by step",
        "long_tail_keywords": [
            "how to start options trading in India with 10000 rupees",
            "Nifty options buying strategy for beginners",
        ],
        "affiliate_angle": "open trading account to start options — Zerodha, Dhan",
        "slides": [],
    },
    {
        "title": "Option Selling — Collect Premium Like Insurance Companies Do",
        "category": "Options",
        "level": "Intermediate",
        "target_primary": "India",
        "target_secondary": ["USA", "UK"],
        "seo_seed": "option selling strategy India monthly income 2026",
        "long_tail_keywords": ["how to earn monthly income from option selling Nifty"],
        "affiliate_angle": "Zerodha Sensibull for option strategy builder",
        "slides": [],
    },
    {
        "title": "Understanding Greeks — Delta Theta Vega Gamma Made Simple",
        "category": "Options",
        "level": "Advanced",
        "target_primary": "Global",
        "target_secondary": ["India", "USA"],
        "seo_seed": "options Greeks explained simply delta theta vega India 2026",
        "long_tail_keywords": ["what is delta in options trading explained in Hindi"],
        "affiliate_angle": "Sensibull Greeks calculator",
        "slides": [],
    },
]

TUESDAY_TOPICS = [
    {
        "title": "Candlestick Patterns — The 5 That Actually Make Money",
        "category": "Technical Analysis",
        "level": "Beginner",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "UK"],
        "seo_seed": "candlestick patterns that work best stocks crypto Nifty 2026",
        "long_tail_keywords": ["which candlestick pattern is most reliable for Nifty trading"],
        "affiliate_angle": "TradingView free plan",
        "slides": [],
    },
    {
        "title": "Support and Resistance — How to Draw Levels That Actually Work",
        "category": "Technical Analysis",
        "level": "Beginner",
        "target_primary": "Global",
        "target_secondary": ["India", "USA"],
        "seo_seed": "how to draw support and resistance correctly for stocks India",
        "long_tail_keywords": ["how to find strong support resistance levels Nifty 50"],
        "affiliate_angle": "TradingView free charts",
        "slides": [],
    },
    {
        "title": "RSI Complete Guide — How to Actually Use It Profitably",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "Brazil"],
        "seo_seed": "RSI indicator how to use correctly stocks crypto Nifty 2026",
        "long_tail_keywords": ["RSI divergence how to spot and trade it on Nifty"],
        "affiliate_angle": "TradingView free RSI setup",
        "slides": [],
    },
]

WEDNESDAY_TOPICS = [
    {
        "title": "How to Read a Company's Balance Sheet",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "UK"],
        "seo_seed": "how to read balance sheet stock investing beginners 2026",
        "long_tail_keywords": ["how to analyse balance sheet for stock investing India beginners"],
        "affiliate_angle": "Screener.in for free Indian company financial data",
        "slides": [],
    },
    {
        "title": "Global Market Outlook — What Drives International Markets",
        "category": "Global Markets",
        "level": "Intermediate",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "UK"],
        "seo_seed": "global markets outlook 2026 India USA impact",
        "long_tail_keywords": ["how does US stock market affect Indian market Nifty"],
        "affiliate_angle": "International mutual funds for Indian investors",
        "slides": [],
    },
]

THURSDAY_TOPICS = [
    {
        "title": "SIP Strategy — How to Invest Rs.500 to Rs.50000 Per Month",
        "category": "Wealth Building",
        "level": "Beginner",
        "target_primary": "India",
        "target_secondary": ["Global"],
        "seo_seed": "SIP investment strategy 2026 beginners India wealth building",
        "long_tail_keywords": ["best SIP amount for salary 30000 India mutual fund"],
        "affiliate_angle": "Groww or Kuvera for direct mutual fund SIP — zero commission",
        "slides": [],
    },
    {
        "title": "Term Insurance — How Much Cover Do You Actually Need",
        "category": "Insurance",
        "level": "Beginner",
        "target_primary": "India",
        "target_secondary": ["Global"],
        "seo_seed": "term insurance India 2026 how much cover do I need",
        "long_tail_keywords": ["LIC vs HDFC Life term plan comparison 2026 India"],
        "affiliate_angle": "Policybazaar for term insurance comparison — largest in India",
        "slides": [],
    },
]

FRIDAY_TOPICS = [
    {
        "title": "Trading Psychology — Why 95 Percent of Traders Lose Money",
        "category": "Psychology",
        "level": "All Levels",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "UK"],
        "seo_seed": "why most traders fail psychology emotions trading 2026",
        "long_tail_keywords": ["how to control emotions while trading stocks India"],
        "affiliate_angle": "Trading journal apps — TraderVue free for basic",
        "slides": [],
    },
    {
        "title": "Risk Management — The Only Rule That Matters in Trading",
        "category": "Risk Management",
        "level": "All Levels",
        "target_primary": "Global",
        "target_secondary": ["India", "USA"],
        "seo_seed": "risk management trading position sizing stop loss 2026",
        "long_tail_keywords": ["how to set stop loss for swing trading India Nifty"],
        "affiliate_angle": "Zerodha for disciplined trading with built-in GTT orders",
        "slides": [],
    },
]

WEEKEND_TOPICS = [
    {
        "title": "Personal Finance For Indians — Complete 2026 Guide",
        "category": "Personal Finance",
        "level": "Beginner",
        "target_primary": "India",
        "target_secondary": ["Global"],
        "seo_seed": "personal finance India 2026 complete guide savings investment",
        "long_tail_keywords": ["how to manage salary 30000 and save invest India"],
        "affiliate_angle": "ETMONEY app for tracking and investing",
        "slides": [],
    },
    {
        "title": "Gold vs Stocks vs Real Estate — Best Investment 2026",
        "category": "Investment Comparison",
        "level": "Beginner",
        "target_primary": "India",
        "target_secondary": ["USA", "UK", "UAE"],
        "seo_seed": "gold vs stocks vs real estate India best investment 2026",
        "long_tail_keywords": ["should I invest in gold or stocks or real estate India 2026"],
        "affiliate_angle": "Zerodha Coin for gold ETF and stock investment together",
        "slides": [],
    },
]

HOLIDAY_TOPICS = [
    {
        "title": "Why Market Holidays Are the Best Time to Plan",
        "category": "Motivation",
        "level": "All Levels",
        "target_primary": "Global",
        "target_secondary": ["India"],
        "seo_seed": "stock market holiday trading preparation wealth mindset",
        "long_tail_keywords": ["what to do during stock market holiday as a trader"],
        "affiliate_angle": None,
        "slides": [],
    },
]


# ══════════════════════════════════════════════════════════════════════
# MAIN FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def get_todays_education_topic() -> dict:
    """
    v3.0: Returns the correct 52-week course topic for today.
    Week auto-calculated from COURSE_START date.
    Returns topic dict WITH "week" key — used by generate_education.py.

    Week 1 starts: May 15, 2026
    Week auto-advances every 7 days forever — no manual intervention needed.

    Returns:
        dict with keys: title, title_en, category, level, description,
                        target_audience, slides, week (NEW)
    """
    today = date.today()
    days_since_start = (today - COURSE_START).days
    week = (days_since_start // 7) + 1  # Week 1 on day 0-6, Week 2 on day 7-13, etc.
    week = max(1, min(week, 52))  # Cap between 1 and 52

    # Get topic for this week (0-indexed list)
    topic_index = (week - 1) % len(COURSE_52_WEEKS)
    topic = dict(COURSE_52_WEEKS[topic_index])
    topic["week"] = week

    print(f"📖 Course Week {week}: {topic['title']} — {topic.get('description','')}")
    return topic


def get_todays_article_topic() -> dict:
    """
    Returns day-of-week based topic for articles and other generators.
    Unchanged from v2.0 — used by generate_articles.py.
    """
    day = datetime.now().weekday()  # 0=Mon, 6=Sun
    topic_map = {
        0: MONDAY_TOPICS,
        1: TUESDAY_TOPICS,
        2: WEDNESDAY_TOPICS,
        3: THURSDAY_TOPICS,
        4: FRIDAY_TOPICS,
        5: WEEKEND_TOPICS,
        6: WEEKEND_TOPICS,
    }
    topics = topic_map.get(day, WEEKEND_TOPICS)
    # Rotate through topics for variety within the day
    week_num = datetime.now().isocalendar()[1]
    idx = week_num % len(topics)
    return topics[idx]


def get_todays_topics(mode: str = "market") -> list:
    """
    Returns list of article topics for today based on mode.
    Used by generate_articles.py.
    """
    if mode == "holiday":
        return HOLIDAY_TOPICS
    if mode == "weekend":
        return WEEKEND_TOPICS
    day = datetime.now().weekday()
    topic_map = {
        0: MONDAY_TOPICS,
        1: TUESDAY_TOPICS,
        2: WEDNESDAY_TOPICS,
        3: THURSDAY_TOPICS,
        4: FRIDAY_TOPICS,
    }
    return topic_map.get(day, WEEKEND_TOPICS)


if __name__ == "__main__":
    topic = get_todays_education_topic()
    print(f"\nEducation topic: Week {topic['week']} — {topic['title']}")
    print(f"Category: {topic['category']} | Level: {topic['level']}")
    print(f"Slides: {len(topic.get('slides', []))}")
    print(f"\nArticle topic today: {get_todays_article_topic()['title']}")
