import os
import pytz
import requests
import random
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

# Initialize Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")
POSTS_DIR = os.path.join(os.getcwd(), '_posts')

def get_live_news():
    """Scrapes dynamic news to ensure variety and global appeal."""
    # List of different focus areas to prevent daily repetition
    rotational_queries = [
        "NASDAQ+tech+selloff+AI+bubble+Nvidia+earnings",
        "US+Federal+Reserve+interest+rates+inflation+CPI",
        "China+stimulus+Evergrande+property+market+Yuan",
        "Gold+prices+Crude+Oil+geopolitical+risk+War",
        "FTSE+100+UK+economy+Bank+of+England+recession",
        "Bitcoin+ETF+Crypto+regulation+SEC+Blackrock"
    ]
    
    # Select a random query focus each day
    query_focus = random.choice(rotational_queries)
    headlines = []
    url = f"https://news.google.com/rss/search?q={query_focus}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)
        # Mix top news and some random news from the list
        items = root.findall('.//item')
        random.shuffle(items) # Randomize headlines order
        for item in items[:15]:
            headlines.append(item.find('title').text)
    except Exception as e: 
        return f"Trending Global Finance Incident: {date_str}"
    
    return "\n".join(headlines)

def generate_full_report():
    news = get_live_news()
    # Create a more dynamic title for SEO
    dynamic_title = f"{date_str}-global-market-shocker-news-analysis.md"
    file_path = os.path.join(POSTS_DIR, dynamic_title)

    prompt = (
        f"Today's Date: {date_str}. Write a HIGH-ENERGY, viral Market Intelligence Report for ai360trading.in.\n"
        f"IMPORTANT: Focus on a unique 'Incident of the Day' based on these news headlines:\n{news}\n\n"
        "GOAL: Attract worldwide visitors with bold predictions and deep macro analysis.\n\n"
        "STYLE RULES:\n"
        "1. Start with a 'Breaking News' hook.\n"
        "2. Include a section: '🌍 Worldwide Trending Hashtags' with 10 viral tags like #StockMarket #Nvidia etc.\n"
        "3. Use H2/H3 tags. Break down NASDAQ, FTSE, and Asian Markets.\n"
        "4. Include a 'Global Pivot Table' with Support/Resistance levels for top 5 assets.\n\n"
        "IMAGES (Performance Optimized):\n"
        "<img src='https://images.unsplash.com/photo-1611974714013-3c7456ca017a?auto=format&fit=crop&w=800&q=80' width='800' height='450' loading='lazy' alt='Global Market Chart'>\n\n"
        "END WITH THIS EXACT HTML FOOTER:\n"
        '<h3>📢 Share this Analysis</h3>\n'
        '<div class="share-bar">\n'
        '  <a href="https://wa.me/?text={{ page.title }} - {{ site.url }}{{ page.url }}" class="share-btn btn-whatsapp">WhatsApp</a>\n'
        '  <a href="https://twitter.com/intent/tweet?text={{ page.title }}&url={{ site.url }}{{ page.url }}" class="share-btn btn-twitter">Twitter</a>\n'
        '  <a href="https://t.me/share/url?url={{ site.url }}{{ page.url }}&text={{ page.title }}" class="share-btn btn-telegram">Telegram</a>\n'
        '</div>\n\n'
        '<div class="sub-box">\n'
        '  <h3>🚀 Global Trade Signals</h3>\n'
        '  <p>Join our international community for real-time macro alerts.</p>\n'
        '  <a href="https://t.me/{{ site.telegram_username }}">Join Telegram Now</a>\n'
        '</div>'
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a world-class financial journalist. You write uniquely and never repeat yourself."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8, # Increased for more variety
        )
        content = completion.choices[0].message.content
        
        # Ensure directory exists
        if not os.path.exists(POSTS_DIR): os.makedirs(POSTS_DIR)
        
        # Add Jekyll Front Matter (Crucial for Website formatting)
        front_matter = (
            "---\n"
            f"layout: post\n"
            f"title: \"Global Market Intelligence Report: {date_str}\"\n"
            f"date: {date_str}\n"
            "categories: [Market-Intelligence]\n"
            "---\n\n"
        )
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(front_matter + content)
            
        print(f"✅ Success: New Unique Article Generated for {date_str}")
    except Exception as e: 
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_full_report()
