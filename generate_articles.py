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
    """Fetches trending Indian & Global market news via Google News RSS."""
    news_items = []
    # Query for Indian Market and Global Macro news
    url = "https://news.google.com/rss/search?q=nifty+50+sensex+global+market+news&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        for item in root.findall('.//item')[:8]: # Get top 8 news stories
            news_items.append(item.find('title').text)
    except Exception as e:
        print(f"News Fetch Error: {e}")
    return "\n".join(news_items)

def clean_markdown(text):
    """Ensures Jekyll compatibility by removing AI wrappers."""
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text.strip()

def generate_market_post():
    filename = f"{date_str}-market-intelligence.md"
    posts_dir = os.path.join(os.getcwd(), '_posts')
    file_path = os.path.join(posts_dir, filename)

    # FETCH LIVE DATA
    market_news = get_latest_news()
    
    print(f"Generating Fresh Intelligence Report for {date_str}...")
    
    # DYNAMIC PROMPT USING REAL NEWS
    prompt = (
        f"Today is {date_str}. Use these REAL headlines to write a SEO-optimized report:\n\n"
        f"LATEST NEWS:\n{market_news}\n\n"
        "INSTRUCTIONS:\n"
        "1. Write as a Senior Market Strategist.\n"
        "2. Include a 'Click-worthy' title with a specific news event in it.\n"
        "3. Frontmatter: layout: post, categories: [Market-Update], tags: [nifty, global-markets].\n"
        "4. Section: '⚡ Market Pulse' - Analyze the news above.\n"
        "5. Section: '📊 Pivot Levels' - Estimated levels for Nifty, BankNifty.\n"
        "6. Section: '🎯 Breakout Stocks' - Mention 3 stocks from the news headlines.\n"
        "7. Include Trending Hashtags for 2026: #NiftyToday #StockMarketIndia #AI360Trading #MarketNews\n"
        "8. Use Markdown. No intro/outro fluff."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6, # Slightly higher for more creative/trending titles
        )
        
        content = clean_markdown(completion.choices[0].message.content)
        
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Success: Post Created with live news context.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_market_post()
