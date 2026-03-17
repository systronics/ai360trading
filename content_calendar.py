"""
AI360Trading — Global Content Calendar
Smart topic rotation covering ALL markets and ALL audiences worldwide.

Monday    = Options & Derivatives (universal — works for US, India, UK, Brazil)
Tuesday   = Technical Analysis (universal charts — any market)
Wednesday = Fundamental + Macro + Global Events
Thursday  = Strategies (intraday, swing, positional — universal)
Friday    = Psychology + Risk Management (universal)
"""

from datetime import datetime

# ══════════════════════════════════════════════════════════
# MONDAY — OPTIONS & DERIVATIVES (Global)
# ══════════════════════════════════════════════════════════
MONDAY_TOPICS = [
    {
        "title": "Options Trading Complete Beginner Guide",
        "category": "Options",
        "level": "Beginner",
        "target_audience": "US, India, UK, Brazil — universal",
        "slides": [
            {"heading": "What is an Option Contract?",
             "points": ["Right but not obligation to buy or sell","Call option = right to BUY","Put option = right to SELL","Premium = price you pay for this right","Works for stocks, indices, crypto — any market worldwide"]},
            {"heading": "How Call Options Make Money",
             "points": ["Buy call when you think price will rise","Example: Apple at 180, buy 185 call","If Apple rises to 200 — your call explodes in value","If Apple stays below 185 — you lose only the premium","Maximum loss is always just the premium paid"]},
            {"heading": "How Put Options Make Money",
             "points": ["Buy put when you think price will fall","Used to profit from crashes","Used to protect your stock portfolio","Example: S&P 500 drops 10% — your put 5x","Every big investor uses puts as insurance"]},
            {"heading": "Why Options Beat Stocks for Returns",
             "points": ["Control 100 shares for fraction of the cost","10% stock move can mean 100% option return","Risk is always capped at premium paid","Leverage without borrowing money","Why hedge funds and institutions love options"]},
            {"heading": "The 3 Rules Every Option Buyer Must Know",
             "points": ["Time is your enemy — options lose value daily","Buy options with at least 30 days to expiry","Always set a stop loss at 40% of premium","Exit winners at 50-100% profit — do not be greedy","Weekly options = highest risk, highest reward"]},
            {"heading": "Options in Different Markets",
             "points": ["US: SPY QQQ Apple Tesla options most liquid","India: Nifty Bank Nifty weekly options most popular","UK: FTSE options available on spread betting platforms","Brazil: Bovespa options very actively traded","Crypto: Bitcoin Ethereum options on Deribit and Bybit"]},
        ]
    },
    {
        "title": "Option Selling — How to Collect Premium Like a Bank",
        "category": "Options",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "Why Option Sellers Win Long Term",
             "points": ["80% of options expire worthless","Sellers collect that premium every expiry","Time decay works FOR sellers, AGAINST buyers","Like being the casino — house always wins over time","Warren Buffett sold options to buy Coca-Cola cheaper"]},
            {"heading": "Covered Call — Generate Monthly Income",
             "points": ["Own 100 shares of a stock you like","Sell a call option every month against those shares","Collect premium whether stock goes up, down, or sideways","Example: Own Apple, sell monthly call, collect 1-2% every month","This is how retirees in US generate income from stocks"]},
            {"heading": "Cash Secured Put — Buy Stocks at a Discount",
             "points": ["Pick a stock you want to own","Sell a put below current price and collect premium","If stock falls to your strike — you buy it at a discount","If stock stays up — keep the premium and repeat","Warren Buffett used this to buy Coca-Cola in the 1990s"]},
            {"heading": "Iron Condor — Profit When Market Does Nothing",
             "points": ["Sell both a call spread and a put spread","Profit when market stays in a range","Perfect for sideways markets and low volatility periods","Maximum profit if market closes between your short strikes","Used widely on SPX, Nifty, FTSE during consolidation"]},
            {"heading": "Risk Management for Option Sellers",
             "points": ["Always buy a further out option to cap your loss","Never sell naked options without a hedge","Exit when loss equals 2x the premium collected","Avoid holding through major news events","Position size: never risk more than 5% of account on one trade"]},
        ]
    },
    {
        "title": "Understanding Greeks — Delta Theta Vega Gamma",
        "category": "Options",
        "level": "Advanced",
        "target_audience": "Global",
        "slides": [
            {"heading": "Why Greeks Are the Secret Language of Options",
             "points": ["Greeks tell you exactly how your option will behave","Without Greeks you are flying blind","Professional traders think in Greeks not prices","Master these and you trade like an institution","Same Greeks apply to US, India, UK, crypto options"]},
            {"heading": "Delta — Your Directional Exposure",
             "points": ["Delta 0.5 means option moves 50 cents per $1 stock move","Deep ITM option delta approaches 1.0","Far OTM option delta approaches 0","Total portfolio delta tells you your net market exposure","Use delta to size positions correctly"]},
            {"heading": "Theta — Time is Money, Literally",
             "points": ["Theta is how much premium you lose per day","ATM weekly option loses 20-30% of value in last 3 days","Sellers love theta — they earn it every night","Buyers must be fast or theta destroys them","Why selling options before weekends is popular"]},
            {"heading": "Vega — Volatility Is Your Hidden Risk",
             "points": ["High VIX means expensive options — good to sell","Low VIX means cheap options — good to buy","Buy options before big events when VIX is low","Sell options after fear spike when VIX is elevated","This applies identically in US, India, and crypto markets"]},
        ]
    },
    {
        "title": "Weekly Options Expiry Strategy — Thursday Friday Plays",
        "category": "Options",
        "level": "Intermediate",
        "target_audience": "India + Global",
        "slides": [
            {"heading": "Weekly Options — The Fastest Money in Markets",
             "points": ["Weekly options expire every Thursday in India","Every Friday for US SPX and SPY","Theta decay is maximum in last 48 hours","Huge volatility on expiry day = big opportunities","Most traded financial instrument in the world by volume"]},
            {"heading": "Expiry Day Strategy for Option Buyers",
             "points": ["Buy ATM options only after clear direction is established","First 30 minutes — wait and watch, do not trade","Enter after 10 AM when direction is clear","Target 50-100% in hours — exit same day","Stop loss at 50% of premium — no exceptions"]},
            {"heading": "Expiry Day Strategy for Option Sellers",
             "points": ["Sell OTM options at open on expiry morning","Collect premium from rapid theta decay","Most profitable strategy statistically on expiry day","Exit by 2 PM — do not hold into last 30 minutes","Risk: sudden big move can wipe out sellers fast"]},
            {"heading": "Max Pain Theory on Expiry",
             "points": ["Max pain is the price where most option buyers lose money","Market gravitates toward max pain as expiry approaches","Check max pain every Thursday morning before trading","Available on NSE website for Nifty Bank Nifty","For US: available on optionstrat.com and unusualwhales.com"]},
        ]
    },
]

