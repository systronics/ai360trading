"""
AI360Trading — Content Calendar v2.1
======================================
v2.1 CHANGES (May 2026):
- Added EDUCATION_COURSE: true 52-week progressive investing course
- get_todays_education_topic() now returns week number from COURSE_START
- Day-based topics (Monday-Friday) preserved for articles and reels
- Education videos now follow progressive curriculum Week 1 → Week 52

STRUCTURE:
  Articles/Reels: MONDAY_TOPICS, TUESDAY_TOPICS etc. (day-of-week rotation)
  Education Videos: EDUCATION_COURSE (progressive 52-week from COURSE_START)

Target countries: India, USA, UK, UAE, Canada, Australia, Brazil

Author: AI360Trading Automation
Last Updated: May 2026
"""

from datetime import date, datetime

# ── Course start date — NEVER change this ─────────────────────────────────────
COURSE_START = date(2026, 5, 15)   # Week 1 begins here

# ══════════════════════════════════════════════════════════════════════
# 52-WEEK EDUCATION COURSE — Progressive Curriculum
# Week auto-calculated from COURSE_START
# Each week builds on the previous — beginner to advanced
# ══════════════════════════════════════════════════════════════════════

EDUCATION_COURSE = [

    # ── PHASE 1: FOUNDATIONS (Weeks 1-8) ──────────────────────────────────────
    {
        "week": 1,
        "title": "Stock Market Kya Hai",
        "title_en": "What Is the Stock Market",
        "category": "Foundations",
        "level": "Beginner",
        "description": "Basics: Shares, NSE, BSE explained simply",
        "target_audience": "Complete beginners — never invested before",
        "slides": [
            {"heading": "Stock Market Kya Hota Hai"},
            {"heading": "Share Kya Hai — Ownership Ka Concept"},
            {"heading": "NSE Aur BSE Mein Kya Fark Hai"},
            {"heading": "SEBI — Market Ka Police Officer"},
            {"heading": "Market Mein Paisa Kaise Lagta Hai"},
        ],
    },
    {
        "week": 2,
        "title": "Demat Account Kaise Kholein",
        "title_en": "How to Open a Demat Account",
        "category": "Foundations",
        "level": "Beginner",
        "description": "Zerodha, Dhan, Groww — which broker to choose and how to start",
        "target_audience": "Beginners wanting to invest for the first time",
        "slides": [
            {"heading": "Demat Account Kya Hota Hai"},
            {"heading": "Broker Kaise Chunein — Zerodha vs Dhan vs Groww"},
            {"heading": "Account Kholne Ka Poora Process"},
            {"heading": "KYC Kya Hai Aur Kaise Karein"},
            {"heading": "Pehla Share Kaise Khareedein"},
        ],
    },
    {
        "week": 3,
        "title": "Nifty 50 Aur Sensex Samjhein",
        "title_en": "Understanding Nifty 50 and Sensex",
        "category": "Foundations",
        "level": "Beginner",
        "description": "What market indices are and why they matter for every investor",
        "target_audience": "Beginners who have a demat account",
        "slides": [
            {"heading": "Index Kya Hota Hai"},
            {"heading": "Nifty 50 Mein Kaunse Stocks Hain"},
            {"heading": "Sensex — Bombay Stock Exchange Ka Index"},
            {"heading": "Index Upar Jaaye Toh Mera Portfolio Bhi Upar Jaayega"},
            {"heading": "Global Indices — Dow Jones, Nasdaq, S&P 500"},
        ],
    },
    {
        "week": 4,
        "title": "IPO Mein Invest Karein Ya Nahi",
        "title_en": "Should You Invest in IPOs",
        "category": "Foundations",
        "level": "Beginner",
        "description": "IPO basics, allotment process, GMP, and whether IPOs are worth it",
        "target_audience": "Beginners curious about new stock listings",
        "slides": [
            {"heading": "IPO Kya Hota Hai"},
            {"heading": "Company IPO Kyon Laati Hai"},
            {"heading": "IPO Apply Kaise Karein — Step by Step"},
            {"heading": "GMP Kya Hai Aur Kya Believe Karein"},
            {"heading": "IPO Mein Kitna Risk Hai"},
        ],
    },
    {
        "week": 5,
        "title": "Dividend — Stocks Se Passive Income",
        "title_en": "Dividends — Passive Income From Stocks",
        "category": "Foundations",
        "level": "Beginner",
        "description": "Dividend basics, yield, ex-dividend date, dividend investing strategy",
        "target_audience": "Beginners wanting passive income from stocks",
        "slides": [
            {"heading": "Dividend Kya Hota Hai"},
            {"heading": "Dividend Yield Kaise Calculate Karein"},
            {"heading": "Ex-Dividend Date — Kyun Important Hai"},
            {"heading": "Top Dividend Stocks India 2026"},
            {"heading": "Dividend Reinvestment — Compounding Ka Jaadu"},
        ],
    },
    {
        "week": 6,
        "title": "Large Cap vs Mid Cap vs Small Cap",
        "title_en": "Large Cap vs Mid Cap vs Small Cap Stocks",
        "category": "Foundations",
        "level": "Beginner",
        "description": "Understanding market capitalisation and what it means for risk and returns",
        "target_audience": "Beginners building their first portfolio",
        "slides": [
            {"heading": "Market Cap Kya Hota Hai"},
            {"heading": "Large Cap — Stability Aur Slow Growth"},
            {"heading": "Mid Cap — Balance of Risk and Reward"},
            {"heading": "Small Cap — High Risk High Reward"},
            {"heading": "Apne Portfolio Mein Kitna Kitna Rakhein"},
        ],
    },
    {
        "week": 7,
        "title": "Mutual Funds vs Direct Stocks",
        "title_en": "Mutual Funds vs Direct Stock Investing",
        "category": "Foundations",
        "level": "Beginner",
        "description": "Complete comparison — which is better for beginners and why",
        "target_audience": "Beginners deciding how to start investing",
        "slides": [
            {"heading": "Mutual Fund Kaise Kaam Karta Hai"},
            {"heading": "Direct Stock Investment — Control Aapke Haath Mein"},
            {"heading": "Expense Ratio — Jo Baat Koi Nahi Batata"},
            {"heading": "Kab Mutual Fund Better Hai Kab Stock Better"},
            {"heading": "Index Fund — Sabse Simple Sabse Powerful"},
        ],
    },
    {
        "week": 8,
        "title": "SIP — Systematic Investment Plan Ka Jaadu",
        "title_en": "SIP — The Magic of Systematic Investment",
        "category": "Foundations",
        "level": "Beginner",
        "description": "How SIP works, rupee cost averaging, and power of compounding",
        "target_audience": "Salaried professionals wanting to invest monthly",
        "slides": [
            {"heading": "SIP Kya Hai Aur Kaise Shuru Karein"},
            {"heading": "Rupee Cost Averaging — Market Timing Ki Zaroorat Nahi"},
            {"heading": "Compounding — Ek Baar Samjho, Zindagi Badal Jaayegi"},
            {"heading": "SIP Calculator — Apna Target Calculate Karein"},
            {"heading": "Common SIP Mistakes Jo Sabse Zyada Log Karte Hain"},
        ],
    },

    # ── PHASE 2: TECHNICAL ANALYSIS (Weeks 9-16) ──────────────────────────────
    {
        "week": 9,
        "title": "Chart Padhna Seekhein — Beginners Guide",
        "title_en": "How to Read Stock Charts — Beginners Guide",
        "category": "Technical Analysis",
        "level": "Beginner",
        "description": "Line chart, bar chart, candlestick chart — which to use and why",
        "target_audience": "Beginners starting technical analysis",
        "slides": [
            {"heading": "Chart Kyon Zaroori Hai"},
            {"heading": "Line Chart vs Bar Chart vs Candlestick"},
            {"heading": "Time Frame — Daily Weekly Monthly"},
            {"heading": "Volume — Price Ka Confirmation"},
            {"heading": "TradingView Par Chart Kaise Dekhein"},
        ],
    },
    {
        "week": 10,
        "title": "Candlestick Patterns — 5 Jo Kaam Aate Hain",
        "title_en": "Candlestick Patterns — 5 That Actually Work",
        "category": "Technical Analysis",
        "level": "Beginner",
        "description": "Most reliable candlestick patterns with real Indian stock examples",
        "target_audience": "Beginners who have learned to read charts",
        "slides": [
            {"heading": "Candlestick Kya Batata Hai"},
            {"heading": "Bullish Engulfing — FII Buying Ka Signal"},
            {"heading": "Pin Bar — Strong Rejection Pattern"},
            {"heading": "Doji — Decision Point"},
            {"heading": "Inside Bar — Breakout Ki Taiyaari"},
        ],
    },
    {
        "week": 11,
        "title": "Support and Resistance — Drawing Levels Correctly",
        "title_en": "Support and Resistance — Drawing Levels That Work",
        "category": "Technical Analysis",
        "level": "Beginner",
        "description": "How to identify and draw correct support/resistance zones",
        "target_audience": "Beginners learning chart analysis",
        "slides": [
            {"heading": "Support Kya Hai Aur Kyon Hold Karta Hai"},
            {"heading": "Resistance Kya Hai Aur Kyon Rok Deta Hai"},
            {"heading": "Levels Correctly Kaise Draw Karein"},
            {"heading": "Role Reversal — Sabse Powerful Concept"},
            {"heading": "Breakout Entry — Kab Aur Kaise"},
        ],
    },
    {
        "week": 12,
        "title": "Moving Averages — 9, 21, 50, 200 EMA",
        "title_en": "Moving Averages — 9, 21, 50, 200 EMA Explained",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "How moving averages work and how AI360 system uses them",
        "target_audience": "Intermediate traders learning trend analysis",
        "slides": [
            {"heading": "Moving Average Kya Hoti Hai"},
            {"heading": "SMA vs EMA — Kya Fark Hai"},
            {"heading": "9 EMA — Short Term Momentum"},
            {"heading": "50 aur 200 EMA — Trend Direction"},
            {"heading": "Golden Cross aur Death Cross"},
        ],
    },
    {
        "week": 13,
        "title": "RSI — Overbought Oversold Sahi Tarike Se Samjhein",
        "title_en": "RSI — Using Overbought and Oversold Correctly",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "RSI indicator — common mistakes and correct usage",
        "target_audience": "Traders who know basic charts",
        "slides": [
            {"heading": "RSI Kya Measure Karta Hai"},
            {"heading": "RSI 30 70 Rule — Kyun Akela Kafi Nahi"},
            {"heading": "RSI Divergence — Most Powerful Signal"},
            {"heading": "AI360 Mein RSI Kaise Use Hota Hai"},
            {"heading": "RSI Entry Filter — Galat Stocks Se Bachein"},
        ],
    },
    {
        "week": 14,
        "title": "MACD — Trend Following Ka Best Tool",
        "title_en": "MACD — The Best Trend Following Indicator",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "MACD crossover, histogram, divergence with real examples",
        "target_audience": "Traders learning momentum indicators",
        "slides": [
            {"heading": "MACD Kya Hai Aur Kaise Kaam Karta Hai"},
            {"heading": "Signal Line Crossover — Entry Signal"},
            {"heading": "Histogram — Momentum Ka Measurement"},
            {"heading": "MACD Divergence — Reversal Ka Warning"},
            {"heading": "MACD + EMA Combination — Powerful Setup"},
        ],
    },
    {
        "week": 15,
        "title": "Volume Analysis — Smart Money Kahaan Ja Raha Hai",
        "title_en": "Volume Analysis — Tracking Smart Money",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "Volume is the truth behind price — how to read it correctly",
        "target_audience": "Traders wanting to understand institutional moves",
        "slides": [
            {"heading": "Volume Kyon Price Se Important Hai"},
            {"heading": "High Volume Breakout vs Low Volume Breakout"},
            {"heading": "Volume Divergence — Warning Signal"},
            {"heading": "OBV — On Balance Volume Indicator"},
            {"heading": "FII DII Data Se Volume Analysis"},
        ],
    },
    {
        "week": 16,
        "title": "Trend Analysis — Uptrend Downtrend Sideways",
        "title_en": "Trend Analysis — Identifying Market Direction",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "description": "How to identify trend, trade with trend, and avoid counter-trend traps",
        "target_audience": "Traders who know indicators and want to improve entries",
        "slides": [
            {"heading": "Trend Kya Hoti Hai — Higher Highs Higher Lows"},
            {"heading": "Uptrend Mein Kaise Trade Karein"},
            {"heading": "Downtrend Mein Kya Karein"},
            {"heading": "Sideways Market — Most Traders Ka Trap"},
            {"heading": "Trend Change Kaise Identify Karein"},
        ],
    },

    # ── PHASE 3: FUNDAMENTAL ANALYSIS (Weeks 17-24) ───────────────────────────
    {
        "week": 17,
        "title": "Fundamental Analysis Kya Hai",
        "title_en": "What Is Fundamental Analysis",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "Introduction to fundamental analysis — why business matters more than chart",
        "target_audience": "Traders wanting to add fundamentals to their analysis",
        "slides": [
            {"heading": "Technical vs Fundamental — Dono Zaroori Hain"},
            {"heading": "Balance Sheet — Company Ki Health Report"},
            {"heading": "P&L Statement — Profit Kaisa Aa Raha Hai"},
            {"heading": "Cash Flow Statement — Cash King Hai"},
            {"heading": "Where to Find Annual Reports — Free Sources"},
        ],
    },
    {
        "week": 18,
        "title": "P/E Ratio — Stock Sasta Hai Ya Mahanga",
        "title_en": "P/E Ratio — Is the Stock Cheap or Expensive",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "Price to Earnings ratio — how to use it correctly and its limitations",
        "target_audience": "Investors wanting to evaluate stock valuations",
        "slides": [
            {"heading": "P/E Ratio Kya Hota Hai"},
            {"heading": "High P/E vs Low P/E — Kya Sochein"},
            {"heading": "Sector Comparison — P/E Hamesha Relative Hota Hai"},
            {"heading": "PEG Ratio — P/E Ka Better Version"},
            {"heading": "P/E Trap — Jab Sasta Dikhta Hai Aur Hota Nahi"},
        ],
    },
    {
        "week": 19,
        "title": "ROE ROA ROCE — Quality Stocks Kaise Dhundein",
        "title_en": "ROE ROA ROCE — Finding Quality Stocks",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "Return ratios explained — how to identify consistently profitable companies",
        "target_audience": "Investors wanting to find quality long-term stocks",
        "slides": [
            {"heading": "Return Ratios Kyon Matter Karte Hain"},
            {"heading": "ROE — Return on Equity Explained"},
            {"heading": "ROCE — Better Than ROE — Here Is Why"},
            {"heading": "Consistent ROE 15%+ = Quality Business"},
            {"heading": "India Examples — Reliance, TCS, HDFC Bank ROE"},
        ],
    },
    {
        "week": 20,
        "title": "Debt Analysis — Kitna Karz Hai Company Par",
        "title_en": "Debt Analysis — How Much Debt Is Too Much",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "Debt-to-equity ratio, interest coverage, and why debt kills companies",
        "target_audience": "Investors wanting to avoid highly leveraged companies",
        "slides": [
            {"heading": "Debt-to-Equity Ratio — Basic Calculation"},
            {"heading": "Interest Coverage Ratio — Can Company Pay Interest"},
            {"heading": "Kaunsi Industry Mein Zyada Debt Normal Hai"},
            {"heading": "Debt Trap — Warning Signs"},
            {"heading": "Zero Debt Companies — Are They Always Better"},
        ],
    },
    {
        "week": 21,
        "title": "Sector Analysis — Sahi Sector Mein Invest Karein",
        "title_en": "Sector Analysis — Investing in the Right Sector",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "Business cycles, sector rotation, and which sectors to focus on when",
        "target_audience": "Investors wanting sector-based stock selection",
        "slides": [
            {"heading": "India Ke Top Sectors — Overview"},
            {"heading": "Sector Rotation — Economy Cycle Se Connect"},
            {"heading": "Tailwind Sectors — Ek Baar Samjho"},
            {"heading": "FII Kis Sector Mein Invest Kar Rahi Hai"},
            {"heading": "AI360 System Mein Sector Filter Kaise Kaam Karta Hai"},
        ],
    },
    {
        "week": 22,
        "title": "Management Quality — Promoter Ko Kaise Samjhein",
        "title_en": "Management Quality — Understanding Promoters",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "description": "Promoter holding, pledging, governance — how to evaluate company leadership",
        "target_audience": "Investors wanting to pick trustworthy companies",
        "slides": [
            {"heading": "Management Kyon Company Se Zyada Important Hai"},
            {"heading": "Promoter Holding — Kitna Hona Chahiye"},
            {"heading": "Promoter Pledging — Red Flag Hai"},
            {"heading": "Corporate Governance Score Check Karein"},
            {"heading": "Good Management Examples — India Mein"},
        ],
    },
    {
        "week": 23,
        "title": "Competitive Moat — Wide Moat Stocks Kaise Dhundein",
        "title_en": "Competitive Moat — Finding Wide Moat Stocks",
        "category": "Fundamental Analysis",
        "level": "Advanced",
        "description": "Warren Buffett's moat concept applied to Indian stocks",
        "target_audience": "Investors wanting to hold stocks for 5-10 years",
        "slides": [
            {"heading": "Moat Kya Hota Hai — Warren Buffett Ka Concept"},
            {"heading": "5 Types of Moats — Network Brand Cost Switching Scale"},
            {"heading": "India Mein Wide Moat Stocks Ke Examples"},
            {"heading": "Moat Kitne Saalo Tak Tika Reh Sakta Hai"},
            {"heading": "Moat Wala Stock Kab Khareedein Kab Nahi"},
        ],
    },
    {
        "week": 24,
        "title": "Valuation — Fair Value Kaise Calculate Karein",
        "title_en": "Valuation — How to Calculate Fair Value",
        "category": "Fundamental Analysis",
        "level": "Advanced",
        "description": "DCF, Graham number, earnings-based valuation — simple approach",
        "target_audience": "Investors wanting to calculate intrinsic value of stocks",
        "slides": [
            {"heading": "Valuation Kyon Zaroori Hai"},
            {"heading": "P/E Based Valuation — Simple Method"},
            {"heading": "Graham Number — Value Investing Formula"},
            {"heading": "DCF — Discounted Cash Flow Simplified"},
            {"heading": "Margin of Safety — Galti Ka Kaafi Room Rakhein"},
        ],
    },

    # ── PHASE 4: TRADING STRATEGIES (Weeks 25-32) ─────────────────────────────
    {
        "week": 25,
        "title": "Swing Trading — Ek Week Mein 5-10% Kaise Kamayein",
        "title_en": "Swing Trading — How to Make 5-10% in One Week",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "Complete swing trading system — entry, exit, SL, target, position sizing",
        "target_audience": "Working professionals wanting to swing trade",
        "slides": [
            {"heading": "Swing Trading vs Intraday vs Positional"},
            {"heading": "Best Timeframe for Swing Trading — Daily + 4Hr"},
            {"heading": "Entry Criteria — 3 Must-Haves Before Entering"},
            {"heading": "Stop Loss Placement — ATR Method"},
            {"heading": "Target Setting — RR Minimum 1:2"},
        ],
    },
    {
        "week": 26,
        "title": "Positional Trading — Hold Karo 1-3 Mahine",
        "title_en": "Positional Trading — Hold for 1-3 Months",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "Positional trading strategy using fundamentals + technicals together",
        "target_audience": "Investors wanting medium-term returns",
        "slides": [
            {"heading": "Positional Trading Kya Hota Hai"},
            {"heading": "Stock Selection — Fundamental + Technical Filter"},
            {"heading": "Entry Point — Weekly Chart Se"},
            {"heading": "Trailing Stop Loss — Profit Ko Protect Karein"},
            {"heading": "When to Exit Early — News Events"},
        ],
    },
    {
        "week": 27,
        "title": "Momentum Trading — Moving Stocks Ke Saath Chalo",
        "title_en": "Momentum Trading — Ride the Moving Stocks",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "Momentum investing — buy strength, sell weakness",
        "target_audience": "Traders wanting to capture strong trending moves",
        "slides": [
            {"heading": "Momentum Kya Hai — Fizik Ka Law Markets Mein"},
            {"heading": "RS Relative Strength — Market Se Zyada Chalne Wale Stocks"},
            {"heading": "VCP Pattern — Volatility Contraction Before Breakout"},
            {"heading": "Entry Timing — Volume Confirm Kare Toh Enter"},
            {"heading": "Momentum Ka Life Cycle — Kab Khatam Hota Hai"},
        ],
    },
    {
        "week": 28,
        "title": "Breakout Trading — Naya High Banane Par Khareedein",
        "title_en": "Breakout Trading — Buying at New Highs",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "How to trade breakouts correctly — avoiding false breakouts",
        "target_audience": "Traders wanting momentum-based entries",
        "slides": [
            {"heading": "Breakout Kya Hota Hai"},
            {"heading": "True Breakout vs False Breakout — Difference"},
            {"heading": "Volume Confirmation — Non-Negotiable"},
            {"heading": "Entry After Confirmation — Not Before"},
            {"heading": "Stop Loss and Target For Breakout Trades"},
        ],
    },
    {
        "week": 29,
        "title": "Base Entry — Sabse Kum Risk Ka Entry Point",
        "title_en": "Base Entry — The Lowest Risk Entry Point",
        "category": "Trading Strategies",
        "level": "Advanced",
        "description": "How AI360 system identifies base entries before breakout",
        "target_audience": "Traders wanting to enter before the crowd",
        "slides": [
            {"heading": "Base Entry Kya Hai"},
            {"heading": "Accumulation Zone — FII Khareed Rahi Hai"},
            {"heading": "VCP Pattern — Tight Base Ki Pehchaan"},
            {"heading": "Entry Timing — DMA Ke Paas"},
            {"heading": "Risk Reward — 1:3+ Easily Possible From Base"},
        ],
    },
    {
        "week": 30,
        "title": "Trailing Stop Loss — Profit Ko Lock Karein",
        "title_en": "Trailing Stop Loss — Locking In Your Profits",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "TSL methods — fixed percentage, ATR-based, how AI360 bot uses TSL",
        "target_audience": "Traders who enter well but exit poorly",
        "slides": [
            {"heading": "Fixed SL vs Trailing SL — Kya Fark Hai"},
            {"heading": "ATR Based Trailing — Most Professional Method"},
            {"heading": "Breakeven Move — Pehla Step"},
            {"heading": "Progressive Locking — Jitna Upar Jaao Utna Lock"},
            {"heading": "AI360 Bot Ka TSL System — Automated"},
        ],
    },
    {
        "week": 31,
        "title": "Intraday Trading — Sach Batata Hoon",
        "title_en": "Intraday Trading — The Honest Truth",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "Intraday trading reality check — who should do it and who should not",
        "target_audience": "People curious about intraday trading",
        "slides": [
            {"heading": "Intraday Trading Reality — 90% Lose Money"},
            {"heading": "Kab Intraday Sahi Hai"},
            {"heading": "Best Intraday Stocks India 2026"},
            {"heading": "Intraday Setup — Gap and Go Strategy"},
            {"heading": "Intraday Rules — 5 Non-Negotiable"},
        ],
    },
    {
        "week": 32,
        "title": "Portfolio Building — Balanced Portfolio Kaise Banayein",
        "title_en": "Portfolio Building — Creating a Balanced Portfolio",
        "category": "Trading Strategies",
        "level": "Intermediate",
        "description": "Complete portfolio construction — asset allocation, diversification, review",
        "target_audience": "Investors who want to build a long-term portfolio",
        "slides": [
            {"heading": "Portfolio Kya Hota Hai"},
            {"heading": "Asset Allocation — Stocks Bonds Gold Cash"},
            {"heading": "Diversification — Kaise Sahi Tarike Se Karein"},
            {"heading": "Rebalancing — Kitne Samay Mein"},
            {"heading": "Portfolio Review — Quarterly Zaroor Karein"},
        ],
    },

    # ── PHASE 5: OPTIONS & DERIVATIVES (Weeks 33-40) ──────────────────────────
    {
        "week": 33,
        "title": "Options Introduction — Call Put Basics",
        "title_en": "Options Introduction — Call and Put Basics",
        "category": "Options",
        "level": "Beginner",
        "description": "First introduction to options for those who have learned stocks",
        "target_audience": "Stock investors curious about options",
        "slides": [
            {"heading": "Option Contract Kya Hota Hai"},
            {"heading": "Call Option — Buy Karne Ka Right"},
            {"heading": "Put Option — Sell Karne Ka Right"},
            {"heading": "Premium Kya Hota Hai"},
            {"heading": "Maximum Loss — Sirf Premium Tak Limited"},
        ],
    },
    {
        "week": 34,
        "title": "Options Greeks — Delta Theta Vega",
        "title_en": "Options Greeks — Delta Theta Vega Simply Explained",
        "category": "Options",
        "level": "Intermediate",
        "description": "Options Greeks explained simply with Indian market examples",
        "target_audience": "Traders who understand basic options",
        "slides": [
            {"heading": "Greeks Kyon Zaroori Hain"},
            {"heading": "Delta — Directional Exposure"},
            {"heading": "Theta — Har Din Ka Nuksan"},
            {"heading": "Vega — Volatility Ka Effect"},
            {"heading": "Greeks Ko Practice Kaise Karein"},
        ],
    },
    {
        "week": 35,
        "title": "Option Buying Strategy — CE PE Kab Khareedein",
        "title_en": "Option Buying Strategy — When to Buy CE and PE",
        "category": "Options",
        "level": "Intermediate",
        "description": "Directional option buying — right time, right strike, right expiry",
        "target_audience": "Traders wanting to buy options profitably",
        "slides": [
            {"heading": "Option Buying Mein 3 Cheezein Sahi Karni Hain"},
            {"heading": "Strike Selection — ATM OTM ITM"},
            {"heading": "Expiry Selection — Weekly vs Monthly"},
            {"heading": "VIX Check — Kab Buy Karna Theek Hai"},
            {"heading": "Stop Loss and Exit Rules"},
        ],
    },
    {
        "week": 36,
        "title": "Option Selling — Consistent Income Strategy",
        "title_en": "Option Selling — Generating Consistent Income",
        "category": "Options",
        "level": "Advanced",
        "description": "Option selling strategies — covered call, cash secured put, spreads",
        "target_audience": "Advanced traders with capital for margin",
        "slides": [
            {"heading": "Option Sellers Kyun Long Term Mein Jeette Hain"},
            {"heading": "Covered Call — Monthly Income Stocks Se"},
            {"heading": "Cash Secured Put — Stock Discount Par Khareedein"},
            {"heading": "Bull Put Spread — Limited Risk Selling"},
            {"heading": "Risk Management — Non-Negotiable Rules"},
        ],
    },
    {
        "week": 37,
        "title": "Nifty Weekly Expiry Strategy",
        "title_en": "Nifty Weekly Expiry Trading Strategy",
        "category": "Options",
        "level": "Intermediate",
        "description": "Thursday expiry trading — max pain, entry time, exit rules",
        "target_audience": "Traders who want to trade every Thursday",
        "slides": [
            {"heading": "Thursday Kyon Important Hai"},
            {"heading": "Max Pain Kya Hai Aur Kaise Use Karein"},
            {"heading": "Expiry Day Entry — 10 AM Ke Baad"},
            {"heading": "Same Day Exit — Compulsory Rule"},
            {"heading": "Last 30 Minutes — Kabhi Mat Pakdein"},
        ],
    },
    {
        "week": 38,
        "title": "India VIX — Fear Ka Indicator",
        "title_en": "India VIX — The Fear Indicator Explained",
        "category": "Options",
        "level": "Intermediate",
        "description": "India VIX — what it is, how to use it for options decisions",
        "target_audience": "Options traders wanting better timing",
        "slides": [
            {"heading": "VIX Kya Measure Karta Hai"},
            {"heading": "VIX High — Options Mehnge Hote Hain"},
            {"heading": "VIX Low — Options Saste Hote Hain"},
            {"heading": "VIX 15-18 — Best Zone for Option Buyers"},
            {"heading": "AI360 System Mein VIX Filter"},
        ],
    },
    {
        "week": 39,
        "title": "F&O Ban List — Kya Hota Hai Aur Kyun",
        "title_en": "F&O Ban List — What It Is and Why It Matters",
        "category": "Options",
        "level": "Intermediate",
        "description": "SEBI F&O ban, open interest limits, what to do when stock is banned",
        "target_audience": "F&O traders wanting to avoid banned stocks",
        "slides": [
            {"heading": "F&O Ban Kya Hota Hai"},
            {"heading": "Open Interest Limit Se Ban Kab Hota Hai"},
            {"heading": "Ban Mein Kya Kar Sakte Hain Kya Nahi"},
            {"heading": "Ban Se Pehle Warning Signs"},
            {"heading": "Ban List Kahan Dekhein — NSE Website Free"},
        ],
    },
    {
        "week": 40,
        "title": "Futures Trading — Basics Aur Risk",
        "title_en": "Futures Trading — Basics and Risks",
        "category": "Options",
        "level": "Advanced",
        "description": "Futures contracts — leverage, margin, rollover, and dangers",
        "target_audience": "Advanced traders considering futures",
        "slides": [
            {"heading": "Futures Contract Kya Hota Hai"},
            {"heading": "Leverage — Opportunity Aur Danger Dono"},
            {"heading": "Margin Call — Jab Account Saaf Ho Jaata Hai"},
            {"heading": "Rollover — Contract Extend Karna"},
            {"heading": "Futures vs Options — Kab Kya Better"},
        ],
    },

    # ── PHASE 6: RISK & WEALTH MANAGEMENT (Weeks 41-48) ──────────────────────
    {
        "week": 41,
        "title": "Position Sizing — Ek Trade Mein Kitna Lagayein",
        "title_en": "Position Sizing — How Much to Risk Per Trade",
        "category": "Risk Management",
        "level": "Intermediate",
        "description": "Position sizing formula, 1% rule, capital allocation per trade",
        "target_audience": "Traders who win trades but still lose money",
        "slides": [
            {"heading": "Position Sizing Kyon Sabse Important Hai"},
            {"heading": "1% Rule — Per Trade Maximum Risk"},
            {"heading": "Kelly Criterion — Mathematical Approach"},
            {"heading": "Capital Tiers — High Medium Standard"},
            {"heading": "AI360 Position Sizing System"},
        ],
    },
    {
        "week": 42,
        "title": "Risk Management — Capital Bachana Pehle",
        "title_en": "Risk Management — Protecting Your Capital First",
        "category": "Risk Management",
        "level": "Intermediate",
        "description": "Complete risk management framework for Indian traders",
        "target_audience": "All traders and investors",
        "slides": [
            {"heading": "Capital Preservation — Rule Number One"},
            {"heading": "Maximum Drawdown — Kitna Lose Karna Theek Hai"},
            {"heading": "Concentration Risk — Ek Jagah Sab Mat Lagao"},
            {"heading": "Sector Concentration — 2 Stocks Per Sector Max"},
            {"heading": "When to Reduce Position — Signals to Watch"},
        ],
    },
    {
        "week": 43,
        "title": "Trading Psychology — Mann Ko Control Karein",
        "title_en": "Trading Psychology — Controlling Your Mind",
        "category": "Psychology",
        "level": "Intermediate",
        "description": "FOMO, revenge trading, overconfidence — how to overcome them",
        "target_audience": "Traders making emotional decisions",
        "slides": [
            {"heading": "90% Traders Kyon Harte Hain — Psychology"},
            {"heading": "FOMO — Fear of Missing Out Ke Against"},
            {"heading": "Revenge Trading — Account Ka Sabse Bada Dushman"},
            {"heading": "Overconfidence — Winning Streak Ke Baad"},
            {"heading": "Trading Journal — Discipline Ka Secret Weapon"},
        ],
    },
    {
        "week": 44,
        "title": "Personal Finance — Savings Investment Insurance",
        "title_en": "Personal Finance — Savings Investment Insurance",
        "category": "Personal Finance",
        "level": "Beginner",
        "description": "Emergency fund, term insurance, health insurance before investing",
        "target_audience": "Anyone wanting to organize their finances",
        "slides": [
            {"heading": "Invest Karne Se Pehle Yeh Karo"},
            {"heading": "Emergency Fund — 6 Mahine Ka Kharcha"},
            {"heading": "Term Insurance — Sabse Zaroori Cheez"},
            {"heading": "Health Insurance — Second Most Important"},
            {"heading": "Invest Karne Ki Sahi Order"},
        ],
    },
    {
        "week": 45,
        "title": "Tax Planning — Trading Income Par Tax Kaise Bachayein",
        "title_en": "Tax Planning — Reducing Tax on Trading Income",
        "category": "Personal Finance",
        "level": "Intermediate",
        "description": "STCG, LTCG, tax loss harvesting — legally reducing trading taxes",
        "target_audience": "Traders and investors wanting tax efficiency",
        "slides": [
            {"heading": "Trading Income Par Kitna Tax Lagta Hai"},
            {"heading": "STCG vs LTCG — Fark Samjhein"},
            {"heading": "Tax Loss Harvesting — Legal Tax Bachane Ka Tarika"},
            {"heading": "F&O Income — Business Income Ki Tarah"},
            {"heading": "CA Se Kab Milein Aur Kaise Milein"},
        ],
    },
    {
        "week": 46,
        "title": "Inflation — Apna Paisa Protect Karo",
        "title_en": "Inflation — Protecting Your Money's Value",
        "category": "Personal Finance",
        "level": "Beginner",
        "description": "Inflation impact on savings, how stocks beat inflation long term",
        "target_audience": "Savers who keep money in FDs and savings accounts",
        "slides": [
            {"heading": "Inflation Kya Hai — Simple Example"},
            {"heading": "FD Mein Paisa — Inflation Se Nahi Bachata"},
            {"heading": "Stocks — Best Inflation Beater Historically"},
            {"heading": "Gold — Real Inflation Hedge"},
            {"heading": "Real Return — Inflation Adjust Karke Calculate"},
        ],
    },
    {
        "week": 47,
        "title": "Retirement Planning — Kitna Chahiye Aapko",
        "title_en": "Retirement Planning — How Much Do You Need",
        "category": "Personal Finance",
        "level": "Intermediate",
        "description": "Retirement corpus calculation, NPS, EPF, SWP strategy",
        "target_audience": "Working professionals thinking about retirement",
        "slides": [
            {"heading": "Retirement Corpus Kaise Calculate Karein"},
            {"heading": "NPS — National Pension Scheme Worth It"},
            {"heading": "EPF — Company Contribution Ka Faida Uthao"},
            {"heading": "SWP — Systematic Withdrawal After Retirement"},
            {"heading": "4% Rule — Global Retirement Standard"},
        ],
    },
    {
        "week": 48,
        "title": "Global Investing — USA Stocks India Se Kaise Khareedein",
        "title_en": "Global Investing — How to Buy USA Stocks From India",
        "category": "Personal Finance",
        "level": "Intermediate",
        "description": "LRS route, platforms, tax implications of global investing from India",
        "target_audience": "Indian investors wanting international diversification",
        "slides": [
            {"heading": "India Se Videsh Mein Invest Karna Legal Hai"},
            {"heading": "LRS Route — 250000 Dollar Per Year Allowed"},
            {"heading": "Platforms — Vested, INDmoney, Interactive Brokers"},
            {"heading": "Tax — India Mein Kya Dena Padta Hai"},
            {"heading": "Best US ETFs for Indian Investors"},
        ],
    },

    # ── PHASE 7: ADVANCED & REVIEW (Weeks 49-52) ──────────────────────────────
    {
        "week": 49,
        "title": "Algorithmic Trading — Bot Se Trade Karein",
        "title_en": "Algorithmic Trading — Trading With Bots",
        "category": "Advanced",
        "level": "Advanced",
        "description": "Algo trading basics, backtesting, API trading, AI360 system overview",
        "target_audience": "Tech-savvy traders wanting automation",
        "slides": [
            {"heading": "Algo Trading Kya Hai"},
            {"heading": "Backtesting — Strategy Ko Test Karo Pehle"},
            {"heading": "Python Se Trading Bot Kaise Banate Hain"},
            {"heading": "AI360 Trading System — Hamara Automated Approach"},
            {"heading": "Algo Trading Ke Risks Aur Limitations"},
        ],
    },
    {
        "week": 50,
        "title": "Global Markets — USA UK Brazil Se Kya Seekhein",
        "title_en": "Global Markets — Learning From USA UK Brazil",
        "category": "Advanced",
        "level": "Advanced",
        "description": "How global market correlations affect Indian stocks",
        "target_audience": "Advanced traders wanting macro understanding",
        "slides": [
            {"heading": "India Market Aur Global Connection"},
            {"heading": "US Market Girta Hai Toh India Kyun Girta Hai"},
            {"heading": "FII — Foreign Money Ka India Effect"},
            {"heading": "Dollar Index — DXY Ka Indian Market Par Asar"},
            {"heading": "Global Opportunities — Beyond India"},
        ],
    },
    {
        "week": 51,
        "title": "Complete Trading Plan Banayein",
        "title_en": "Build Your Complete Trading Plan",
        "category": "Advanced",
        "level": "Advanced",
        "description": "Complete trading plan — rules, journal, review system, goals",
        "target_audience": "All traders wanting a systematic approach",
        "slides": [
            {"heading": "Trading Plan Kyon Zaroori Hai"},
            {"heading": "Entry Rules — Black and White Likhein"},
            {"heading": "Exit Rules — Both Profit and Loss"},
            {"heading": "Daily Weekly Monthly Review System"},
            {"heading": "Goals — Realistic Expectations Set Karein"},
        ],
    },
    {
        "week": 52,
        "title": "Course Complete — Aage Kya Karein",
        "title_en": "Course Complete — What to Do Next",
        "category": "Advanced",
        "level": "Advanced",
        "description": "52-week course review, next steps, and AI360 membership benefits",
        "target_audience": "All students who completed the course",
        "slides": [
            {"heading": "52 Weeks Mein Aapne Kya Seekha"},
            {"heading": "Paper Trading Se Live Trading Ka Safar"},
            {"heading": "AI360 Premium — Live Signals Ke Saath Trade"},
            {"heading": "Community — Saath Milke Seekhein"},
            {"heading": "Aapka Agle 52 Hafte Ka Plan"},
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════
# MONDAY — OPTIONS & DERIVATIVES (for articles and reels)
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
            "what happens if I buy a call option and it expires",
            "options trading vs stock trading which is better for beginners India",
        ],
        "affiliate_angle": "open trading account to start options — Zerodha, Dhan",
        "slides": [
            {"heading": "What is an Option Contract?",
             "points": ["Right but not obligation to buy or sell",
                        "Call option = right to BUY at a fixed price",
                        "Put option = right to SELL at a fixed price",
                        "Premium = price you pay for this right",
                        "Maximum loss always limited to premium paid"]},
            {"heading": "How Call Options Make Money",
             "points": ["Buy call when you think price will rise",
                        "Nifty at 22000 buy 22200 call at Rs.50 premium",
                        "If Nifty rises to 22500 call may be worth Rs.300 — 6x return",
                        "If Nifty stays below 22200 — you lose only the Rs.50 premium",
                        "Options give leverage without borrowing money"]},
            {"heading": "The 3 Rules Every Option Buyer Must Know",
             "points": ["Time decay is your enemy — options lose value every day",
                        "Always buy options with at least 15-20 days to expiry",
                        "Exit winners at 50-100% profit — greed kills options trades",
                        "Stop loss at 40-50% of premium — no exceptions",
                        "Weekly options have highest risk and highest theta decay"]},
        ],
    },
    {
        "title": "Option Selling — Collect Premium Like Insurance Companies",
        "category": "Options",
        "level": "Intermediate",
        "target_primary": "India",
        "target_secondary": ["USA", "UK"],
        "seo_seed": "option selling strategy India monthly income 2026",
        "long_tail_keywords": [
            "how to earn monthly income from option selling Nifty",
            "covered call strategy India step by step 2026",
            "iron condor Nifty strategy explained in Hindi",
        ],
        "affiliate_angle": "Zerodha Sensibull for option strategy builder — free plan available",
        "slides": [
            {"heading": "Why Option Sellers Win Long Term",
             "points": ["80% of options expire worthless — sellers collect premium",
                        "Time decay works FOR sellers every single day",
                        "Like being the casino — house wins over time",
                        "Warren Buffett sold put options to buy Coca-Cola",
                        "Indian market — Bank Nifty weekly options huge premium"]},
        ],
    },
    {
        "title": "Understanding Greeks — Delta Theta Vega Gamma Made Simple",
        "category": "Options",
        "level": "Advanced",
        "target_primary": "Global",
        "target_secondary": ["India", "USA"],
        "seo_seed": "options Greeks explained simply delta theta vega India 2026",
        "long_tail_keywords": [
            "what is delta in options trading explained in Hindi",
            "theta decay options how much do I lose per day",
        ],
        "affiliate_angle": "Sensibull Greeks calculator free for basic",
        "slides": [
            {"heading": "Why Greeks Are the Secret Language of Options",
             "points": ["Greeks tell you exactly how your option will behave",
                        "Without Greeks you are guessing — with Greeks you calculate",
                        "Same Greeks apply to US SPY and India Nifty identically",
                        "Master these four numbers — trade like an institution"]},
        ],
    },
]

