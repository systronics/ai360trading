"""
AI360Trading — Smart Content Calendar
Every day = different educational topic based on what Indian traders
actually search for. Topics rotate intelligently by day-of-week.
"""

# ══════════════════════════════════════════════════════════
# CONTENT CALENDAR — What to teach on which day
# Monday   = Options & Derivatives (most searched on Mondays)
# Tuesday  = Technical Analysis & Indicators
# Wednesday= Fundamental + Sector + News Analysis
# Thursday = Strategies & Trade Setups (pre-expiry week)
# Friday   = Psychology, Risk, Weekly Review
# ══════════════════════════════════════════════════════════

MONDAY_TOPICS = [
    {
        "title": "Options Trading Basics — Call & Put Explained",
        "category": "Options",
        "level": "Beginner",
        "why_today": "Monday: fresh week, beginners start learning",
        "slides": [
            {"heading": "What is an Option?", "points": ["Right but not obligation to buy/sell","Call = right to BUY","Put = right to SELL","Premium is the price you pay","Expiry date — when it expires"], "visual": "comparison_table"},
            {"heading": "Call Option — How it Works", "points": ["You buy CALL when market will go UP","Example: Nifty at 22000, buy 22200 CE","If Nifty goes to 22500 — profit","If Nifty falls — max loss is premium paid","Risk is limited, reward is unlimited"], "visual": "payoff_chart"},
            {"heading": "Put Option — How it Works", "points": ["You buy PUT when market will go DOWN","Example: Nifty at 22000, buy 21800 PE","If Nifty falls to 21500 — profit","If Nifty rises — max loss is premium paid","Used for hedging your portfolio too"], "visual": "payoff_chart"},
            {"heading": "In The Money vs Out The Money", "points": ["ITM Call: Strike BELOW current price","OTM Call: Strike ABOVE current price","ATM: Strike = current price","ITM has intrinsic value","OTM is pure time value"], "visual": "levels_diagram"},
            {"heading": "Option Premium — What affects it?", "points": ["Underlying price movement","Time to expiry (theta decay)","Volatility (India VIX)","Interest rates","Dividends"], "visual": "factors_chart"},
            {"heading": "Common Beginner Mistakes in Options", "points": ["Buying far OTM options — lottery mindset","Holding till expiry hoping for recovery","Ignoring theta decay","Not using stop loss","Overtrading on expiry day"], "visual": "mistake_icons"},
            {"heading": "Golden Rules for Option Buyers", "points": ["Trade only with money you can lose","Set max loss per trade before entering","Exit at 30-40% profit — don't be greedy","Avoid trading first 15 min","Weekly expiry = faster theta decay"], "visual": "rules_checklist"},
        ]
    },
    {
        "title": "Option Chain Reading — Complete Guide",
        "category": "Options",
        "level": "Intermediate",
        "slides": [
            {"heading": "What is Option Chain?", "points": ["Live table of all strikes","Shows CE and PE data","OI = Open Interest = active contracts","Volume = contracts traded today","IV = Implied Volatility"], "visual": "option_chain_screenshot"},
            {"heading": "Open Interest — What it Tells You", "points": ["High CE OI at a strike = strong resistance","High PE OI at a strike = strong support","Rising OI with rising price = bullish","Rising OI with falling price = bearish","Unwinding OI = reversal signal"], "visual": "oi_chart"},
            {"heading": "Put Call Ratio (PCR)", "points": ["PCR = Total PE OI / Total CE OI","PCR above 1.2 = Bearish sentiment, often contrarian bullish","PCR below 0.8 = Bullish sentiment, often contrarian bearish","PCR 0.9 to 1.1 = Neutral market","Best used with price action"], "visual": "pcr_gauge"},
            {"heading": "Max Pain Theory", "points": ["Level where most option buyers lose","Market often gravitates toward max pain on expiry","Not always accurate but useful reference","Used by institutional traders","Check every week before expiry"], "visual": "max_pain_chart"},
            {"heading": "How to Find Support & Resistance", "points": ["Find strike with highest PE OI = support","Find strike with highest CE OI = resistance","These are your key levels for the week","Change weekly on Thursday after expiry","More reliable than normal S/R for short term"], "visual": "sr_diagram"},
        ]
    },
    {
        "title": "Option Selling — The Professional Strategy",
        "category": "Options",
        "level": "Advanced",
        "slides": [
            {"heading": "Why 90% of Options Expire Worthless", "points": ["Time decay (theta) destroys premium every day","Sellers collect premium = positive theta","Buyers fight time every single day","On expiry day — most OTM options go to zero","This is why sellers have statistical edge"], "visual": "theta_decay_curve"},
            {"heading": "Covered Call Strategy", "points": ["Own shares + Sell Call option","Generate monthly income from your shares","Example: Hold Reliance, Sell CE every month","Maximum profit = premium collected","Risk: stock rises sharply above strike"], "visual": "covered_call_diagram"},
            {"heading": "Cash Secured Put Strategy", "points": ["Sell Put on stock you want to own","Collect premium while waiting to buy","If stock falls below strike — you buy it cheap","If stock stays up — keep the premium","Warren Buffett uses this strategy"], "visual": "csp_diagram"},
            {"heading": "Iron Condor — Range Bound Strategy", "points": ["Sell OTM Call + Buy further OTM Call","Sell OTM Put + Buy further OTM Put","Profit when market stays in a range","Maximum loss is defined and limited","Best for sideways markets — like pre RBI policy"], "visual": "iron_condor_chart"},
            {"heading": "Risk Management for Option Sellers", "points": ["Never sell naked options without hedge","Keep margin buffer of 50% extra","Exit if premium doubles against you","Avoid holding through big events","Position size: max 5% of capital per trade"], "visual": "risk_table"},
        ]
    },
    {
        "title": "Greeks — Delta Gamma Theta Vega Explained",
        "category": "Options",
        "level": "Advanced",
        "slides": [
            {"heading": "What are Option Greeks?", "points": ["Mathematical measures of option sensitivity","Delta: sensitivity to price move","Gamma: rate of change of delta","Theta: time decay per day","Vega: sensitivity to volatility"], "visual": "greeks_overview"},
            {"heading": "Delta — The Most Important Greek", "points": ["ATM option delta = 0.5","ITM option delta approaches 1.0","OTM option delta approaches 0","Delta 0.5 means: Nifty up 100 = option up 50","Use delta to understand your real market exposure"], "visual": "delta_chart"},
            {"heading": "Theta — Your Enemy as Buyer", "points": ["Theta = premium lost per day due to time","ATM option loses most theta","Accelerates rapidly in last week","Weekly expiry: highest theta decay Thursday-Friday","This is why option buyers must be quick"], "visual": "theta_decay"},
            {"heading": "Vega — Volatility's Role", "points": ["High VIX = expensive options (high vega)","Buy options when VIX is low","Sell options when VIX is high","Event days: VIX spikes before, crashes after","Budget day: sell options after 11 AM when VIX falls"], "visual": "vega_vix_chart"},
        ]
    },
]