# ══════════════════════════════════════════════════════════
# TUESDAY — TECHNICAL ANALYSIS (Universal — any market)
# ══════════════════════════════════════════════════════════
TUESDAY_TOPICS = [
    {
        "title": "Candlestick Patterns — The Language of Price",
        "category": "Technical Analysis",
        "level": "Beginner",
        "target_audience": "Global",
        "slides": [
            {"heading": "Candlesticks Work in Every Market on Earth",
             "points": ["Invented in Japan 300 years ago for rice trading","Now used on stocks, crypto, forex, commodities","Same patterns on Nifty, S&P 500, Bitcoin, Gold","Learn once — trade any market anywhere in the world","Most powerful visual tool in all of trading"]},
            {"heading": "The Doji — Markets Most Honest Signal",
             "points": ["Open and close at almost the same price","The market is perfectly balanced between buyers and sellers","After a strong trend this means reversal is coming","Dragonfly doji after downtrend = powerful buy signal","Gravestone doji after uptrend = powerful sell signal"]},
            {"heading": "Engulfing Candles — Institutional Footprint",
             "points": ["The second candle completely swallows the first","Bullish engulfing: institutions stepped in and bought hard","Bearish engulfing: institutions distributed and sold hard","Works on all timeframes from 5-minute to weekly","Most reliable when it appears at key support or resistance"]},
            {"heading": "Hammer and Shooting Star",
             "points": ["Long wick shows the market rejected that price level violently","Hammer at bottom: sellers pushed down but buyers overwhelmed them","Shooting Star at top: buyers pushed up but sellers crushed them","The longer the wick the stronger the rejection","Works identically on Bitcoin, Apple, Nifty, Gold"]},
            {"heading": "How to Use Candlesticks Correctly",
             "points": ["Never trade a single candle in isolation","Always look at the trend before the candle","Confirmation from the next candle is essential","Combine with support and resistance for 80% accuracy","Volume should increase on reversal candles"]},
        ]
    },
    {
        "title": "Support and Resistance — The Foundation of All Trading",
        "category": "Technical Analysis",
        "level": "Beginner",
        "target_audience": "Global",
        "slides": [
            {"heading": "What Support and Resistance Really Means",
             "points": ["Support: price level where buyers are stronger than sellers","Resistance: price level where sellers are stronger than buyers","These levels exist because traders have memory","Same levels work on Apple, Bitcoin, EUR/USD, Gold, Nifty","The most universal concept in all of trading worldwide"]},
            {"heading": "How to Draw Support and Resistance",
             "points": ["Connect at least 2-3 price touches at the same level","More touches = stronger the level","Round numbers are always strong: 50000 Bitcoin, 20000 Nifty, 400 SPY","Use the body of candles not the wicks for cleaner levels","Weekly and monthly levels are strongest of all"]},
            {"heading": "Role Reversal — The Most Powerful Concept",
             "points": ["When price breaks above resistance it BECOMES support","When price breaks below support it BECOMES resistance","This is one of the most reliable setups in all markets","Example: Bitcoin 20000 was resistance for years, then became support","Trade the retest of the broken level for high-probability entries"]},
            {"heading": "How Institutions Use Support and Resistance",
             "points": ["Banks and hedge funds place huge orders at key levels","This is why the same levels hold again and again","They buy at support, sell at resistance, always","Retail traders who understand this trade WITH institutions","The levels on your chart represent real money, real orders"]},
            {"heading": "Trading Support and Resistance Step by Step",
             "points": ["Identify the key level on daily or weekly chart first","Wait for price to come back to that level","Watch for a reversal candlestick pattern at the level","Enter with tight stop just beyond the level","Target the next major support or resistance level"]},
        ]
    },
    {
        "title": "RSI — The Complete Masterclass",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "RSI Works the Same on Every Asset on Earth",
             "points": ["Relative Strength Index — measures momentum","Range 0 to 100, same on stocks, crypto, forex, commodities","Above 70 = overbought, below 30 = oversold","Created by J. Welles Wilder in 1978 — still the most used indicator","Same settings work on Bitcoin, S&P 500, Nifty, Gold, EUR/USD"]},
            {"heading": "RSI Divergence — The Signal Professionals Watch",
             "points": ["Price makes new high but RSI makes lower high = hidden weakness","Price makes new low but RSI makes higher low = hidden strength","This divergence predicted every major crash in history","Bitcoin 2021 top: price at 69000, RSI divergence was screaming sell","Nifty tops: RSI divergence visible weeks before crashes"]},
            {"heading": "RSI in Bull and Bear Markets",
             "points": ["In a bull market RSI rarely goes below 40","In a bear market RSI rarely goes above 60","RSI below 40 in a bull market = golden buy opportunity","RSI above 60 in a bear market = golden sell opportunity","First step: identify the trend, then use RSI correctly"]},
            {"heading": "RSI Hidden Divergence — Trend Continuation",
             "points": ["Price makes higher low but RSI makes lower low = buy signal in uptrend","Price makes lower high but RSI makes higher high = sell signal in downtrend","Used by professional traders to add to winning positions","Much more reliable than regular divergence in trending markets","Works beautifully on crypto which has strong sustained trends"]},
        ]
    },
    {
        "title": "MACD — How to Read Market Momentum",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "What MACD is Really Telling You",
             "points": ["Moving Average Convergence Divergence","Measures the relationship between two moving averages","MACD line above signal line = bullish momentum","MACD line below signal line = bearish momentum","Same indicator, same settings — works on all global markets"]},
            {"heading": "MACD Histogram — The Real Secret",
             "points": ["Bars above zero line = buyers in control","Bars below zero line = sellers in control","Histogram shrinking while above zero = momentum weakening","Histogram expanding above zero = momentum strengthening","This is how you see institutional momentum shifts early"]},
            {"heading": "MACD Zero Line Crossover",
             "points": ["MACD crossing above zero = major bullish shift","MACD crossing below zero = major bearish shift","Strongest signal MACD gives on any market","Works best on daily and weekly charts","Used widely on S&P 500, Bitcoin, Nifty, Crude Oil"]},
            {"heading": "Combining MACD with Other Indicators",
             "points": ["MACD crossover + RSI above 50 = strongest buy signal","MACD crossover + price above 200 EMA = confirmed uptrend","MACD + volume surge = institutional accumulation","MACD divergence + resistance level = high probability short","This combination works on any stock in any country"]},
        ]
    },
    {
        "title": "Chart Patterns — Head Shoulders Triangle Flag",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "Why Chart Patterns Work in Every Market",
             "points": ["Patterns form because human psychology never changes","Fear and greed look the same in India, USA, Brazil, UK","Same patterns on Apple, Tata Motors, Bitcoin, Gold","Learned once — applied everywhere for your entire career","The most timeless skill in all of financial trading"]},
            {"heading": "Head and Shoulders — Most Reliable Reversal",
             "points": ["Three peaks: left shoulder, head (highest), right shoulder","Neckline connects the two lows between the peaks","Break below neckline = strong sell signal with a specific target","Target = height of head projected down from neckline","Appeared before the 2008 crash, 2021 Bitcoin top, many more"]},
            {"heading": "Bull Flag — The Momentum Trader Favourite",
             "points": ["Strong vertical move up (the flagpole)","Then tight sideways or slightly downward consolidation (the flag)","Breakout above flag = continuation of the original move","Target = flagpole height added to breakout point","One of highest win-rate patterns in trending markets"]},
            {"heading": "Ascending Triangle — Institutional Accumulation",
             "points": ["Flat top resistance with rising lows","Institutions buying quietly, pushing lows higher each time","They have a target and they keep buying every dip","Breakout above flat top = explosive move begins","Seen on Bitcoin before every major bull run, and on growth stocks"]},
            {"heading": "How to Trade Patterns Correctly",
             "points": ["Never buy the pattern — wait for the breakout","Breakout must be accompanied by above average volume","Place stop loss just below the breakout level","Target is the measured move from the pattern","If breakout fails and price comes back inside — exit immediately"]},
        ]
    },
]