# ══════════════════════════════════════════════════════════════════════
# TUESDAY — TECHNICAL ANALYSIS (for articles and reels)
# ══════════════════════════════════════════════════════════════════════

TUESDAY_TOPICS = [
    {
        "title": "Candlestick Patterns — The 5 That Actually Make Money",
        "category": "Technical Analysis",
        "level": "Beginner",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "UK"],
        "seo_seed": "candlestick patterns that work best stocks crypto Nifty 2026",
        "long_tail_keywords": [
            "which candlestick pattern is most reliable for Nifty trading",
            "bullish engulfing pattern how to trade it correctly",
        ],
        "affiliate_angle": "TradingView free plan for chart analysis",
        "slides": [
            {"heading": "The 5 Candlestick Patterns Worth Your Time",
             "points": ["Most traders memorise 50 patterns — professionals focus on 5",
                        "These 5 work consistently on Nifty S&P 500 Bitcoin Forex",
                        "A pattern is only useful with support resistance and volume"]},
            {"heading": "Bullish Engulfing — Institutions Stepping In",
             "points": ["Second candle completely swallows the first red candle",
                        "Buyers overwhelmed sellers completely in one session",
                        "Most powerful at major support levels after strong downtrend"]},
        ],
    },
    {
        "title": "RSI Complete Guide — How to Actually Use It Profitably",
        "category": "Technical Analysis",
        "level": "Intermediate",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "Brazil"],
        "seo_seed": "RSI indicator how to use correctly profitable trading strategy 2026",
        "long_tail_keywords": [
            "RSI divergence strategy stocks India explained step by step",
            "how to use RSI 14 correctly for swing trading",
        ],
        "affiliate_angle": "TradingView for RSI charting — free plan",
        "slides": [
            {"heading": "RSI Overbought Oversold — Most Misunderstood Concept",
             "points": ["RSI above 70 does not always mean sell",
                        "Trending stocks stay overbought for weeks",
                        "RSI divergence is far more reliable than levels"]},
        ],
    },
]

