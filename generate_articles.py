import os
import pytz
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Timezone Setup
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")

def get_latest_news():
    """Fetches trending Indian & Global market news via Google News RSS for SEO freshness."""
    news_items = []
    # Targeted search for Indian Markets and Global Macro news
    url = "https://news.google.com/rss/search?q=nifty+50+sensex+global+market+news&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        # Pull top 10 headlines to feed the AI
        for item in root.findall('.//item')[:10]:
            title = item.find('title').text
            news_items.append(title)
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return "Standard market update"
    return "\n".join(news_items)

def clean_markdown(text):
    """Ensures Jekyll compatibility by removing AI code block wrappers."""
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text.strip()

def generate_market_post():
    filename = f"{date_str}-market-intelligence.md"
    posts_dir = os.path.join(os.getcwd(), '_posts')
    file_path = os.path.join(posts_dir, filename)

    # 1. FETCH LIVE DATA FOR SEO RANKING
    market_news = get_latest_news()
    
    print(f"Generating Fresh Intelligence Report for {date_str}...")
    
    # 2. DYNAMIC PROMPT INJECTING REAL-TIME HEADLINES
    prompt = (
        f"Today is {date_str}. You are a Senior Market Strategist for AI360Trading.\n\n"
        f"LATEST LIVE NEWS HEADLINES:\n{market_news}\n\n"
        "TASK:\n"
        "Write a high-authority Indian Market Intelligence report. "
        "The content MUST be based on the news headlines provided above to ensure Google treats it as fresh news.\n\n"
        "REQUIRED STRUCTURE:\n"
        "1. FRONTMATTER:\n"
        "---\n"
        "layout: post\n"
        f"title: 'Market Intelligence {date_str} | [Insert Main News Theme Here]'\n"
        "categories: [Market-Update]\n"
        "tags: [nifty50, stock-market-india, global-macro]\n"
        "---\n\n"
        "2. SECTIONS:\n"
        "### ⚡ Market Pulse\n"
        "Analyze the global sentiment based on the provided news (US Tech, Oil, or Currency).\n\n"
        "### 📊 Trading Levels\n"
        "Provide Support/Resistance levels for Nifty and BankNifty based on today's volatility.\n\n"
        "### 🎯 Sector/Stock Spotlight\n"
        "Pick 3 stocks or sectors mentioned in the news that show breakout potential.\n\n"
        "### 🏷️ Trending Hashtags\n"
        "#Nifty50 #BankNifty #StockMarketIndia #Investing #GlobalMacro #TradingStrategy #AI360Trading\n\n"
        "---\n"
        "**Pro Tip:** Check our [Live Dashboards](/#dashboards) for real-time signals."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5, # Balance between factual data and engaging SEO tone
        )
        
        content = clean_markdown(completion.choices[0].message.content)
        
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Full Report Created: {filename}")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")

if __name__ == "__main__":
    generate_market_post()