# ══════════════════════════════════════════════════════════
# WEDNESDAY — GLOBAL MACRO + FUNDAMENTALS + EVENTS
# ══════════════════════════════════════════════════════════
WEDNESDAY_TOPICS = [
    {
        "title": "How US Federal Reserve Moves Every Market on Earth",
        "category": "Global Macro",
        "level": "Beginner",
        "target_audience": "US, India, Brazil, UK — everyone",
        "slides": [
            {"heading": "Why the Fed Controls All Global Markets",
             "points": ["US Federal Reserve sets interest rates for the world's reserve currency","When Fed raises rates: global money flows back to USA","Stocks fall, emerging markets crash, dollar strengthens","When Fed cuts rates: money floods into stocks and emerging markets","India, Brazil, UK — all affected immediately by Fed decisions"]},
            {"heading": "How Fed Decisions Affect Indian Markets",
             "points": ["Fed rate hike: FII pull money out of India and return to US","Nifty often falls 2-5% within days of Fed hike","Rupee weakens: USDINR rises, imports become expensive","IT stocks benefit: they earn in USD","Every Indian investor must watch Fed calendar, not just RBI"]},
            {"heading": "How to Trade Fed Announcement Days",
             "points": ["Fed announces 8 times per year — mark all dates now","Markets are highly volatile 30 minutes before and after","Professional strategy: sell options 2 days before (collect VIX premium)","After announcement: trade the direction of the initial reaction","Second move after 30 minutes is often more reliable than first"]},
            {"heading": "Fed Dot Plot — What It Really Means",
             "points": ["Dot plot shows where Fed members expect rates to go","More dots at higher levels = hawkish = bad for stocks","More dots at lower levels = dovish = good for stocks","Stocks often move more on dot plot than on actual rate decision","Released 4 times per year — more important than the rate decision itself"]},
            {"heading": "Central Banks Around the World",
             "points": ["RBI: India — watch every 6 weeks","ECB: Europe — affects EUR/USD and European stocks","Bank of England: UK — affects GBP and FTSE","Bank of Japan: huge impact on global markets through Yen carry trade","All follow the Fed — Fed moves first, everyone else follows within months"]},
        ]
    },
    {
        "title": "Bitcoin and Crypto — Technical Analysis Guide",
        "category": "Crypto",
        "level": "Beginner",
        "target_audience": "Global — huge Brazil, US, India audience",
        "slides": [
            {"heading": "Why Crypto is the Best Market for Technical Analysis",
             "points": ["Crypto trades 24/7 — no gaps, pure price action","Retail dominated — patterns work extremely well","No earnings reports to blindside you","Same support resistance RSI MACD work perfectly","Highest volatility = highest potential returns for traders"]},
            {"heading": "Bitcoin Halving Cycle — The Most Predictable Pattern",
             "points": ["Bitcoin supply cuts in half every 4 years — called the halving","After every halving Bitcoin has made all-time highs within 12-18 months","2012 halving: Bitcoin went from 12 to 1000 dollars","2016 halving: Bitcoin went from 650 to 20000 dollars","2020 halving: Bitcoin went from 9000 to 69000 dollars"]},
            {"heading": "Key Bitcoin Levels Every Trader Watches",
             "points": ["200 week moving average: most important support in all of crypto","Previous all time high always becomes support after being broken","Round numbers: 50000, 100000, 200000 are massive psychological levels","4 year cycle low: historically the best time to buy Bitcoin","On-chain data confirms these technical levels every single cycle"]},
            {"heading": "How to Apply Technical Analysis to Crypto",
             "points": ["Use daily and weekly charts for trend direction","Use 4-hour chart for entry timing","RSI below 30 on weekly chart = generational buy opportunity","RSI above 80 on weekly chart = take significant profits","Bitcoin dominance chart tells you when altcoins will outperform"]},
            {"heading": "Crypto Risk Management — Critical Rules",
             "points": ["Never invest more than you can afford to lose completely","Crypto can fall 80-90% in bear markets — this is normal","Dollar cost averaging beats trying to time the market","Cold wallet storage for anything you hold long term","Do not trade crypto with leverage unless you are very experienced"]},
        ]
    },
    {
        "title": "How to Read Economic Data — Jobs CPI GDP",
        "category": "Global Macro",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "The Economic Calendar — Your Most Important Tool",
             "points": ["Economic data moves markets more than any chart pattern","Three reports move US markets most: NFP, CPI, GDP","NFP: Non-Farm Payrolls — released first Friday every month","CPI: Consumer Price Index — inflation data, moves everything","GDP: economic growth data — quarterly, big picture signal"]},
            {"heading": "Non-Farm Payrolls — The Most Watched Number on Earth",
             "points": ["Released every first Friday of the month at 8:30 AM US Eastern","Strong jobs report: economy healthy, Fed may raise rates, stocks mixed","Weak jobs report: Fed may cut rates, stocks often rally","Gold and bonds move opposite to stocks on this data","Indian markets react indirectly through FII flow changes"]},
            {"heading": "CPI — Inflation Data That Controls Fed Policy",
             "points": ["CPI above expectations: inflation hot, Fed stays hawkish, stocks fall","CPI below expectations: inflation cooling, Fed turns dovish, stocks rally","Core CPI excludes food and energy — Fed focuses on core","This single number has caused 3-5% market moves in recent years","Watch this more than any technical indicator on release day"]},
            {"heading": "How India's Economic Data Moves Markets",
             "points": ["India GDP growth rate: 7%+ is bullish for Nifty long term","India CPI: RBI targets 4%, above 6% means rate hikes coming","India PMI Manufacturing: above 50 = expansion, bullish","Current Account Deficit: high CAD weakens rupee","Foreign Exchange Reserves: RBI uses to stabilise rupee — watch monthly"]},
        ]
    },
    {
        "title": "Gold and Oil — How Commodities Affect Your Stocks",
        "category": "Commodities",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "Why Every Stock Trader Must Watch Gold and Oil",
             "points": ["Commodities signal inflation before it shows in economic data","Rising oil = higher inflation = Fed hawks = stock market pressure","Rising gold = fear in markets = risk-off = stocks often fall","Falling oil = good for India — we import 80% of our oil","These relationships have worked for 50+ years across all countries"]},
            {"heading": "Gold — The Fear Gauge of Global Markets",
             "points": ["Gold rises when investors fear: war, recession, banking crisis","Gold falls when confidence returns and risk appetite is high","Key levels: 2000, 2500, 3000 USD per ounce are psychological","Gold in rupees: USDINR × gold USD price — affects Indian buyers","Central banks are buying gold at record pace — very bullish signal"]},
            {"heading": "Crude Oil — The Lifeblood of the Global Economy",
             "points": ["Brent crude affects petrol prices in every country","High oil = higher inflation globally = central banks raise rates","India imports 85% of oil: high oil = higher CAD = weaker rupee","Oil company stocks (ONGC, Reliance, Saudi Aramco) benefit from high oil","OPEC decisions on production cuts move oil price immediately"]},
            {"heading": "How to Trade Commodity Correlations",
             "points": ["Oil rises: buy oil companies, sell airlines and paint companies","Gold rises: buy gold ETFs, gold mining stocks","Copper rises: strong global economic growth signal — buy industrial stocks","Falling commodities: buy consumer companies whose costs are falling","These sector rotation plays work the same in India, USA, and UK"]},
        ]
    },
]