# ══════════════════════════════════════════════════════════════════════
# WEDNESDAY — FUNDAMENTAL + MACRO (for articles and reels)
# ══════════════════════════════════════════════════════════════════════

WEDNESDAY_TOPICS = [
    {
        "title": "P/E Ratio — Is This Stock Cheap or Expensive",
        "category": "Fundamental Analysis",
        "level": "Beginner",
        "target_primary": "Global",
        "target_secondary": ["India", "USA"],
        "seo_seed": "PE ratio how to use correctly stock valuation India 2026",
        "long_tail_keywords": [
            "what is a good PE ratio for Indian stocks",
            "PE ratio trap how to avoid overpaying for stocks India",
        ],
        "affiliate_angle": "Screener.in free stock analysis tool India",
        "slides": [
            {"heading": "PE Ratio — The Most Misused Number in Investing",
             "points": ["PE tells you how much you pay for every Rs.1 of earnings",
                        "A high PE is not always bad — depends on growth rate",
                        "Always compare PE within the same sector — never across sectors"]},
        ],
    },
    {
        "title": "FII DII Data — How Smart Money Moves Indian Markets",
        "category": "Fundamental Analysis",
        "level": "Intermediate",
        "target_primary": "India",
        "target_secondary": ["Global"],
        "seo_seed": "FII DII buying selling data how to use for stock market India",
        "long_tail_keywords": [
            "how to track FII buying and selling in Indian market",
            "FII selling causes market to fall India explained",
        ],
        "affiliate_angle": "NSEIndia.com for free FII DII daily data",
        "slides": [
            {"heading": "FII vs DII — Who Has More Influence",
             "points": ["FII = Foreign Institutional Investors — global funds",
                        "DII = Domestic Institutional Investors — LIC MFs",
                        "FII moves are more volatile and cause larger swings"]},
        ],
    },
]