TUESDAY_TOPICS = [
    {
        "title": "Candlestick Patterns — Complete Visual Guide",
        "category": "Technical Analysis",
        "level": "Beginner",
        "slides": [
            {"heading": "How to Read a Candle", "points": ["Green candle = price went UP","Red candle = price went DOWN","Body = open to close range","Wick = high and low extremes","Long wick = rejection of that price level"], "visual": "candle_anatomy"},
            {"heading": "Doji — Indecision Candle", "points": ["Open and close almost equal","Market is indecisive","Strong signal after a big trend","Dragonfly Doji = bullish reversal","Gravestone Doji = bearish reversal"], "visual": "doji_types"},
            {"heading": "Hammer & Hanging Man", "points": ["Long lower wick, small body at top","Hammer at bottom = BULLISH reversal","Hanging Man at top = BEARISH reversal","Confirmation candle is important","One of most reliable single candle patterns"], "visual": "hammer_chart"},
            {"heading": "Engulfing Pattern", "points": ["Second candle completely covers first","Bullish Engulfing: red then big green","Bearish Engulfing: green then big red","Most powerful at key support/resistance","Volume should be higher on engulfing candle"], "visual": "engulfing_chart"},
            {"heading": "Morning Star & Evening Star", "points": ["3-candle reversal patterns","Morning Star: bearish + doji + bullish = BUY","Evening Star: bullish + doji + bearish = SELL","Most reliable at end of strong trends","Confirmation: third candle closes above/below midpoint"], "visual": "star_patterns"},
            {"heading": "Shooting Star & Inverted Hammer", "points": ["Long upper wick, small body at bottom","Shooting Star at TOP = bearish reversal","Inverted Hammer at BOTTOM = bullish reversal","Wick shows rejection of higher prices","Always confirm with next candle"], "visual": "shooting_star"},
        ]
    },
    {
        "title": "RSI — How to Use it Correctly",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "slides": [
            {"heading": "What is RSI?", "points": ["Relative Strength Index","Range: 0 to 100","Above 70 = Overbought","Below 30 = Oversold","Default period: 14 days"], "visual": "rsi_gauge"},
            {"heading": "RSI Divergence — Most Powerful Signal", "points": ["Price makes new high, RSI makes lower high = BEARISH divergence","Price makes new low, RSI makes higher low = BULLISH divergence","Divergence warns of trend reversal","Works on all timeframes","Most reliable signal RSI gives"], "visual": "divergence_chart"},
            {"heading": "RSI in Trending Markets", "points": ["In strong uptrend: RSI stays 50-80","In strong downtrend: RSI stays 20-50","Overbought in uptrend = buy signal, not sell","Oversold in downtrend = sell signal, not buy","Always check the bigger trend first"], "visual": "rsi_trend"},
            {"heading": "RSI 50 Level — The Trend Filter", "points": ["RSI above 50 = bullish momentum","RSI below 50 = bearish momentum","RSI crossing 50 upward = trend change","Only take buy trades when RSI above 50","Only take sell trades when RSI below 50"], "visual": "rsi_50_chart"},
            {"heading": "RSI Failure Swings", "points": ["RSI enters overbought, pulls back, fails to reach 70 again = SELL","RSI enters oversold, bounces, fails to reach 30 again = BUY","More reliable than simple overbought/oversold","Used by professional traders","Works well on daily charts"], "visual": "failure_swing"},
        ]
    },
    {
        "title": "Moving Averages — Complete Masterclass",
        "category": "Technical Analysis",
        "level": "Beginner",
        "slides": [
            {"heading": "What is a Moving Average?", "points": ["Average of last N closing prices","Smooths out price noise","Shows the direction of trend","EMA reacts faster than SMA","Most used: 20, 50, 200 EMA"], "visual": "ma_chart"},
            {"heading": "Golden Cross & Death Cross", "points": ["Golden Cross: 50 EMA crosses above 200 EMA = STRONG BUY","Death Cross: 50 EMA crosses below 200 EMA = STRONG SELL","Long-term trend change signals","Lagging but very reliable","Used by mutual funds and institutions"], "visual": "golden_cross"},
            {"heading": "20 EMA — The Trader's Friend", "points": ["Price above 20 EMA = short-term uptrend","Price below 20 EMA = short-term downtrend","20 EMA acts as dynamic support in uptrend","Bounce from 20 EMA = buy opportunity","Break below 20 EMA = exit long positions"], "visual": "ema20_chart"},
            {"heading": "200 EMA — The Big Trend Line", "points": ["Price above 200 EMA = long-term bull market","Price below 200 EMA = long-term bear market","200 EMA = strongest support/resistance","Nifty above 200 EMA = stay invested","Nifty below 200 EMA = be cautious with longs"], "visual": "ema200_chart"},
            {"heading": "EMA Crossover Strategy", "points": ["Buy: 20 EMA crosses above 50 EMA","Sell: 20 EMA crosses below 50 EMA","Works best on daily and weekly charts","Add RSI confirmation to reduce false signals","Best for positional and swing traders"], "visual": "crossover_strategy"},
        ]
    },
    {
        "title": "Chart Patterns — Head Shoulders Double Top Bottom",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "slides": [
            {"heading": "Head and Shoulders — Most Reliable Pattern", "points": ["Left shoulder + Head (highest) + Right shoulder","Neckline connects the two lows","Break below neckline = STRONG SELL","Target = Head height projected down","Volume decreases on right shoulder"], "visual": "head_shoulders"},
            {"heading": "Double Top — Bearish Reversal", "points": ["Two peaks at same resistance level","Market tried twice and failed","Break below middle trough = SELL","Target = distance from top to trough","RSI usually shows divergence on second top"], "visual": "double_top"},
            {"heading": "Double Bottom — Bullish Reversal", "points": ["Two troughs at same support level","Market found buyers at same level twice","Break above middle peak = BUY","Target = distance from bottom to peak","Volume higher on second bottom breakout"], "visual": "double_bottom"},
            {"heading": "Triangle Patterns", "points": ["Ascending Triangle: flat top + rising lows = bullish","Descending Triangle: flat bottom + falling highs = bearish","Symmetrical Triangle: breakout direction = trend continuation","Trade the breakout with volume confirmation","Stop loss below/above the triangle"], "visual": "triangle_types"},
            {"heading": "Flag & Pennant — Continuation Patterns", "points": ["Strong move (pole) then consolidation (flag/pennant)","Flag: parallel channels","Pennant: converging lines","Both break in direction of original move","One of highest success rate patterns"], "visual": "flag_pennant"},
        ]
    },
]