# ══════════════════════════════════════════════════════════
# THURSDAY — STRATEGIES (Universal)
# ══════════════════════════════════════════════════════════
THURSDAY_TOPICS = [
    {
        "title": "Price Action Trading — No Indicators Needed",
        "category": "Trading Strategy",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "What is Price Action Trading?",
             "points": ["Trade using only raw price movement — no indicators","Candlestick patterns, support resistance, trend lines","Used by most professional traders worldwide","Works on stocks, forex, crypto, commodities, indices","Cleaner charts mean cleaner thinking and better decisions"]},
            {"heading": "The Pin Bar — Most Powerful Price Action Signal",
             "points": ["Long wick with small body = strong rejection","Pin bar at support = institutional buying signal","Pin bar at resistance = institutional selling signal","The longer the wick relative to body the stronger the signal","Works on 5-minute charts for day traders and weekly charts for investors"]},
            {"heading": "Inside Bar — Coiled Spring Setup",
             "points": ["Entire second candle fits inside the first candle","Market consolidating, about to make a big move","Break above inside bar high = buy","Break below inside bar low = sell","Tightest stop loss of any price action setup"]},
            {"heading": "Trend Line Trading",
             "points": ["Draw trend line connecting swing lows in uptrend","Third touch of trend line = highest probability entry","Break of trend line = trend is changing — reduce long positions","Trend lines become stronger with every successful touch","Same trend lines visible on Bitcoin, S&P 500, Nifty, Gold"]},
            {"heading": "How to Build a Price Action System",
             "points": ["Identify trend on weekly chart first","Find key levels of support and resistance","Wait for price to reach those levels","Look for a rejection candle — pin bar or engulfing","Enter on next candle open with tight stop — simple and powerful"]},
        ]
    },
    {
        "title": "Swing Trading — The Perfect Strategy for Working People",
        "category": "Trading Strategy",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "Why Swing Trading Beats Intraday for Most People",
             "points": ["Hold trades for 2 to 10 days — check once per day","No need to stare at screen all day","Works while you have a full-time job","Better risk to reward ratios than intraday","Used successfully on US stocks, Indian stocks, crypto, forex"]},
            {"heading": "The Perfect Swing Trade Setup",
             "points": ["Stock in strong uptrend: above 20, 50, and 200 EMA","Price pulls back to 20 EMA — this is the entry zone","RSI pulls back to 40-50 during the pullback","Volume decreasing on pullback — sellers not aggressive","Enter when first green candle appears at the 20 EMA"]},
            {"heading": "Finding the Best Stocks to Swing Trade",
             "points": ["Screen for stocks making 52-week highs — these have momentum","Look for high relative strength vs the index","Avoid stocks below their 200 EMA — only trade the trend","In US: use Finviz.com screener for this","In India: use Screener.in or TradingView screener"]},
            {"heading": "Swing Trading Crypto",
             "points": ["Crypto perfect for swing trading — moves 10-30% in days","Apply exact same setup: pullback to 20 EMA in uptrend","Bitcoin and Ethereum most liquid — tightest spreads","Altcoins: higher reward but higher risk — smaller position size","Set alerts so you don't need to watch 24/7"]},
            {"heading": "Exit Strategy That Maximises Profits",
             "points": ["Sell half at first target — usually 5-8% profit","Move stop to breakeven on remaining position","Trail stop below each new swing low as price rises","If stock gaps up strongly — sell entire position into strength","Never let a good profit turn into a loss — always move stops up"]},
        ]
    },
    {
        "title": "How to Build a Complete Trading System",
        "category": "Trading Strategy",
        "level": "All Levels",
        "target_audience": "Global",
        "slides": [
            {"heading": "Why Most Traders Fail — The Real Reason",
             "points": ["Not lack of a strategy — lack of a COMPLETE system","A system has: entry rules, exit rules, position sizing, risk rules","Without all four, emotion takes over every trade","Professional traders follow systems even when it feels wrong","Your system is your edge — protect it and follow it always"]},
            {"heading": "Step 1 — Define Your Market and Timeframe",
             "points": ["Pick ONE market to master first: Nifty, S&P 500, or Bitcoin","Pick ONE primary timeframe: daily chart is best for beginners","Use one higher timeframe (weekly) for trend direction","Use one lower timeframe (4 hour) for entry timing","Do not jump between markets — depth beats breadth always"]},
            {"heading": "Step 2 — Your Entry Rules",
             "points": ["Write down exactly what conditions must be true to enter","Example: Price above 200 EMA AND RSI above 50 AND bullish engulfing candle","If all three not present — no trade, period","Having rules removes 90% of emotional trading mistakes","Test your rules on at least 50 historical setups before trading live"]},
            {"heading": "Step 3 — Position Sizing Formula",
             "points": ["Risk per trade = 1% of your total account","Account is 10 lakh rupees or 10000 USD: max risk per trade = 10000 Rs or 100 USD","Calculate shares from your stop loss distance","This formula keeps you alive through any losing streak","Consistent position sizing is more important than your entry strategy"]},
            {"heading": "Step 4 — Review and Improve Weekly",
             "points": ["Every Sunday review all trades of the past week","Calculate win rate and average risk to reward","Identify which setups are working and which are not","Remove or adjust rules that consistently lose","This weekly review process is how good traders become great traders"]},
        ]
    },
    {
        "title": "Fibonacci Retracement — How Professionals Find Entries",
        "category": "Trading Strategy",
        "level": "Intermediate",
        "target_audience": "Global",
        "slides": [
            {"heading": "Why Fibonacci Works on Every Market on Earth",
             "points": ["Based on the golden ratio found throughout nature","Used by millions of traders worldwide simultaneously","Self-fulfilling prophecy — works because everyone watches the same levels","61.8% retracement is the golden zone in any market","Same levels work on Apple, Bitcoin, EUR/USD, Gold, Nifty"]},
            {"heading": "How to Draw Fibonacci Correctly",
             "points": ["In uptrend: drag from the significant swing low to swing high","In downtrend: drag from swing high to swing low","The tool automatically draws 38.2%, 50%, 61.8% levels","Most important levels: 38.2% for strong trends, 61.8% for normal trends","Use the wick extremes — not candle bodies — for accuracy"]},
            {"heading": "The Golden Zone — 61.8% Strategy",
             "points": ["Price retraces to 61.8% after a strong move","RSI reaches 40-50 at the same time = confluence","This confluence gives you a very high probability entry","Stop loss just below 78.6% level — minimal risk","Target: return to the previous high = typically 2:1 to 4:1 reward"]},
            {"heading": "Fibonacci Extensions — Finding Profit Targets",
             "points": ["After a breakout, where will price go next?","161.8% extension is the most common first target","261.8% extension is the target for strong trending markets","Draw from swing low to swing high to retracement low","This gives you a mathematical price target in any market"]},
        ]
    },
]