# ══════════════════════════════════════════════════════════════════════
# THURSDAY — STRATEGIES + PERSONAL FINANCE (for articles and reels)
# ══════════════════════════════════════════════════════════════════════

THURSDAY_TOPICS = [
    {
        "title": "Swing Trading Strategy — How to Make 5-10% in a Week",
        "category": "Strategies",
        "level": "Intermediate",
        "target_primary": "India",
        "target_secondary": ["USA", "UK"],
        "seo_seed": "swing trading strategy India 2026 5 to 10 percent weekly",
        "long_tail_keywords": [
            "how to swing trade Nifty 200 stocks for 5 percent profit",
            "swing trading rules stop loss target India 2026",
        ],
        "affiliate_angle": "AI360 Advance membership for daily swing trade signals",
        "slides": [
            {"heading": "Swing Trading Mein Kya Chahiye",
             "points": ["Good stock with strong fundamental backing",
                        "Technical breakout or base entry point",
                        "Clear SL at 2xATR and Target at 4xATR minimum",
                        "Patience to hold 3-7 days without checking every minute"]},
        ],
    },
    {
        "title": "LIC vs Term Insurance — Which One Should You Buy",
        "category": "Personal Finance",
        "level": "Beginner",
        "target_primary": "India",
        "target_secondary": ["UAE"],
        "seo_seed": "LIC endowment vs term insurance which is better India 2026",
        "long_tail_keywords": [
            "why term insurance is better than LIC endowment plan India",
            "LIC policy surrender value calculator should I stop paying premium",
        ],
        "affiliate_angle": "Policybazaar term insurance comparison — free",
        "slides": [
            {"heading": "Term Insurance vs LIC Endowment — The Real Math",
             "points": ["Term: Rs.1 crore cover for Rs.10000-15000 per year",
                        "LIC endowment: Rs.50 lakh cover for Rs.60000 per year",
                        "Difference invested in index fund = 10x more at retirement"]},
        ],
    },
]