WEDNESDAY_TOPICS = [
    {
        "title": "How to Read Company Fundamentals",
        "category": "Fundamental Analysis",
        "level": "Beginner",
        "slides": [
            {"heading": "What is Fundamental Analysis?", "points": ["Study of company's financial health","Revenue, profit, debt, growth","Not chart — it is business analysis","Long-term investing approach","Warren Buffett uses this method"], "visual": "fa_overview"},
            {"heading": "P/E Ratio — Price to Earnings", "points": ["Stock price divided by EPS","P/E 15 means paying 15 years of earnings","Low P/E vs sector = possibly undervalued","High P/E = growth expectations priced in","Compare within same sector only"], "visual": "pe_comparison"},
            {"heading": "Debt to Equity Ratio", "points": ["Total debt divided by shareholders equity","Low D/E = financially strong company","D/E above 1.5 = high debt risk","Banks and NBFCs naturally have high D/E","Avoid high D/E companies in rising interest rate era"], "visual": "debt_chart"},
            {"heading": "Return on Equity (ROE)", "points": ["Net profit divided by shareholders equity","ROE above 15% = good business","ROE above 20% = excellent business","Consistent ROE = quality company","Look for improving ROE trend over 5 years"], "visual": "roe_chart"},
            {"heading": "How to Find Quality Stocks", "points": ["ROE above 15% consistently","Low debt (D/E below 0.5)","Revenue growing 15%+ per year","Positive free cash flow","Promoter holding stable or increasing"], "visual": "quality_checklist"},
        ]
    },
    {
        "title": "Sector Rotation — Follow Smart Money",
        "category": "Sector Analysis",
        "level": "Intermediate",
        "slides": [
            {"heading": "What is Sector Rotation?", "points": ["Money moves from sector to sector in cycles","FII and mutual funds drive this rotation","Riding the right sector = 2-3x better returns","Technology leads in bull markets","FMCG and Pharma lead in bear markets"], "visual": "rotation_cycle"},
            {"heading": "Economic Cycle and Sectors", "points": ["Recovery: Banks, Auto, Real Estate","Expansion: IT, Capital Goods, Consumer","Peak: Energy, Metals, Materials","Recession: FMCG, Pharma, Utilities","Know where we are in the cycle"], "visual": "economic_cycle"},
            {"heading": "How to Identify Leading Sectors", "points": ["Compare sector index vs Nifty50","Sector making new highs while Nifty stagnates = leadership","Sector relative strength vs Nifty","FII buying data sector-wise","Mutual fund holdings quarterly data"], "visual": "sector_comparison"},
            {"heading": "Nifty Sector Indices to Track", "points": ["Nifty Bank — biggest weight in Nifty","Nifty IT — global tech sentiment","Nifty Auto — rural demand indicator","Nifty Pharma — defensive sector","Nifty Realty — interest rate sensitive"], "visual": "sector_indices"},
            {"heading": "Sector Rotation Trading Strategy", "points": ["Monthly review which sectors outperforming","Shift capital to top 2-3 sectors","Exit sectors showing relative weakness","Never put all capital in one sector","Best strategy for 6-12 month holding"], "visual": "rotation_strategy"},
        ]
    },
    {
        "title": "How News & Events Move Markets",
        "category": "News & Events",
        "level": "Beginner",
        "slides": [
            {"heading": "Events that Move Markets Most", "points": ["RBI Monetary Policy — interest rates","Union Budget — February every year","US Federal Reserve policy","Quarterly earnings results","Global geopolitical events"], "visual": "events_calendar"},
            {"heading": "How to Trade RBI Policy Day", "points": ["Market volatile before announcement","Buy straddle 2 days before if VIX low","After announcement: trend usually continues","Rate cut = Bank Nifty rally","Rate hike = Bank Nifty falls"], "visual": "rbi_trade"},
            {"heading": "Budget Day Strategy", "points": ["Most volatile day of the year","Avoid taking new positions morning of budget","Wait for direction after 1 PM","Sector plays: infrastructure, defence, agriculture","Sell options day before — collect premium from VIX spike"], "visual": "budget_strategy"},
            {"heading": "Quarterly Results Trading", "points": ["Check results calendar every week","Buy before results only if technically strong","Avoid holding through results unless long-term","Good results in weak market = sell the news","Bad results in strong market = buy the dip"], "visual": "results_strategy"},
            {"heading": "Global Events Checklist", "points": ["US Jobs data (first Friday every month)","US CPI inflation data","Fed meeting minutes","China PMI data","Oil prices — directly affects Indian market"], "visual": "global_calendar"},
        ]
    },
    {
        "title": "IPO Investing — How to Evaluate and Apply",
        "category": "IPO & New Listings",
        "level": "Beginner",
        "slides": [
            {"heading": "What is an IPO?", "points": ["Company selling shares to public first time","Primary market — money goes to company","Price band set by investment bankers","Apply through broker or UPI ASEAN","Allotment is lottery based if oversubscribed"], "visual": "ipo_process"},
            {"heading": "How to Evaluate an IPO", "points": ["Read DRHP — Draft Red Herring Prospectus","Check why company needs money","Look at promoter reputation and holding","Compare valuation with listed peers","Avoid IPOs where existing investors fully exit"], "visual": "ipo_checklist"},
            {"heading": "Grey Market Premium (GMP)", "points": ["Unofficial indicator of listing price expectation","High GMP = strong listing expected","GMP can be manipulated — use with caution","Good proxy but not guarantee","Check GMP 2-3 days before listing"], "visual": "gmp_chart"},
            {"heading": "IPO Listing Strategy", "points": ["Sell on listing day if profit above 20%","Hold quality IPOs for 6-12 months","Never apply for IPOs with borrowed money","Diversify — apply in multiple IPOs","Subscription 50x+ = good demand signal"], "visual": "listing_strategy"},
        ]
    },
]