# ══════════════════════════════════════════════════════════
# FRIDAY — PSYCHOLOGY + RISK (Universal)
# ══════════════════════════════════════════════════════════
FRIDAY_TOPICS = [
    {
        "title": "Trading Psychology — Why Smart People Lose Money",
        "category": "Psychology",
        "level": "All Levels",
        "target_audience": "Global",
        "slides": [
            {"heading": "The Dirty Secret of the Trading Industry",
             "points": ["90% of traders lose money — this is a documented fact worldwide","The problem is never the strategy — it is always psychology","A perfect strategy fails if you cannot follow it under pressure","The same psychological traps destroy traders in India, USA, UK, Brazil","Understanding your enemy is the first step to defeating it"]},
            {"heading": "Loss Aversion — Why Losses Hurt More Than Gains Feel Good",
             "points": ["Losing 1000 rupees feels twice as bad as gaining 1000 feels good","This is hardwired into human DNA for survival","In trading this makes you hold losers too long hoping to break even","And cut winners too early to lock in the 'safe' profit","This single bias is responsible for most trading losses worldwide"]},
            {"heading": "The Revenge Trade — Account Killer",
             "points": ["You take a loss. Now you feel angry and need to recover it immediately","You trade bigger — sometimes 3x or 5x your normal size","You lose again — now the account is seriously damaged","This sequence destroys accounts in hours across all countries","Rule: after any loss exceeding your daily limit — turn off your screen and walk away"]},
            {"heading": "Overconfidence — The Bull Market Trap",
             "points": ["After 5 consecutive wins traders feel invincible","They increase position size to 3x or 5x their normal size","The inevitable losing trade wipes out all previous profits","Bull markets make everyone look like a genius","Keep position size consistent regardless of recent wins or losses"]},
            {"heading": "Building Unbreakable Mental Discipline",
             "points": ["Write your trading rules in a physical notebook — not just on screen","Read them before every trading session — make it a ritual","Accept that every loss is simply the cost of doing business","Professional traders aim for consistency — not big wins","Your goal is to be in the game for 10 years — one trade never matters"]},
        ]
    },
    {
        "title": "Risk Management — The Only Thing That Guarantees Survival",
        "category": "Risk Management",
        "level": "All Levels",
        "target_audience": "Global",
        "slides": [
            {"heading": "The Mathematics of Ruin — Why Small Losses Compound",
             "points": ["Lose 10%: need 11% to recover","Lose 25%: need 33% to recover","Lose 50%: need 100% to recover","Lose 75%: need 300% to recover","This is why protecting capital is more important than making money"]},
            {"heading": "The 1% Rule — Professional Risk Management",
             "points": ["Never risk more than 1-2% of your account on any single trade","With 1 lakh rupees: max risk per trade is 1000-2000 rupees","With 10000 USD: max risk per trade is 100-200 USD","This means you can have 50 consecutive losing trades before account is gone","No strategy has a 50-trade losing streak — this gives you complete safety"]},
            {"heading": "Stop Loss — Your Insurance Policy",
             "points": ["Every trade needs a stop loss placed in the system before entry","A stop loss in your head does not exist — the market will find your weakness","Move stop to breakeven once profit equals your risk","Trailing stop lock in profits as price moves in your favour","Traders who remove stop losses eventually blow up — no exceptions"]},
            {"heading": "Portfolio Risk — Not Just Per Trade",
             "points": ["Maximum 20-25% of portfolio in any single stock","Maximum 10-15% in any single sector","Keep 20-30% in cash at all times for opportunities","If total portfolio is down 10% — reduce all positions by 50%","Diversification across markets: stocks, gold, a little crypto is smart"]},
            {"heading": "Your Personal Risk Management Plan",
             "points": ["Daily loss limit: stop trading when down 3% in one day","Weekly loss limit: review strategy when down 6% in one week","Monthly loss limit: take a break when down 10% in one month","These limits prevent small losses becoming catastrophic ones","Write this plan now — before your next trade, not after your next loss"]},
        ]
    },
    {
        "title": "How to Invest for Long Term Wealth — SIP Index Fund Strategy",
        "category": "Personal Finance",
        "level": "Beginner",
        "target_audience": "Global — huge audience",
        "slides": [
            {"heading": "The Simplest Path to Wealth That Works in Any Country",
             "points": ["Invest a fixed amount every month into an index fund","Do not try to time the market — just keep buying","This strategy has made millions of ordinary people wealthy","Warren Buffett recommends this for everyone who is not a professional","Works whether you are in India, USA, UK, Brazil, or anywhere"]},
            {"heading": "Why Index Funds Beat 80% of Professional Fund Managers",
             "points": ["S&P 500 index fund: average 10-12% per year for 100 years","Nifty 50 index fund: average 12-14% per year over 20 years","80% of actively managed funds underperform the index over 10 years","Index fund fees: 0.1% per year vs active funds 1-2% per year","This fee difference alone costs you 20-30% of your wealth over 30 years"]},
            {"heading": "The Magic of Compound Interest — Numbers That Will Shock You",
             "points": ["5000 rupees per month from age 25 to 60 at 12% = 3.2 crore rupees","Same from age 35: only 90 lakhs — the 10 year delay costs 2.4 crore","200 USD per month from age 25 in S&P 500 index = over 1 million USD by retirement","Starting 10 years late reduces your final wealth by 70%","Time in the market beats timing the market — always"]},
            {"heading": "Dollar Cost Averaging — Why Market Crashes Are Your Friend",
             "points": ["When market falls 20%: your monthly investment buys more shares","When market recovers: all those extra shares are now worth much more","This is why you must NEVER stop your SIP during a crash","2020 COVID crash: people who kept their SIP running made the most money","Every crash in history has been followed by new all-time highs"]},
            {"heading": "Getting Started Today — The Action Plan",
             "points": ["India: open Zerodha or Groww, start Nifty 50 index fund SIP with as little as 500 rupees","USA: open Vanguard or Fidelity, invest in VOO or SPY — zero fees","UK: open Vanguard UK, invest in FTSE All-World index","Brazil: invest in BOVA11 ETF which tracks Ibovespa index","Start today with whatever amount you have — the amount matters far less than starting"]},
        ]
    },
    {
        "title": "How to Read a Stock — Fundamental Analysis for Everyone",
        "category": "Fundamental Analysis",
        "level": "Beginner",
        "target_audience": "Global",
        "slides": [
            {"heading": "What Makes a Stock Worth Owning Long Term",
             "points": ["A business that grows revenue and profits every year","Low or no debt — financial strength to survive downturns","High return on equity — management uses money efficiently","Strong brand or competitive moat — hard for competitors to copy","Consistent dividend growth for income investors"]},
            {"heading": "The P/E Ratio — Most Used Valuation Metric",
             "points": ["Price per share divided by earnings per share","P/E of 20 means paying 20 years of earnings upfront","Compare P/E to industry average — not to the entire market","Growth stocks command high P/E: Apple 30, Reliance 25, Infosys 24","Value stocks have low P/E: banks, energy companies often below 15"]},
            {"heading": "Revenue and Profit Growth — The Most Important Numbers",
             "points": ["Revenue growing 15%+ per year = fast growing company","Net profit growing faster than revenue = improving margins","Check 5 years of data — one good year means nothing","Consistent growth beats spectacular but inconsistent growth","This works whether you are analysing Apple, TCS, or a Brazilian bank"]},
            {"heading": "Finding Great Stocks Using Free Tools",
             "points": ["Screener.in: best free tool for Indian stock analysis","Finviz.com: best free screener for US stocks","Simply Wall St: visual fundamental analysis for global stocks","Set filters: ROE above 15%, debt below 0.5, revenue growth above 15%","This takes 10 minutes per week and beats most paid research"]},
        ]
    },
]

# ══════════════════════════════════════════════════════════
# MASTER MAPPING
# ══════════════════════════════════════════════════════════
WEEKDAY_TOPICS = {
    0: MONDAY_TOPICS,
    1: TUESDAY_TOPICS,
    2: WEDNESDAY_TOPICS,
    3: THURSDAY_TOPICS,
    4: FRIDAY_TOPICS,
}

def get_todays_education_topic():
    """Smart rotation — returns today's education topic."""
    now = datetime.now()
    weekday = now.weekday()
    if weekday >= 5:
        weekday = 0
    topics = WEEKDAY_TOPICS[weekday]
    week_num = now.isocalendar()[1]
    return topics[week_num % len(topics)]


if __name__ == "__main__":
    topic = get_todays_education_topic()
    print(f"Today: {topic['title']}")
    print(f"Category: {topic['category']} | Level: {topic['level']}")
    print(f"Target: {topic['target_audience']}")
    print(f"Slides: {len(topic['slides'])}")