# ══════════════════════════════════════════════════════════════════════
# FRIDAY — PSYCHOLOGY + RISK (for articles and reels)
# ══════════════════════════════════════════════════════════════════════

FRIDAY_TOPICS = [
    {
        "title": "Trading Psychology — Why 90% of Traders Fail",
        "category": "Psychology",
        "level": "All Levels",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "UK"],
        "seo_seed": "trading psychology mistakes why traders lose money India 2026",
        "long_tail_keywords": [
            "how to control emotions in trading stocks India",
            "FOMO trading how to avoid missing trades fear",
            "revenge trading how to stop after losing money",
        ],
        "affiliate_angle": "AI360 Telegram — signals remove emotional guesswork",
        "slides": [
            {"heading": "The Real Reason Traders Fail — It Is Not Strategy",
             "points": ["90% of traders lose not because of bad strategy",
                        "They lose because of undisciplined psychology",
                        "FOMO revenge trading overconfidence — these are killers",
                        "System + discipline beats intelligence every single time"]},
        ],
    },
    {
        "title": "Risk Management — Preserve Capital Before Everything",
        "category": "Risk Management",
        "level": "All Levels",
        "target_primary": "Global",
        "target_secondary": ["India", "USA"],
        "seo_seed": "risk management trading capital preservation India 2026",
        "long_tail_keywords": [
            "how much to risk per trade stocks India percentage",
            "position sizing formula for swing trading India",
        ],
        "affiliate_angle": "AI360 system manages risk automatically with TSL",
        "slides": [
            {"heading": "Capital Preservation — The First Job of Every Trader",
             "points": ["You cannot make money if you have lost all your capital",
                        "Never risk more than 1-2% of total capital on any single trade",
                        "This one rule will keep you in the game long enough to learn"]},
        ],
    },
]

