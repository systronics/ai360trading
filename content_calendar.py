"""
AI360Trading — Content Calendar v2.2
======================================
v2.2 CHANGES (May 2026):
- Added get_article_seo_seeds() — fixes "[WARN] content_calendar.py not found"
  generate_articles.py imports this function — was missing in v2.1
- Added no_price_numbers rule to weekend/holiday seeds
  Fixes AI hallucinating fake S&P 500 percentages like "2.1%" in titles
  Weekend mode = evergreen titles only (no live price data)
- get_todays_topic() and get_todays_education_topic() preserved exactly

Author: AI360Trading Automation
Last Updated: May 2026
"""

from datetime import date, datetime

# ── Course start date — NEVER change this ─────────────────────────────────────
COURSE_START = date(2026, 5, 15)


# ══════════════════════════════════════════════════════════════════════
# get_article_seo_seeds() — NEW v2.2
# Called by generate_articles.py to get SEO seed keywords
# Fixes: [WARN] content_calendar.py not found — SEO seeds skipped
# ══════════════════════════════════════════════════════════════════════

def get_article_seo_seeds(mode: str = "market") -> dict:
    """
    Returns SEO seed keywords for article generation.
    Called by generate_articles.py at the start of each run.

    v2.2 FIX:
    - Weekend/holiday seeds have no_price_numbers=True
      This prevents AI from hallucinating fake price data like
      "2.1% Weekly S&P 500" or "Bitcoin at 78,000" in article titles
    - Market seeds allow price references (real data fetched separately)

    Returns dict with:
      global_seeds: list of evergreen SEO phrases
      india_seeds: India-specific keywords
      usa_seeds: USA-specific keywords
      uk_seeds: UK-specific keywords
      no_price_numbers: bool — if True, AI must NOT use specific price numbers
      title_style: instruction for AI title generation
    """
    day = datetime.now().weekday()  # 0=Mon, 6=Sun

    if mode in ("weekend", "holiday"):
        return {
            "global_seeds": [
                "how to invest for beginners 2026",
                "stock market basics explained simply",
                "best investment for beginners India USA UK",
                "how to save money and invest in 2026",
                "index fund vs mutual fund comparison",
                "compound interest explained with examples",
                "how to build wealth from zero salary",
                "term insurance vs whole life insurance",
                "emergency fund how much do you need",
                "passive income ideas that actually work",
            ],
            "india_seeds": [
                "how to invest in share market India beginner",
                "SIP vs lump sum investment India",
                "best mutual funds India 2026",
                "Nifty 50 beginner guide India",
                "PPF vs ELSS tax saving India",
                "term insurance India comparison 2026",
                "demat account how to open India",
            ],
            "usa_seeds": [
                "how to invest in stocks USA beginner 2026",
                "best index fund USA Vanguard Fidelity",
                "401k vs Roth IRA comparison",
                "S&P 500 investing guide beginners",
                "term life insurance USA comparison",
            ],
            "uk_seeds": [
                "how to invest UK beginner 2026",
                "best ISA account UK 2026",
                "FTSE 100 investing guide",
                "term life insurance UK comparison",
            ],
            "no_price_numbers": True,
            "title_style": (
                "Evergreen educational title only. "
                "Do NOT include any specific price numbers, percentages, or market levels. "
                "Do NOT write: '2.1% Weekly S&P 500' or 'Bitcoin at 78,000' or 'Nifty falls 0.14%'. "
                "These are weekend articles — market is closed, live prices are not available. "
                "Write titles like: 'How to Invest in Index Funds — Complete 2026 Guide' "
                "or 'Stock Market Basics Every Beginner Must Know'. "
                "Timeless educational titles only."
            ),
        }

    # Market mode (Mon-Fri) — day-specific seeds
    day_seeds = {
        0: {  # Monday — Options
            "global_seeds": [
                "options trading for beginners 2026",
                "how to buy call options explained",
                "Nifty options strategy weekly expiry",
                "option selling vs option buying which is better",
                "how to earn monthly income from options India",
            ],
            "topic": "Options and Derivatives",
        },
        1: {  # Tuesday — Technical Analysis
            "global_seeds": [
                "how to read stock charts for beginners",
                "RSI indicator explained simply",
                "moving average EMA crossover strategy",
                "candlestick patterns that work India",
                "support and resistance levels how to draw",
            ],
            "topic": "Technical Analysis",
        },
        2: {  # Wednesday — Fundamental + Macro
            "global_seeds": [
                "how to analyse a stock fundamental analysis",
                "PE ratio explained for beginners",
                "FII DII data how to use for trading India",
                "how to read annual report stock",
                "which sectors to invest in India 2026",
            ],
            "topic": "Fundamental Analysis and Global Markets",
        },
        3: {  # Thursday — Strategies + Personal Finance
            "global_seeds": [
                "swing trading strategy India 2026",
                "how to do positional trading stocks",
                "best personal finance habits wealth building",
                "LIC vs term insurance which is better",
                "how much life insurance do I need",
            ],
            "topic": "Trading Strategies and Personal Finance",
        },
        4: {  # Friday — Psychology + Risk
            "global_seeds": [
                "trading psychology tips for beginners",
                "how to control emotions in trading",
                "risk management trading position sizing",
                "why most traders lose money India",
                "how to stop revenge trading",
            ],
            "topic": "Trading Psychology and Risk Management",
        },
    }

    seeds = day_seeds.get(day, day_seeds[0])

    return {
        "global_seeds":    seeds["global_seeds"],
        "india_seeds":     seeds.get("india_seeds", []),
        "usa_seeds":       seeds.get("usa_seeds", []),
        "uk_seeds":        seeds.get("uk_seeds", []),
        "no_price_numbers": False,
        "title_style": (
            f"SEO-optimised article title about {seeds['topic']}. "
            "Include a specific angle, audience, or data point. "
            "Avoid generic titles. Target India, USA, UK readers."
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# 52-WEEK EDUCATION COURSE — Progressive Curriculum
# ══════════════════════════════════════════════════════════════════════

EDUCATION_COURSE = [
    {"week":1,"title":"Stock Market Kya Hai","title_en":"What Is the Stock Market","category":"Foundations","level":"Beginner","description":"Basics: Shares, NSE, BSE explained simply","slides":[{"heading":"Stock Market Kya Hota Hai"},{"heading":"Share Kya Hai — Ownership Ka Concept"},{"heading":"NSE Aur BSE Mein Kya Fark Hai"},{"heading":"SEBI — Market Ka Police Officer"},{"heading":"Market Mein Paisa Kaise Lagta Hai"}]},
    {"week":2,"title":"Demat Account Kaise Kholein","title_en":"How to Open a Demat Account","category":"Foundations","level":"Beginner","description":"Zerodha, Dhan, Groww — which broker to choose","slides":[{"heading":"Demat Account Kya Hota Hai"},{"heading":"Broker Kaise Chunein"},{"heading":"Account Kholne Ka Poora Process"},{"heading":"KYC Kya Hai Aur Kaise Karein"},{"heading":"Pehla Share Kaise Khareedein"}]},
    {"week":3,"title":"Nifty 50 Aur Sensex Samjhein","title_en":"Understanding Nifty 50 and Sensex","category":"Foundations","level":"Beginner","description":"What market indices are and why they matter","slides":[{"heading":"Index Kya Hota Hai"},{"heading":"Nifty 50 Mein Kaunse Stocks Hain"},{"heading":"Sensex — BSE Ka Index"},{"heading":"Index Upar Jaaye Toh Portfolio Bhi"},{"heading":"Global Indices — Dow Jones Nasdaq"}]},
    {"week":4,"title":"IPO Mein Invest Karein Ya Nahi","title_en":"Should You Invest in IPOs","category":"Foundations","level":"Beginner","description":"IPO basics, allotment process, GMP","slides":[{"heading":"IPO Kya Hota Hai"},{"heading":"Company IPO Kyon Laati Hai"},{"heading":"IPO Apply Kaise Karein"},{"heading":"GMP Kya Hai"},{"heading":"IPO Mein Kitna Risk Hai"}]},
    {"week":5,"title":"Dividend — Stocks Se Passive Income","title_en":"Dividends — Passive Income From Stocks","category":"Foundations","level":"Beginner","description":"Dividend basics, yield, ex-dividend date","slides":[{"heading":"Dividend Kya Hota Hai"},{"heading":"Dividend Yield Kaise Calculate Karein"},{"heading":"Ex-Dividend Date"},{"heading":"Top Dividend Stocks India 2026"},{"heading":"Dividend Reinvestment — Compounding"}]},
    {"week":6,"title":"Large Cap vs Mid Cap vs Small Cap","title_en":"Large Cap vs Mid Cap vs Small Cap","category":"Foundations","level":"Beginner","description":"Understanding market capitalisation","slides":[{"heading":"Market Cap Kya Hota Hai"},{"heading":"Large Cap — Stability"},{"heading":"Mid Cap — Balance"},{"heading":"Small Cap — High Risk High Reward"},{"heading":"Portfolio Mein Kitna Kitna Rakhein"}]},
    {"week":7,"title":"Mutual Funds vs Direct Stocks","title_en":"Mutual Funds vs Direct Stock Investing","category":"Foundations","level":"Beginner","description":"Complete comparison for beginners","slides":[{"heading":"Mutual Fund Kaise Kaam Karta Hai"},{"heading":"Direct Stock Investment"},{"heading":"Expense Ratio"},{"heading":"Kab Mutual Fund Better Hai"},{"heading":"Index Fund — Sabse Simple"}]},
    {"week":8,"title":"SIP — Systematic Investment Plan Ka Jaadu","title_en":"SIP — The Magic of Systematic Investment","category":"Foundations","level":"Beginner","description":"How SIP works, rupee cost averaging","slides":[{"heading":"SIP Kya Hai"},{"heading":"Rupee Cost Averaging"},{"heading":"Compounding Ka Jaadu"},{"heading":"SIP Calculator"},{"heading":"Common SIP Mistakes"}]},
    {"week":9,"title":"Chart Padhna Seekhein","title_en":"How to Read Stock Charts","category":"Technical Analysis","level":"Beginner","description":"Line, bar, candlestick charts explained","slides":[{"heading":"Chart Kyon Zaroori Hai"},{"heading":"Line vs Bar vs Candlestick"},{"heading":"Time Frame — Daily Weekly Monthly"},{"heading":"Volume — Price Ka Confirmation"},{"heading":"TradingView Par Chart Kaise Dekhein"}]},
    {"week":10,"title":"Candlestick Patterns — 5 Jo Kaam Aate Hain","title_en":"Candlestick Patterns That Actually Work","category":"Technical Analysis","level":"Beginner","description":"Most reliable candlestick patterns","slides":[{"heading":"Candlestick Kya Batata Hai"},{"heading":"Bullish Engulfing"},{"heading":"Pin Bar"},{"heading":"Doji"},{"heading":"Inside Bar"}]},
    {"week":11,"title":"Support and Resistance","title_en":"Support and Resistance Levels","category":"Technical Analysis","level":"Beginner","description":"How to identify and draw correct levels","slides":[{"heading":"Support Kya Hai"},{"heading":"Resistance Kya Hai"},{"heading":"Levels Correctly Kaise Draw Karein"},{"heading":"Role Reversal"},{"heading":"Breakout Entry"}]},
    {"week":12,"title":"Moving Averages — 9 21 50 200 EMA","title_en":"Moving Averages — 9 21 50 200 EMA","category":"Technical Analysis","level":"Intermediate","description":"How moving averages work","slides":[{"heading":"Moving Average Kya Hoti Hai"},{"heading":"SMA vs EMA"},{"heading":"9 EMA — Short Term Momentum"},{"heading":"50 aur 200 EMA"},{"heading":"Golden Cross aur Death Cross"}]},
    {"week":13,"title":"RSI — Overbought Oversold Sahi Tarike Se","title_en":"RSI — Using Overbought Oversold Correctly","category":"Technical Analysis","level":"Intermediate","description":"RSI indicator common mistakes and correct usage","slides":[{"heading":"RSI Kya Measure Karta Hai"},{"heading":"RSI 30 70 Rule"},{"heading":"RSI Divergence"},{"heading":"AI360 Mein RSI Kaise Use Hota Hai"},{"heading":"RSI Entry Filter"}]},
    {"week":14,"title":"MACD — Trend Following Ka Best Tool","title_en":"MACD — The Best Trend Following Indicator","category":"Technical Analysis","level":"Intermediate","description":"MACD crossover, histogram, divergence","slides":[{"heading":"MACD Kya Hai"},{"heading":"Signal Line Crossover"},{"heading":"Histogram"},{"heading":"MACD Divergence"},{"heading":"MACD + EMA Combination"}]},
    {"week":15,"title":"Volume Analysis — Smart Money Kahaan","title_en":"Volume Analysis — Tracking Smart Money","category":"Technical Analysis","level":"Intermediate","description":"Volume is the truth behind price","slides":[{"heading":"Volume Kyon Price Se Important Hai"},{"heading":"High Volume Breakout"},{"heading":"Volume Divergence"},{"heading":"OBV Indicator"},{"heading":"FII DII Data Se Volume Analysis"}]},
    {"week":16,"title":"Trend Analysis — Uptrend Downtrend Sideways","title_en":"Trend Analysis — Identifying Market Direction","category":"Technical Analysis","level":"Intermediate","description":"How to identify and trade trends","slides":[{"heading":"Trend Kya Hoti Hai"},{"heading":"Uptrend Mein Kaise Trade Karein"},{"heading":"Downtrend Mein Kya Karein"},{"heading":"Sideways Market"},{"heading":"Trend Change Kaise Identify Karein"}]},
    {"week":17,"title":"Fundamental Analysis Kya Hai","title_en":"What Is Fundamental Analysis","category":"Fundamental Analysis","level":"Intermediate","description":"Introduction to fundamental analysis","slides":[{"heading":"Technical vs Fundamental"},{"heading":"Balance Sheet"},{"heading":"P&L Statement"},{"heading":"Cash Flow Statement"},{"heading":"Where to Find Annual Reports"}]},
    {"week":18,"title":"P/E Ratio — Stock Sasta Hai Ya Mahanga","title_en":"P/E Ratio — Cheap or Expensive","category":"Fundamental Analysis","level":"Intermediate","description":"Price to Earnings ratio correctly used","slides":[{"heading":"P/E Ratio Kya Hota Hai"},{"heading":"High P/E vs Low P/E"},{"heading":"Sector Comparison"},{"heading":"PEG Ratio"},{"heading":"P/E Trap"}]},
    {"week":19,"title":"ROE ROA ROCE — Quality Stocks","title_en":"ROE ROA ROCE — Finding Quality Stocks","category":"Fundamental Analysis","level":"Intermediate","description":"Return ratios explained","slides":[{"heading":"Return Ratios Kyon Matter Karte Hain"},{"heading":"ROE Explained"},{"heading":"ROCE — Better Than ROE"},{"heading":"Consistent ROE 15%+"},{"heading":"India Examples"}]},
    {"week":20,"title":"Debt Analysis — Kitna Karz Hai Company Par","title_en":"Debt Analysis — How Much Debt Is Too Much","category":"Fundamental Analysis","level":"Intermediate","description":"Debt-to-equity, interest coverage","slides":[{"heading":"Debt-to-Equity Ratio"},{"heading":"Interest Coverage Ratio"},{"heading":"Industry Normal Debt Levels"},{"heading":"Debt Trap Warning Signs"},{"heading":"Zero Debt Companies"}]},
    {"week":21,"title":"Sector Analysis","title_en":"Sector Analysis — Investing in Right Sector","category":"Fundamental Analysis","level":"Intermediate","description":"Business cycles and sector rotation","slides":[{"heading":"India Ke Top Sectors"},{"heading":"Sector Rotation"},{"heading":"Tailwind Sectors"},{"heading":"FII Kis Sector Mein"},{"heading":"AI360 Sector Filter"}]},
    {"week":22,"title":"Management Quality — Promoter Ko Kaise Samjhein","title_en":"Management Quality — Understanding Promoters","category":"Fundamental Analysis","level":"Intermediate","description":"Promoter holding, pledging, governance","slides":[{"heading":"Management Kyon Important Hai"},{"heading":"Promoter Holding"},{"heading":"Promoter Pledging — Red Flag"},{"heading":"Corporate Governance"},{"heading":"Good Management Examples India"}]},
    {"week":23,"title":"Competitive Moat — Wide Moat Stocks","title_en":"Competitive Moat — Finding Wide Moat Stocks","category":"Fundamental Analysis","level":"Advanced","description":"Warren Buffett's moat concept for India","slides":[{"heading":"Moat Kya Hota Hai"},{"heading":"5 Types of Moats"},{"heading":"India Mein Wide Moat Stocks"},{"heading":"Moat Kitne Saalo Tak"},{"heading":"Moat Wala Stock Kab Khareedein"}]},
    {"week":24,"title":"Valuation — Fair Value Kaise Calculate Karein","title_en":"Valuation — How to Calculate Fair Value","category":"Fundamental Analysis","level":"Advanced","description":"DCF, Graham number, earnings-based","slides":[{"heading":"Valuation Kyon Zaroori Hai"},{"heading":"P/E Based Valuation"},{"heading":"Graham Number"},{"heading":"DCF Simplified"},{"heading":"Margin of Safety"}]},
    {"week":25,"title":"Swing Trading — 5-10% Kaise Kamayein","title_en":"Swing Trading — Making 5-10% in a Week","category":"Trading Strategies","level":"Intermediate","description":"Complete swing trading system","slides":[{"heading":"Swing vs Intraday vs Positional"},{"heading":"Best Timeframe for Swing"},{"heading":"Entry Criteria"},{"heading":"Stop Loss Placement"},{"heading":"Target Setting RR 1:2"}]},
    {"week":26,"title":"Positional Trading — Hold 1-3 Mahine","title_en":"Positional Trading — Hold for 1-3 Months","category":"Trading Strategies","level":"Intermediate","description":"Positional trading with fundamentals + technicals","slides":[{"heading":"Positional Trading Kya Hota Hai"},{"heading":"Stock Selection"},{"heading":"Entry Point Weekly Chart"},{"heading":"Trailing Stop Loss"},{"heading":"When to Exit Early"}]},
    {"week":27,"title":"Momentum Trading","title_en":"Momentum Trading — Ride the Moving Stocks","category":"Trading Strategies","level":"Intermediate","description":"Buy strength, sell weakness","slides":[{"heading":"Momentum Kya Hai"},{"heading":"RS Relative Strength"},{"heading":"VCP Pattern"},{"heading":"Entry Timing with Volume"},{"heading":"Momentum Ka Life Cycle"}]},
    {"week":28,"title":"Breakout Trading","title_en":"Breakout Trading — Buying at New Highs","category":"Trading Strategies","level":"Intermediate","description":"How to trade breakouts correctly","slides":[{"heading":"Breakout Kya Hota Hai"},{"heading":"True vs False Breakout"},{"heading":"Volume Confirmation"},{"heading":"Entry After Confirmation"},{"heading":"SL and Target"}]},
    {"week":29,"title":"Base Entry — Sabse Kum Risk Ka Entry","title_en":"Base Entry — The Lowest Risk Entry","category":"Trading Strategies","level":"Advanced","description":"AI360 base entry before breakout","slides":[{"heading":"Base Entry Kya Hai"},{"heading":"Accumulation Zone"},{"heading":"VCP Pattern"},{"heading":"Entry Timing"},{"heading":"Risk Reward from Base"}]},
    {"week":30,"title":"Trailing Stop Loss — Profit Ko Lock Karein","title_en":"Trailing Stop Loss — Locking In Profits","category":"Trading Strategies","level":"Intermediate","description":"TSL methods — fixed, ATR-based, AI360 bot","slides":[{"heading":"Fixed SL vs Trailing SL"},{"heading":"ATR Based Trailing"},{"heading":"Breakeven Move"},{"heading":"Progressive Locking"},{"heading":"AI360 Bot Ka TSL System"}]},
    {"week":31,"title":"Intraday Trading — Sach Batata Hoon","title_en":"Intraday Trading — The Honest Truth","category":"Trading Strategies","level":"Intermediate","description":"Intraday reality check","slides":[{"heading":"Intraday Trading Reality"},{"heading":"Kab Intraday Sahi Hai"},{"heading":"Best Intraday Stocks India"},{"heading":"Gap and Go Strategy"},{"heading":"5 Non-Negotiable Rules"}]},
    {"week":32,"title":"Portfolio Building — Balanced Portfolio","title_en":"Portfolio Building — Creating Balance","category":"Trading Strategies","level":"Intermediate","description":"Complete portfolio construction","slides":[{"heading":"Portfolio Kya Hota Hai"},{"heading":"Asset Allocation"},{"heading":"Diversification"},{"heading":"Rebalancing"},{"heading":"Quarterly Review"}]},
    {"week":33,"title":"Options Introduction — Call Put Basics","title_en":"Options Introduction — Call and Put Basics","category":"Options","level":"Beginner","description":"First introduction to options","slides":[{"heading":"Option Contract Kya Hota Hai"},{"heading":"Call Option"},{"heading":"Put Option"},{"heading":"Premium Kya Hota Hai"},{"heading":"Maximum Loss Limited"}]},
    {"week":34,"title":"Options Greeks — Delta Theta Vega","title_en":"Options Greeks Simply Explained","category":"Options","level":"Intermediate","description":"Greeks explained with Indian examples","slides":[{"heading":"Greeks Kyon Zaroori Hain"},{"heading":"Delta"},{"heading":"Theta"},{"heading":"Vega"},{"heading":"Practice Karein"}]},
    {"week":35,"title":"Option Buying Strategy — CE PE Kab Khareedein","title_en":"Option Buying — When to Buy CE and PE","category":"Options","level":"Intermediate","description":"Directional option buying","slides":[{"heading":"3 Cheezein Sahi Karni Hain"},{"heading":"Strike Selection ATM OTM ITM"},{"heading":"Expiry Selection"},{"heading":"VIX Check"},{"heading":"Stop Loss and Exit"}]},
    {"week":36,"title":"Option Selling — Consistent Income","title_en":"Option Selling — Generating Consistent Income","category":"Options","level":"Advanced","description":"Covered call, cash secured put, spreads","slides":[{"heading":"Option Sellers Kyun Jeette Hain"},{"heading":"Covered Call"},{"heading":"Cash Secured Put"},{"heading":"Bull Put Spread"},{"heading":"Risk Management Rules"}]},
    {"week":37,"title":"Nifty Weekly Expiry Strategy","title_en":"Nifty Weekly Expiry Strategy","category":"Options","level":"Intermediate","description":"Thursday expiry — max pain, entry, exit","slides":[{"heading":"Thursday Kyon Important Hai"},{"heading":"Max Pain"},{"heading":"Expiry Day Entry"},{"heading":"Same Day Exit"},{"heading":"Last 30 Minutes Rule"}]},
    {"week":38,"title":"India VIX — Fear Ka Indicator","title_en":"India VIX — The Fear Indicator","category":"Options","level":"Intermediate","description":"India VIX for options decisions","slides":[{"heading":"VIX Kya Measure Karta Hai"},{"heading":"VIX High — Options Mehnge"},{"heading":"VIX Low — Options Saste"},{"heading":"VIX 15-18 Best Zone"},{"heading":"AI360 VIX Filter"}]},
    {"week":39,"title":"F&O Ban List — Kya Hota Hai","title_en":"F&O Ban List — What It Is and Why","category":"Options","level":"Intermediate","description":"SEBI F&O ban, open interest limits","slides":[{"heading":"F&O Ban Kya Hota Hai"},{"heading":"Open Interest Limit"},{"heading":"Ban Mein Kya Kar Sakte Hain"},{"heading":"Warning Signs"},{"heading":"NSE Website Free Check"}]},
    {"week":40,"title":"Futures Trading — Basics Aur Risk","title_en":"Futures Trading — Basics and Risks","category":"Options","level":"Advanced","description":"Futures contracts — leverage, margin","slides":[{"heading":"Futures Contract Kya Hota Hai"},{"heading":"Leverage"},{"heading":"Margin Call"},{"heading":"Rollover"},{"heading":"Futures vs Options"}]},
    {"week":41,"title":"Position Sizing — Ek Trade Mein Kitna Lagayein","title_en":"Position Sizing — How Much to Risk Per Trade","category":"Risk Management","level":"Intermediate","description":"Position sizing formula, 1% rule","slides":[{"heading":"Position Sizing Kyon Important Hai"},{"heading":"1% Rule"},{"heading":"Kelly Criterion"},{"heading":"Capital Tiers"},{"heading":"AI360 Position Sizing"}]},
    {"week":42,"title":"Risk Management — Capital Bachana Pehle","title_en":"Risk Management — Protecting Capital First","category":"Risk Management","level":"Intermediate","description":"Complete risk management framework","slides":[{"heading":"Capital Preservation Rule One"},{"heading":"Maximum Drawdown"},{"heading":"Concentration Risk"},{"heading":"Sector Concentration"},{"heading":"When to Reduce Position"}]},
    {"week":43,"title":"Trading Psychology — Mann Ko Control Karein","title_en":"Trading Psychology — Controlling Your Mind","category":"Psychology","level":"Intermediate","description":"FOMO, revenge trading, overconfidence","slides":[{"heading":"90% Traders Kyon Harte Hain"},{"heading":"FOMO"},{"heading":"Revenge Trading"},{"heading":"Overconfidence"},{"heading":"Trading Journal"}]},
    {"week":44,"title":"Personal Finance — Savings Investment Insurance","title_en":"Personal Finance — Savings Investment Insurance","category":"Personal Finance","level":"Beginner","description":"Emergency fund, term insurance, health insurance","slides":[{"heading":"Invest Karne Se Pehle Yeh Karo"},{"heading":"Emergency Fund"},{"heading":"Term Insurance"},{"heading":"Health Insurance"},{"heading":"Invest Karne Ki Sahi Order"}]},
    {"week":45,"title":"Tax Planning — Trading Income Par Tax","title_en":"Tax Planning — Reducing Tax on Trading","category":"Personal Finance","level":"Intermediate","description":"STCG, LTCG, tax loss harvesting","slides":[{"heading":"Trading Income Par Kitna Tax"},{"heading":"STCG vs LTCG"},{"heading":"Tax Loss Harvesting"},{"heading":"F&O Income — Business Income"},{"heading":"CA Se Kab Milein"}]},
    {"week":46,"title":"Inflation — Apna Paisa Protect Karo","title_en":"Inflation — Protecting Your Money","category":"Personal Finance","level":"Beginner","description":"Inflation impact, how stocks beat it","slides":[{"heading":"Inflation Kya Hai"},{"heading":"FD Mein Paisa — Inflation Se Nahi Bachata"},{"heading":"Stocks — Best Inflation Beater"},{"heading":"Gold — Real Inflation Hedge"},{"heading":"Real Return Calculate"}]},
    {"week":47,"title":"Retirement Planning — Kitna Chahiye","title_en":"Retirement Planning — How Much Do You Need","category":"Personal Finance","level":"Intermediate","description":"Retirement corpus, NPS, EPF, SWP","slides":[{"heading":"Retirement Corpus Kaise Calculate Karein"},{"heading":"NPS"},{"heading":"EPF"},{"heading":"SWP"},{"heading":"4% Rule"}]},
    {"week":48,"title":"Global Investing — USA Stocks India Se","title_en":"Global Investing — Buy USA Stocks From India","category":"Personal Finance","level":"Intermediate","description":"LRS route, platforms, tax implications","slides":[{"heading":"India Se Videsh Mein Invest Karna Legal"},{"heading":"LRS Route"},{"heading":"Platforms — Vested INDmoney"},{"heading":"Tax India Mein"},{"heading":"Best US ETFs for Indian Investors"}]},
    {"week":49,"title":"Algorithmic Trading — Bot Se Trade Karein","title_en":"Algorithmic Trading — Trading With Bots","category":"Advanced","level":"Advanced","description":"Algo trading basics, AI360 system","slides":[{"heading":"Algo Trading Kya Hai"},{"heading":"Backtesting"},{"heading":"Python Se Trading Bot"},{"heading":"AI360 Trading System"},{"heading":"Algo Trading Risks"}]},
    {"week":50,"title":"Global Markets — USA UK Brazil Se Kya Seekhein","title_en":"Global Markets — Learning From USA UK Brazil","category":"Advanced","level":"Advanced","description":"Global market correlations with India","slides":[{"heading":"India Market Aur Global Connection"},{"heading":"US Market Girta Hai Toh India Kyun"},{"heading":"FII — Foreign Money Ka Effect"},{"heading":"Dollar Index DXY"},{"heading":"Global Opportunities"}]},
    {"week":51,"title":"Complete Trading Plan Banayein","title_en":"Build Your Complete Trading Plan","category":"Advanced","level":"Advanced","description":"Rules, journal, review system, goals","slides":[{"heading":"Trading Plan Kyon Zaroori Hai"},{"heading":"Entry Rules"},{"heading":"Exit Rules"},{"heading":"Daily Weekly Monthly Review"},{"heading":"Realistic Goals"}]},
    {"week":52,"title":"Course Complete — Aage Kya Karein","title_en":"Course Complete — What to Do Next","category":"Advanced","level":"Advanced","description":"52-week review and next steps","slides":[{"heading":"52 Weeks Mein Aapne Kya Seekha"},{"heading":"Paper Trading Se Live Trading"},{"heading":"AI360 Premium"},{"heading":"Community"},{"heading":"Aapka Agle 52 Hafte Ka Plan"}]},
]


# ══════════════════════════════════════════════════════════════════════
# DAY-BASED TOPICS (for articles, reels, morning reel)
# ══════════════════════════════════════════════════════════════════════

MONDAY_TOPICS = [
    {"title":"Options Trading Complete Beginner Guide","category":"Options","level":"Beginner","target_primary":"India","target_secondary":["USA","UK","Brazil"],"seo_seed":"options trading for beginners India 2026 step by step","long_tail_keywords":["how to start options trading in India with 10000 rupees","Nifty options buying strategy for beginners"],"affiliate_angle":"open trading account to start options — Zerodha, Dhan","slides":[{"heading":"What is an Option Contract?","points":["Right but not obligation to buy or sell","Call = right to BUY","Put = right to SELL","Premium = price you pay","Max loss limited to premium"]},{"heading":"How Call Options Make Money","points":["Buy call when you think price will rise","Example: Nifty at 22000 buy 22200 call at Rs.50","If Nifty rises to 22500 — call worth Rs.300 — 6x","If stays below 22200 — lose only Rs.50","Leverage without borrowing"]}]},
    {"title":"Option Selling — Collect Premium Like Insurance Companies","category":"Options","level":"Intermediate","target_primary":"India","target_secondary":["USA","UK"],"seo_seed":"option selling strategy India monthly income 2026","long_tail_keywords":["how to earn monthly income from option selling Nifty","covered call strategy India step by step 2026"],"affiliate_angle":"Zerodha Sensibull for option strategy builder","slides":[{"heading":"Why Option Sellers Win Long Term","points":["80% options expire worthless","Time decay works FOR sellers","Like being the casino","Buffett sold puts to buy Coca-Cola","India: Bank Nifty weekly options huge premium"]}]},
]

TUESDAY_TOPICS = [
    {"title":"Candlestick Patterns — The 5 That Actually Make Money","category":"Technical Analysis","level":"Beginner","target_primary":"Global","target_secondary":["India","USA","UK"],"seo_seed":"candlestick patterns that work best stocks crypto Nifty 2026","long_tail_keywords":["which candlestick pattern is most reliable for Nifty trading","bullish engulfing pattern how to trade it correctly"],"affiliate_angle":"TradingView free plan for chart analysis","slides":[{"heading":"The 5 Candlestick Patterns Worth Your Time","points":["Most traders memorise 50 — professionals focus on 5","These work on Nifty S&P 500 Bitcoin Forex","Pattern only useful with support resistance and volume"]}]},
    {"title":"RSI Complete Guide — How to Actually Use It Profitably","category":"Technical Analysis","level":"Intermediate","target_primary":"Global","target_secondary":["India","USA","Brazil"],"seo_seed":"RSI indicator how to use correctly profitable trading strategy 2026","long_tail_keywords":["RSI divergence strategy stocks India","how to use RSI 14 correctly for swing trading"],"affiliate_angle":"TradingView for RSI charting","slides":[{"heading":"RSI Overbought Oversold — Most Misunderstood","points":["RSI above 70 does not always mean sell","Trending stocks stay overbought for weeks","RSI divergence far more reliable than levels"]}]},
]

WEDNESDAY_TOPICS = [
    {"title":"P/E Ratio — Is This Stock Cheap or Expensive","category":"Fundamental Analysis","level":"Beginner","target_primary":"Global","target_secondary":["India","USA"],"seo_seed":"PE ratio how to use correctly stock valuation India 2026","long_tail_keywords":["what is a good PE ratio for Indian stocks","PE ratio trap how to avoid overpaying"],"affiliate_angle":"Screener.in free stock analysis tool India","slides":[{"heading":"PE Ratio — Most Misused Number in Investing","points":["PE tells you how much you pay for Rs.1 of earnings","High PE not always bad — depends on growth","Always compare within same sector"]}]},
    {"title":"FII DII Data — How Smart Money Moves Indian Markets","category":"Fundamental Analysis","level":"Intermediate","target_primary":"India","target_secondary":["Global"],"seo_seed":"FII DII buying selling data how to use for stock market India","long_tail_keywords":["how to track FII buying selling in Indian market"],"affiliate_angle":"NSEIndia.com for free FII DII daily data","slides":[{"heading":"FII vs DII — Who Has More Influence","points":["FII = Foreign Institutional Investors","DII = Domestic Institutional Investors — LIC MFs","FII moves more volatile and cause larger swings"]}]},
]

THURSDAY_TOPICS = [
    {"title":"Swing Trading Strategy — How to Make 5-10% in a Week","category":"Strategies","level":"Intermediate","target_primary":"India","target_secondary":["USA","UK"],"seo_seed":"swing trading strategy India 2026 5 to 10 percent weekly","long_tail_keywords":["how to swing trade Nifty 200 stocks for 5 percent profit"],"affiliate_angle":"AI360 Advance membership for daily swing trade signals","slides":[{"heading":"Swing Trading Mein Kya Chahiye","points":["Good stock with strong fundamental backing","Technical breakout or base entry","Clear SL at 2xATR and Target at 4xATR","Patience to hold 3-7 days"]}]},
    {"title":"LIC vs Term Insurance — Which One Should You Buy","category":"Personal Finance","level":"Beginner","target_primary":"India","target_secondary":["UAE"],"seo_seed":"LIC endowment vs term insurance which is better India 2026","long_tail_keywords":["why term insurance is better than LIC endowment plan India"],"affiliate_angle":"Policybazaar term insurance comparison","slides":[{"heading":"Term Insurance vs LIC Endowment — The Real Math","points":["Term: Rs.1 crore cover for Rs.10000-15000 per year","LIC endowment: Rs.50 lakh cover for Rs.60000 per year","Difference invested in index fund = 10x more at retirement"]}]},
]

FRIDAY_TOPICS = [
    {"title":"Trading Psychology — Why 90% of Traders Fail","category":"Psychology","level":"All Levels","target_primary":"Global","target_secondary":["India","USA","UK"],"seo_seed":"trading psychology mistakes why traders lose money India 2026","long_tail_keywords":["how to control emotions in trading stocks India","FOMO trading how to avoid"],"affiliate_angle":"AI360 Telegram — signals remove emotional guesswork","slides":[{"heading":"The Real Reason Traders Fail — Not Strategy","points":["90% lose not because of bad strategy","Lose because of undisciplined psychology","FOMO revenge trading overconfidence","System + discipline beats intelligence"]}]},
    {"title":"Risk Management — Preserve Capital Before Everything","category":"Risk Management","level":"All Levels","target_primary":"Global","target_secondary":["India","USA"],"seo_seed":"risk management trading capital preservation India 2026","long_tail_keywords":["how much to risk per trade stocks India"],"affiliate_angle":"AI360 system manages risk automatically with TSL","slides":[{"heading":"Capital Preservation — First Job of Every Trader","points":["Cannot make money if lost all capital","Never risk more than 1-2% per trade","This rule keeps you in game long enough to learn"]}]},
]

WEEKEND_TOPICS = [
    {"title":"How to Build Wealth From Zero — Complete Roadmap","category":"Personal Finance","level":"Beginner","target_primary":"Global","target_secondary":["India","USA","UAE","UK"],"seo_seed":"how to build wealth from zero salary India step by step 2026","long_tail_keywords":["how to invest on a 30000 salary India 2026"],"affiliate_angle":"Zerodha account + SIP in index fund — beginner combo","slides":[{"heading":"Wealth Building — Step by Step From Zero","points":["Step 1: Emergency fund — 6 months expenses","Step 2: Term insurance — Rs.1 crore minimum","Step 3: Health insurance — Rs.10 lakh family floater","Step 4: Index fund SIP — Rs.5000 per month","Step 5: After 1 year — add individual stock positions"]}]},
    {"title":"Compounding — The 8th Wonder of the World","category":"Personal Finance","level":"Beginner","target_primary":"Global","target_secondary":["India","USA","Brazil"],"seo_seed":"power of compounding explained simply wealth building 2026","long_tail_keywords":["compounding interest example India stock market returns"],"affiliate_angle":"Start SIP today — any amount — Zerodha Groww","slides":[{"heading":"Compounding — Why Einstein Called It 8th Wonder","points":["Rs.10000 at 12% per year = Rs.96000 in 20 years","Rs.10000 per month SIP at 12% = Rs.1 crore in 20 years","Secret: start early — time more valuable than amount"]}]},
]

HOLIDAY_TOPICS = [
    {"title":"Market Band Hai — Use Karo Seekhne Ke Liye","category":"Motivation","level":"All Levels","target_primary":"India","target_secondary":["UAE"],"seo_seed":"stock market holiday what to do trading education India","long_tail_keywords":["what to do when stock market is closed India"],"affiliate_angle":"AI360 education videos — free on YouTube","slides":[{"heading":"Market Band Hai — Yeh Time Waste Mat Karo","points":["Top traders use holidays for education and review","Review last month trades — what worked what did not","Study one new concept today","Plan next week watchlist","Update trading journal"]}]},
]


# ══════════════════════════════════════════════════════════════════════
# PUBLIC FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def get_todays_topic() -> dict:
    """
    Returns topic for articles, reels, morning reel — based on day of week.
    """
    day = datetime.now().weekday()
    day_map = {
        0: MONDAY_TOPICS,
        1: TUESDAY_TOPICS,
        2: WEDNESDAY_TOPICS,
        3: THURSDAY_TOPICS,
        4: FRIDAY_TOPICS,
        5: WEEKEND_TOPICS,
        6: WEEKEND_TOPICS,
    }
    topics  = day_map.get(day, MONDAY_TOPICS)
    week_num = datetime.now().isocalendar()[1]
    return topics[week_num % len(topics)]


def get_holiday_topic() -> dict:
    """Returns holiday-specific motivational topic."""
    week_num = datetime.now().isocalendar()[1]
    return HOLIDAY_TOPICS[week_num % len(HOLIDAY_TOPICS)]


def get_todays_education_topic() -> dict:
    """
    Returns 52-week progressive course topic for education videos.
    Week auto-calculated from COURSE_START = date(2026, 5, 15).
    Returns dict WITH "week" key for use in title.
    """
    today            = date.today()
    days_since_start = (today - COURSE_START).days
    week_idx         = max(0, days_since_start // 7) % len(EDUCATION_COURSE)
    topic            = EDUCATION_COURSE[week_idx].copy()
    topic["week"]    = week_idx + 1
    print(f"[CALENDAR] Education Week {topic['week']}: {topic['title']}")
    return topic
