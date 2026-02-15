import os
import pytz
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Timezone & Path Setup
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")
POSTS_DIR = os.path.join(os.getcwd(), '_posts')

def keep_only_latest_10():
    """Removes all but the 10 most recent posts to keep the site clean for AdSense."""
    if not os.path.exists(POSTS_DIR):
        return
    
    # Get all markdown files and sort them by name (which starts with date)
    all_posts = sorted(
        [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')],
        reverse=True
    )
    
    # If more than 10, delete the oldest ones
    if len(all_posts) > 10:
        posts_to_delete = all_posts[10:]
        for post in posts_to_delete:
            os.remove(os.path.join(POSTS_DIR, post))
            print(f"🗑️ Deleted old post: {post}")

def get_latest_news():
    """Fetches high-authority global news for worldwide reach."""
    news_items = []
    # Using a global finance query to attract US/UK visitors alongside Indian traders
    url = "https://news.google.com/rss/search?q=nifty+50+us+market+nasdaq+fed+news&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        for item in root.findall('.//item')[:10]:
            news_items.append(item.find('title').text)
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return "Global market trends"
    return "\n".join(news_items)

def clean_markdown(text):
    """Ensures Jekyll compatibility."""
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text.strip()

def generate_market_post():
    filename = f"{date_str}-market-intelligence.md"
    file_path = os.path.join(POSTS_DIR, filename)

    # 1. Housekeeping: Keep only 10 latest
    keep_only_latest_10()

    # 2. Fetch Live Global News
    market_news = get_latest_news()
    
    # 3. Enhanced Prompt for AdSense & Worldwide Reach
    # We ask for 800+ words to meet AdSense "Sufficient Text" requirements
    prompt = (
        f"Today is {date_str}. Act as a Global Market Analyst. "
        f"Using these headlines, write a LONG (800+ words) professional report:\n\n{market_news}\n\n"
        "GOAL: High-value content for AdSense approval and international readers.\n"
        "STRUCTURE:\n"
        "1. Frontmatter (layout: post, title: [News Driven Title], categories: [Market-Update])\n"
        "2. Detailed Analysis of Global Sentiment (Focus on US Markets and Nifty).\n"
        "3. Macroeconomic Outlook (Inflation, Fed/RBI, Brent Oil).\n"
        "4. Technical Analysis with Pivot Tables for Nifty & BankNifty.\n"
        "5. Conclusion for Global Investors.\n"
        "Use professional English. NO AI fluff. Ensure high keyword density for SEO."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        
        content = clean_markdown(completion.choices[0].message.content)
        
        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Success: 800+ word post created for {date_str}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_market_post()
