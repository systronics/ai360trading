"""
AI360Trading — Content Calendar v2.4
======================================
v2.4 CHANGES (2026-05-31) — dedicated SEO seeds for 4 new categories:
- Added mutual / gold / ipo / world seed rows (primary_target = new pillar id's
  first token) in BOTH market and weekend modes, placed BEFORE the "global"
  fallback row so each new pillar matches its own seed (verified). New
  _new_category_seed_rows() + _AFF_HINTS entries for the new categories.

v2.3 CHANGES (May 2026) — SEO SEEDS BLOCK FIX:
- get_article_seo_seeds() now returns a LIST OF PILLAR DICTS (was: a single
  dict of global/india/usa/uk seed lists). generate_articles.py consumes the
  return value as `for s in calendar_seeds: s["primary_target"], s["seo_seed"],
  s["long_tail"], s["affiliate_hint"]` — the old dict shape silently raised
  TypeError on every run, leaving the SEO keyword block empty in every
  generated article. New shape carries one dict per pillar (stock, bitcoin,
  personal, ai) + one "global" fallback row, with day-of-week seed rotation
  so Mon-Fri articles get fresh keyword angles each weekday.
- Weekend/holiday mode returns evergreen pillar dicts (no live price refs).
- get_todays_topic(), get_todays_education_topic(), get_holiday_topic() — unchanged.

v2.2 CHANGES (May 2026):
- Added get_article_seo_seeds() — fixes "[WARN] content_calendar.py not found"
  generate_articles.py imports this function — was missing in v2.1
- Added no_price_numbers rule to weekend/holiday seeds (NOTE: never actually
  consumed by generate_articles.py — superseded by v2.3 reshape)

Author: AI360Trading Automation
Last Updated: 2026-05-26
"""

from datetime import date, datetime

# ── Course start date — NEVER change this ─────────────────────────────────────
COURSE_START = date(2026, 5, 15)


# ══════════════════════════════════════════════════════════════════════
# get_article_seo_seeds() — v2.3 RESHAPED
# Called by generate_articles.py to get SEO seed keywords.
# Returns a LIST of pillar dicts (one per pillar + a "global" fallback row).
# Consumer (generate_articles.py) iterates and matches by primary_target.
# ══════════════════════════════════════════════════════════════════════

# Affiliate hints reused across modes
_AFF_HINTS = {
    "stock":    "Zerodha (India), Webull (USA), Trading 212 (UK) — open trading account",
    "bitcoin":  "CoinDCX (India), Coinbase (USA), Kraken (UK) — buy crypto safely",
    "personal": "PolicyBazaar (India), Policygenius (USA), CompareTheMarket (UK)",
    "ai":       "TradingView free plan + AI360 Telegram free signals",
    # 2026-05-31 — new categories (primary_target = pillar id's first token)
    "mutual":   "Groww / Zerodha Coin (India), Vanguard (USA/UK) — start an SIP in index funds",
    "gold":     "Sovereign Gold Bonds & Gold ETF via Zerodha/Groww (India) — own gold the smart way",
    "ipo":      "Zerodha / Groww demat account (India) to apply for IPOs",
    "world":    "Vested / INDmoney (India) for US stocks; broker access for global indices",
}


# Dedicated SEO seeds for the 4 new categories (2026-05-31). Returned as rows so
# they can be matched by primary_target. IMPORTANT: the consumer in
# generate_articles.py matches primary_target in ["global", pillar_prefix] and
# takes the FIRST hit — so these rows must always be placed BEFORE the "global"
# fallback row, or a new pillar would grab the global seed instead of its own.
def _new_category_seed_rows() -> list:
    return [
        {
            "primary_target": "mutual",
            "seo_seed": "best mutual funds and SIP guide India 2026 honest no hype",
            "long_tail": [
                "SIP vs lump sum which builds more wealth India 2026 real numbers",
                "index fund vs active mutual fund honest comparison for beginners",
            ],
            "affiliate_hint": _AFF_HINTS["mutual"],
        },
        {
            "primary_target": "gold",
            "seo_seed": "gold investment 2026 gold vs stocks vs FD honest comparison",
            "long_tail": [
                "sovereign gold bond vs physical gold which is better India",
                "how much gold should be in your portfolio the real answer",
            ],
            "affiliate_hint": _AFF_HINTS["gold"],
        },
        {
            "primary_target": "ipo",
            "seo_seed": "how to apply for IPO and evaluate it beginner guide 2026",
            "long_tail": [
                "how to apply for IPO online India ASBA UPI step by step",
                "what is IPO GMP grey market premium and its real limits",
            ],
            "affiliate_hint": _AFF_HINTS["ipo"],
        },
        {
            "primary_target": "world",
            "seo_seed": "global markets explained Dow Nasdaq dollar impact on Nifty 2026",
            "long_tail": [
                "why US markets and the dollar index move Indian markets",
                "developed vs emerging markets where to invest 2026",
            ],
            "affiliate_hint": _AFF_HINTS["world"],
        },
    ]