THURSDAY_TOPICS = [
    {
        "title": "Intraday Trading — Complete Strategy Guide",
        "category": "Trading Strategy",
        "level": "Intermediate",
        "slides": [
            {"heading": "Golden Rules of Intraday Trading", "points": ["Never carry intraday position overnight","Set daily loss limit — stop when hit","Trade only in high volume stocks/indices","Avoid first 15 minutes of market open","Square off all positions before 3:15 PM"], "visual": "golden_rules"},
            {"heading": "Opening Range Breakout (ORB)", "points": ["Mark high and low of first 15 minutes","Buy on break above 15 min high","Sell on break below 15 min low","Stop loss = other side of range","Target = 1.5x to 2x the range size"], "visual": "orb_chart"},
            {"heading": "VWAP Strategy", "points": ["VWAP = Volume Weighted Average Price","Price above VWAP = bullish intraday","Price below VWAP = bearish intraday","Buy bounce from VWAP in uptrend","Institutions trade around VWAP all day"], "visual": "vwap_chart"},
            {"heading": "Best Times to Trade Intraday", "points": ["9:30-11:00 AM: Most volatile, best moves","11:00-1:00 PM: Slower, avoid overtrading","1:00-2:00 PM: Lunch lull, low volume","2:00-3:15 PM: Second good window","Avoid last 15 minutes — erratic moves"], "visual": "time_chart"},
            {"heading": "Risk Management for Intraday", "points": ["Max loss per trade = 0.5% of capital","Max daily loss = 2% of capital","Risk:Reward minimum 1:2","Never average a losing intraday trade","Reduce size after 2 consecutive losses"], "visual": "risk_rules"},
            {"heading": "Stocks Best for Intraday", "points": ["High liquidity — Nifty 50 stocks only","High ATR = good daily range","Avoid stocks in news (too unpredictable)","Bank Nifty and Nifty futures — best","Avoid small cap and mid cap for intraday"], "visual": "stock_selection"},
        ]
    },
    {
        "title": "Positional Trading — Swing Trade Masterclass",
        "category": "Trading Strategy",
        "level": "Intermediate",
        "slides": [
            {"heading": "What is Positional Trading?", "points": ["Hold trades for days to weeks","Based on daily and weekly charts","Less stressful than intraday","Better risk:reward ratios possible","Perfect for working professionals"], "visual": "position_overview"},
            {"heading": "How to Find Swing Trades", "points": ["Stock in strong uptrend (above all EMAs)","Wait for pullback to 20 EMA","RSI pulling back to 40-50 zone","Volume declining on pullback","Buy when price bounces with volume"], "visual": "swing_setup"},
            {"heading": "Weekly Chart Analysis", "points": ["Weekly chart = most important for positional","Candle closing above resistance on weekly = strong buy","Weekly 200 EMA = major trend decider","Weekly RSI above 60 = strong momentum","Trade with weekly trend, not against it"], "visual": "weekly_chart"},
            {"heading": "Position Sizing for Swing Trades", "points": ["Risk max 2% of total capital per trade","Calculate share quantity from stop loss","If SL is 5% away: position = 2%/5% = 40% of capital","This controls loss perfectly","Never bet more than 10% in one stock"], "visual": "position_sizing"},
            {"heading": "Exit Strategy for Positional Trades", "points": ["Trailing stop loss — move up as profit increases","Exit 50% at first target","Let remaining run with trailing SL","Time stop: exit if thesis not playing out in 2 weeks","Never convert positional to long-term investment"], "visual": "exit_strategy"},
        ]
    },
    {
        "title": "Fibonacci Retracement — Professional Trading Tool",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "slides": [
            {"heading": "What is Fibonacci?", "points": ["Golden ratio found in nature","38.2%, 50%, 61.8% are key levels","After a big move, market retraces to these levels","Works because millions of traders watch same levels","Self-fulfilling prophecy of technical analysis"], "visual": "fibonacci_overview"},
            {"heading": "How to Draw Fibonacci", "points": ["In uptrend: draw from swing low to swing high","In downtrend: draw from swing high to swing low","Watch 38.2% and 61.8% most carefully","50% is also a strong psychological level","Multiple timeframe confluence = strongest signal"], "visual": "fibonacci_drawing"},
            {"heading": "Fibonacci + RSI Strategy", "points": ["Price at 61.8% retracement = golden zone","RSI at 40-50 zone at same time = buy signal","Place stop below 78.6% level","Target: previous high = full retracement","Risk:Reward typically 1:3 or better"], "visual": "fib_rsi_strategy"},
            {"heading": "Fibonacci Extensions — Finding Targets", "points": ["After breakout, where will price go?","127.2%, 161.8%, 261.8% are extension levels","Draw from swing low to high to the retracement","161.8% is the most common target","Use to set realistic profit targets"], "visual": "fib_extension"},
        ]
    },
    {
        "title": "Supply & Demand Zones — How Institutions Trade",
        "category": "Trading Strategy",
        "level": "Advanced",
        "slides": [
            {"heading": "What are Supply & Demand Zones?", "points": ["Areas where institutions placed big orders","Demand zone: area where big buying happened","Supply zone: area where big selling happened","Price returns to these zones to fill remaining orders","More powerful than normal support/resistance"], "visual": "sd_overview"},
            {"heading": "How to Identify Demand Zones", "points": ["Big bullish candle after sideways consolidation","The consolidation before the big move = demand zone","Price left that area fast = strong unfilled orders remain","Mark the consolidation as the zone","Wait for price to return to that zone to buy"], "visual": "demand_zone"},
            {"heading": "How to Identify Supply Zones", "points": ["Big bearish candle after sideways consolidation","The consolidation before the big drop = supply zone","Price dropped sharply = strong sellers at that level","Mark the consolidation as the supply zone","Wait for price to return to sell/short"], "visual": "supply_zone"},
            {"heading": "Trading Supply & Demand Zones", "points": ["Enter at the zone, not after breakout","Tight stop loss just beyond the zone","First time price revisits = highest probability","Zone loses power once tested multiple times","Works on all timeframes — 5 min to weekly"], "visual": "sd_trade_setup"},
            {"heading": "Why this is How Institutions Think", "points": ["Retail traders see support/resistance on charts","Institutions see unfilled order blocks","This is why charts look the same — same orders","Smart money buys demand, sells supply","Understanding this = trading like a professional"], "visual": "institutional_flow"},
        ]
    },
]