# ══════════════════════════════════════════════════════════════════════
# WEEKEND — EVERGREEN + PERSONAL FINANCE (for articles and reels)
# ══════════════════════════════════════════════════════════════════════

WEEKEND_TOPICS = [
    {
        "title": "How to Build Wealth From Zero — Complete Roadmap",
        "category": "Personal Finance",
        "level": "Beginner",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "UAE", "UK"],
        "seo_seed": "how to build wealth from zero salary India step by step 2026",
        "long_tail_keywords": [
            "how to invest on a 30000 salary India 2026 step by step",
            "wealth building roadmap India first investment beginner",
        ],
        "affiliate_angle": "Zerodha account + SIP in index fund — beginner combo",
        "slides": [
            {"heading": "Wealth Building — Step by Step From Zero",
             "points": ["Step 1: Emergency fund — 6 months expenses saved",
                        "Step 2: Term insurance — Rs.1 crore minimum",
                        "Step 3: Health insurance — Rs.10 lakh family floater",
                        "Step 4: Index fund SIP — Rs.5000 per month start",
                        "Step 5: After 1 year — add individual stock positions"]},
        ],
    },
    {
        "title": "Compounding — The 8th Wonder of the World Explained",
        "category": "Personal Finance",
        "level": "Beginner",
        "target_primary": "Global",
        "target_secondary": ["India", "USA", "Brazil"],
        "seo_seed": "power of compounding explained simply wealth building 2026",
        "long_tail_keywords": [
            "compounding interest example India stock market returns",
            "how much money after 20 years of SIP in index fund India",
        ],
        "affiliate_angle": "Start SIP today — any amount — Zerodha Groww",
        "slides": [
            {"heading": "Compounding — Why Einstein Called It 8th Wonder",
             "points": ["Rs.10000 at 12% per year becomes Rs.96000 in 20 years",
                        "Rs.10000 per month SIP at 12% = Rs.1 crore in 20 years",
                        "The secret: start early — time is more valuable than amount"]},
        ],
    },
]