def get_article_seo_seeds(mode: str = "market") -> list:
    """
    Returns SEO seed keywords for article generation.
    Called by generate_articles.py at the start of each run.

    Return shape (v2.3):
      list[dict] — one dict per pillar + one "global" fallback row.
      Each dict carries:
        - primary_target: one of "stock"|"bitcoin"|"personal"|"ai"|"global"
          (matches pillar["id"].split("-")[0] in the consumer)
        - seo_seed: primary keyword phrase (string, ≤90 chars)
        - long_tail: list of 2 long-tail keyword phrases
        - affiliate_hint: contextual affiliate angle (string)

    Why a list (not a dict): generate_articles.py iterates with
        next((s for s in calendar_seeds if s["primary_target"].lower() in
              ["global", pillar["id"].split("-")[0]]), calendar_seeds[i % N])
    The pre-v2.3 dict return silently raised TypeError, leaving the SEO
    block empty in every article. v2.3 fixes that.
    """
    day = datetime.now().weekday()  # 0=Mon, 6=Sun

    if mode in ("weekend", "holiday"):
        # Evergreen seeds — no live price refs, beginner-focused
        rows = [
            {
                "primary_target": "stock",
                "seo_seed": "how to invest in stock market for beginners 2026",
                "long_tail": [
                    "how to start investing in stocks with small money India USA UK",
                    "index fund vs mutual fund which is better for beginners",
                ],
                "affiliate_hint": _AFF_HINTS["stock"],
            },
            {
                "primary_target": "bitcoin",
                "seo_seed": "how to buy bitcoin safely beginner guide 2026",
                "long_tail": [
                    "is bitcoin a safe investment for beginners in 2026",
                    "cold wallet vs exchange which one for crypto beginners",
                ],
                "affiliate_hint": _AFF_HINTS["bitcoin"],
            },
            {
                "primary_target": "personal",
                "seo_seed": "best term life insurance India USA UK comparison 2026",
                "long_tail": [
                    "term insurance vs LIC endowment plan which is better India",
                    "how much life insurance do I actually need real calculator",
                ],
                "affiliate_hint": _AFF_HINTS["personal"],
            },
            {
                "primary_target": "ai",
                "seo_seed": "best free AI trading tools for beginners 2026",
                "long_tail": [
                    "free stock screener AI tools for retail traders India",
                    "how to use AI for stock market analysis without coding",
                ],
                "affiliate_hint": _AFF_HINTS["ai"],
            },
        ]
        rows += _new_category_seed_rows()   # mutual, gold, ipo, world — BEFORE global
        rows.append({
            "primary_target": "global",
            "seo_seed": "power of compound interest wealth building 2026",
            "long_tail": [
                "how to build wealth from zero salary step by step",
                "passive income ideas that actually work in 2026",
            ],
            "affiliate_hint": "Open a long-term investing account — broker or index-fund SIP",
        })
        return rows

    # Market mode (Mon-Fri) — pillar × day-of-week seed grid
    market_grid = {
        0: {  # Monday — Options / Levels angle
            "stock":    ("Nifty 50 levels and S&P 500 forecast today 2026",
                         ["how to identify intraday breakout on Nifty India",
                          "S&P 500 support and resistance levels for today"]),
            "bitcoin":  ("Bitcoin price today analysis BTC USD INR 2026",
                         ["is bitcoin going up or down today honest analysis",
                          "bitcoin support and resistance levels real numbers"]),
            "personal": ("best term insurance India 2026 cheapest premium honest review",
                         ["LIC vs HDFC vs ICICI term insurance honest comparison",
                          "how much term cover do I actually need calculator"]),
            "ai":       ("free AI trading tools that actually work India 2026",
                         ["free stock screener for Nifty NSE breakout 2026",
                          "how retail traders use AI without writing any code"]),
        },
        1: {  # Tuesday — Technical Analysis
            "stock":    ("how to read stock chart for swing trading 2026",
                         ["RSI 14 strategy that actually works on Nifty",
                          "moving average crossover strategy 50 200 EMA"]),
            "bitcoin":  ("bitcoin technical analysis support resistance 2026",
                         ["bitcoin RSI divergence trade setup explained",
                          "BTC EMA crossover signal beginner guide"]),
            "personal": ("SIP returns calculator real numbers India 2026",
                         ["SIP vs lump sum which gives better returns India",
                          "best SIP mutual fund India 2026 first time investor"]),
            "ai":       ("AI stock screener vs traditional technical analysis 2026",
                         ["best free AI chart pattern recognition tool",
                          "algorithmic trading for beginners no coding 2026"]),
        },
        2: {  # Wednesday — Fundamental + Macro
            "stock":    ("FII DII data Indian market direction today 2026",
                         ["how FII selling affects Nifty in the short term",
                          "DII buying which sectors today India 2026"]),
            "bitcoin":  ("Bitcoin ETF institutional flows weekly 2026",
                         ["spot Bitcoin ETF inflows weekly analysis 2026",
                          "MicroStrategy bitcoin holdings impact on BTC price"]),
            "personal": ("how to read annual report stock investing 2026",
                         ["PE ratio explained for beginners Indian stocks",
                          "ROE ROCE quality stocks India long term holdings"]),
            "ai":       ("AI fintech stocks Nvidia Microsoft Google 2026",
                         ["best AI stocks to buy India 2026 long term portfolio",
                          "Nvidia earnings impact on AI stocks globally 2026"]),
        },
        3: {  # Thursday — Strategies + Personal Finance
            "stock":    ("swing trading Nifty 200 stocks 5-10 percent weekly 2026",
                         ["how to find swing trading stocks India 2026",
                          "positional trading 1-3 months strategy NSE India"]),
            "bitcoin":  ("Ethereum vs Bitcoin which to buy in 2026",
                         ["altcoin season indicator 2026 explained",
                          "crypto portfolio allocation for beginners in India"]),
            "personal": ("how to build Rs.1 crore portfolio on salaried income",
                         ["PPF vs NPS vs ELSS for tax saving India 2026",
                          "retirement planning calculator India real numbers"]),
            "ai":       ("AI trading bot India NSE algo trading rules 2026",
                         ["SEBI algo trading regulations retail traders India",
                          "machine learning in trading explained simply"]),
        },
        4: {  # Friday — Psychology + Risk
            "stock":    ("why 90 percent of traders lose money real reasons 2026",
                         ["trading psychology rules every Nifty trader needs",
                          "how to control FOMO and revenge trading habits"]),
            "bitcoin":  ("crypto trading psychology bear market survival 2026",
                         ["how to handle bitcoin crash mentally as a beginner",
                          "DCA strategy bitcoin volatility for beginners"]),
            "personal": ("emergency fund how much do you actually need 2026",
                         ["how to save your first Rs.1 lakh India realistic plan",
                          "credit card debt vs investment which to clear first"]),
            "ai":       ("how AI removes emotion from trading decisions 2026",
                         ["best free AI signal Telegram channel India 2026",
                          "rule based vs discretionary trading which wins"]),
        },
    }

    pillar_keys = ("stock", "bitcoin", "personal", "ai")
    grid = market_grid.get(day, market_grid[0])  # Sat/Sun shouldn't reach here (mode≠market) but safe-default
    out = []
    for key in pillar_keys:
        seed, long_tail = grid[key]
        out.append({
            "primary_target": key,
            "seo_seed":       seed,
            "long_tail":      long_tail,
            "affiliate_hint": _AFF_HINTS[key],
        })
    # New categories (mutual funds, gold, IPO, world markets) — dedicated seeds,
    # appended BEFORE the global row so each new pillar matches its own seed first.
    out.extend(_new_category_seed_rows())
    # Global fallback row — picked by next()'s default branch when pillar-prefix
    # match misses (shouldn't normally, but keeps the consumer safe).
    out.append({
        "primary_target": "global",
        "seo_seed":       "stock market and crypto outlook today global view 2026",
        "long_tail": [
            "global markets today Nifty S&P 500 bitcoin combined view",
            "US Fed rate decision impact on global markets 2026",
        ],
        "affiliate_hint": "AI360Trading free Telegram channels — Basic / Advance / Premium",
    })
    return out


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