FRIDAY_TOPICS = [
    {
        "title": "Trading Psychology — Why Most Traders Fail",
        "category": "Psychology",
        "level": "All Levels",
        "slides": [
            {"heading": "The Real Reason 90% Traders Lose", "points": ["Not lack of strategy — lack of discipline","Greed: holding winners too long","Fear: cutting winners too early","Hope: holding losers too long","Revenge: trading bigger after a loss"], "visual": "psychology_cycle"},
            {"heading": "Greed — How it Destroys Accounts", "points": ["Good trade running, target hit — but not exiting","Market turns, profit becomes loss","Doubling position size after winning streak","Trading in F&O with all savings","FOMO trading — entering after big moves"], "visual": "greed_chart"},
            {"heading": "Fear — The Paralysis Trap", "points": ["Perfect setup, but not entering","Exiting at small profit, missing big move","Not taking loss early, hoping for recovery","Reducing position too much after a loss","Fear of missing out leads to impulsive entries"], "visual": "fear_chart"},
            {"heading": "Revenge Trading — Account Killer", "points": ["Lost money, now trading bigger to recover","This leads to even bigger losses","Emotional state = worst time to trade","Solution: stop after 2 losses in a day","Walk away, come back tomorrow fresh"], "visual": "revenge_trade"},
            {"heading": "Building Mental Discipline", "points": ["Write down rules BEFORE trading","Follow rules even when emotions say otherwise","Journal every trade — review weekly","Accept losses as cost of doing business","Consistency beats brilliance in trading"], "visual": "discipline_rules"},
            {"heading": "The Professional Trader Mindset", "points": ["Focus on process, not profits","Every trade is just one of 1000 trades","No single trade defines you","Small consistent profits beat occasional big wins","Trading is a marathon, not a sprint"], "visual": "pro_mindset"},
        ]
    },
    {
        "title": "Risk Management — The Only Thing That Matters",
        "category": "Risk Management",
        "level": "All Levels",
        "slides": [
            {"heading": "The Golden Rule of Trading", "points": ["Preserve capital at all costs","A 50% loss needs 100% gain to recover","A 25% loss needs only 33% to recover","Protecting capital is more important than making money","Live to trade another day"], "visual": "recovery_chart"},
            {"heading": "Position Sizing — The Science", "points": ["Risk per trade = 1-2% of total capital","If capital is 1 lakh: max loss per trade = 1000-2000","Calculate share quantity from this","Never increase size because you are confident","Consistency in position size = consistency in results"], "visual": "position_formula"},
            {"heading": "Stop Loss — Non-Negotiable Rule", "points": ["Every trade must have a stop loss before entry","Stop loss is not optional — it is mandatory","Mental stop loss does not work — place it in system","Move stop to breakeven after 1:1 profit","Trailing stop loss protects profits automatically"], "visual": "stop_loss_types"},
            {"heading": "The 2% Rule", "points": ["Never risk more than 2% on any single trade","With 1 lakh capital: max loss per trade = 2000","This means you can have 50 losing trades before wiping out","Gives you time to learn and improve","Even George Soros uses this principle"], "visual": "two_percent_rule"},
            {"heading": "Building Your Personal Risk Plan", "points": ["Daily loss limit: stop trading at -3% day","Weekly loss limit: review strategy at -6% week","Monthly loss limit: stop trading at -10% month","Review all trades that hit stop loss","Keep a trading journal — it will save your account"], "visual": "risk_plan"},
        ]
    },
    {
        "title": "How to Build a Trading Plan — Step by Step",
        "category": "Trading Plan",
        "level": "All Levels",
        "slides": [
            {"heading": "Why You Need a Trading Plan", "points": ["Plan removes emotion from trading","Without plan: gambling, not trading","Plan tells you exactly what to do","Review plan when market is closed, not open","Professionals have written trading plans"], "visual": "plan_overview"},
            {"heading": "Define Your Trading Style", "points": ["Intraday: need full day free","Swing: check once daily, 1-5 day holds","Positional: check weekly, weeks to months hold","Long-term investing: quarterly review","Match your style to your schedule and personality"], "visual": "style_matrix"},
            {"heading": "Your Entry Rules", "points": ["What setup am I looking for?","Which timeframe am I trading?","What indicators confirm my entry?","What is my entry price exactly?","Am I entering market order or limit order?"], "visual": "entry_rules"},
            {"heading": "Your Exit Rules", "points": ["Where is my stop loss? (write exact price)","Where is my target? (write exact price)","Will I trail stop after profit?","How much time will I give trade to work?","Will I scale out or exit all at once?"], "visual": "exit_rules"},
            {"heading": "Weekly Review Process", "points": ["Every Sunday: review all trades of the week","Calculate win rate and risk:reward","Identify which setups are working","Remove setups that are not working","This continuous improvement is how you grow"], "visual": "review_process"},
        ]
    },
    {
        "title": "Mutual Funds vs Stocks vs FD — Complete Guide",
        "category": "Personal Finance",
        "level": "Beginner",
        "slides": [
            {"heading": "Where Should You Invest?", "points": ["FD: safe, 6-7% return, fully taxable","Mutual Fund: 10-15% average over long term","Direct Stocks: 15-20% possible, higher risk","Gold: hedge, not primary investment","Real Estate: illiquid, high entry cost"], "visual": "investment_comparison"},
            {"heading": "SIP — Systematic Investment Plan", "points": ["Invest fixed amount every month in mutual fund","Rupee cost averaging — buy more when market falls","5000 per month for 20 years = 50 lakh+ at 12%","Best for salaried people — automate it","SIP in Nifty50 index fund = simplest strategy"], "visual": "sip_calculator"},
            {"heading": "Index Fund vs Active Fund", "points": ["Index fund: mimics Nifty50, expense ratio 0.1%","Active fund: fund manager picks stocks, expense 1-2%","80% of active funds underperform Nifty over 10 years","Index fund = best choice for most people","Warren Buffett recommends index funds for all"], "visual": "index_vs_active"},
            {"heading": "How to Start Investing with 500 Rupees", "points": ["Open Zerodha or Groww or Angel One account","Start SIP in Nifty50 index fund with 500/month","Increase amount every year with salary hike","Never stop SIP during market crash — keep going","Compounding works best over 15-20 years"], "visual": "getting_started"},
        ]
    },
]