# ══════════════════════════════════════════════════════════════════════
# HOLIDAY — MOTIVATIONAL (for articles and reels)
# ══════════════════════════════════════════════════════════════════════

HOLIDAY_TOPICS = [
    {
        "title": "Market Band Hai — Use Karo Seekhne Ke Liye",
        "category": "Motivation",
        "level": "All Levels",
        "target_primary": "India",
        "target_secondary": ["UAE"],
        "seo_seed": "stock market holiday what to do trading education India",
        "long_tail_keywords": [
            "what to do when stock market is closed India trading holiday",
        ],
        "affiliate_angle": "AI360 education videos — free on YouTube",
        "slides": [
            {"heading": "Market Band Hai — Yeh Time Waste Mat Karo",
             "points": ["Top traders use market holidays for education and review",
                        "Review last month's trades — what worked what did not",
                        "Study one new concept today",
                        "Plan next week's watchlist",
                        "Update your trading journal"]},
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════
# PUBLIC FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def get_todays_topic():
    """
    Returns topic for articles, reels, morning reel — based on day of week.
    This is the ORIGINAL function for non-education content.
    """
    day = datetime.now().weekday()  # 0=Mon, 6=Sun
    day_map = {
        0: MONDAY_TOPICS,
        1: TUESDAY_TOPICS,
        2: WEDNESDAY_TOPICS,
        3: THURSDAY_TOPICS,
        4: FRIDAY_TOPICS,
        5: WEEKEND_TOPICS,
        6: WEEKEND_TOPICS,
    }
    topics = day_map.get(day, MONDAY_TOPICS)
    week_num = (datetime.now().isocalendar()[1])
    idx = week_num % len(topics)
    return topics[idx]


def get_holiday_topic():
    """Returns holiday-specific motivational topic."""
    week_num = datetime.now().isocalendar()[1]
    return HOLIDAY_TOPICS[week_num % len(HOLIDAY_TOPICS)]


def get_todays_education_topic():
    """
    Returns 52-week progressive course topic for education videos.
    v2.1: Auto-calculates week from COURSE_START and returns week number.

    The same topic is used all week (Mon-Sun) and advances next Monday.
    Week 1 = May 15, 2026 | Week 2 = May 22, 2026 | etc.

    Returns dict with "week" key — used by generate_education.py v1.1
    for title: "Topic | Week N | AI360 Trading"
    """
    today = date.today()
    days_since_start = (today - COURSE_START).days
    week_idx = max(0, days_since_start // 7)  # 0-based index
    week_idx = week_idx % len(EDUCATION_COURSE)  # wrap around after 52 weeks

    topic = EDUCATION_COURSE[week_idx].copy()
    # Ensure week number is in the topic dict (it is, but copy() safety)
    topic["week"] = week_idx + 1  # 1-based for display

    print(f"[CALENDAR] Education Week {topic['week']}: {topic['title']}")
    return topic