# Map weekday to topics (0=Monday, 4=Friday)
WEEKDAY_TOPICS = {
    0: MONDAY_TOPICS,    # Monday = Options
    1: TUESDAY_TOPICS,   # Tuesday = Technical Analysis
    2: WEDNESDAY_TOPICS, # Wednesday = Fundamentals + Sectors + News
    3: THURSDAY_TOPICS,  # Thursday = Strategies
    4: FRIDAY_TOPICS,    # Friday = Psychology + Risk
}

def get_todays_education_topic(today=None):
    """Returns the education topic for today based on smart rotation."""
    if today is None:
        today = datetime.now() if hasattr(__import__('datetime'), 'datetime') else None
    from datetime import datetime as dt
    now = dt.now()
    weekday = now.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun

    if weekday >= 5:
        weekday = 0  # Weekend defaults to Monday (Options)

    topics = WEEKDAY_TOPICS[weekday]

    # Rotate through topics by week number
    week_number = now.isocalendar()[1]
    topic_index = week_number % len(topics)

    return topics[topic_index]


if __name__ == "__main__":
    from datetime import datetime
    topic = get_todays_education_topic()
    print(f"Today's education topic: {topic['title']}")
    print(f"Category: {topic['category']}")
    print(f"Level: {topic['level']}")
    print(f"Slides: {len(topic['slides'])}")
