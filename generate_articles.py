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
    """Keeps the site fresh and avoids 'Low Value' archives for AdSense."""
    if not os.path.exists(POSTS_DIR):
        return
    all_posts = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')], reverse=True)
    if len(all_posts) > 10:
        for post in all_posts[10:]:
            os.remove(os.path.join(POSTS_DIR, post))

def get_live_market_context():
    """Fetches high-authority headlines for Nifty and Global Markets."""
    headlines = []
    url = "https://news.google.com/rss/search?q=nifty+50+analysis+fed+rate+hike+global+economy&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        for item in root.findall('.//item')[:12]:
            headlines.append(item.find('title').text)
    except:
        return "Global Market Volatility"
    return "\n".join(headlines)

def clean_markdown(text):
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text.strip()

def generate_premium_report():
    filename = f"{date_str}-global-market-analysis.md"
    file_path = os.path.join(POSTS_DIR, filename)

    keep_only_latest_10()
    news_context = get_live_market_context()

    # THE "HUMAN-AUTHORITY" PROMPT
    prompt = (
        f"Today is {date_str}. Write a 1,200-word Deep-Dive Market Intelligence Report for ai360trading.in.\n\n"
        f"REAL-TIME CONTEXT:\n{news_context}\n\n"
        "WRITING STYLE RULES (FOR ADSENSE APPROVAL):\n"
        "- Tone: Professional, direct, and authoritative (like Financial Times or Bloomberg).\n"
        "- NO AI CLICHES: Do not use 'In the fast-paced world', 'Unlock', 'Delve', or 'Stay tuned'.\n"
        "- Structure: Use short 2-3 sentence paragraphs. Use bold text for key insights.\n\n"
        "REPORT REQUIREMENTS:\n"
        "1. FRONTMATTER: Use 'layout: post', a catchy news-based 'title', and 'categories: [Market-Intelligence]'.\n"
        "2. THE LEAD: Start with a strong opinion on today's market direction based on the news.\n"
        "3. GLOBAL MACRO: Detail how US Bond Yields or Brent Oil are impacting Indian stocks today.\n"
        "4. TECHNICAL PIVOTS: Create a Markdown table for Nifty, BankNifty, and the top 3 trending stocks.\n"
        "5. SECTOR ANALYSIS: Discuss which sectors (IT, PSU Banks, etc.) are overbought or oversold.\n"
        "6. CALL TO ACTION: End with: '> **Don't miss a beat!** Subscribe to our daily Telegram updates and bookmark this page for real-time market signals.'\n"
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        
        content = clean_markdown(completion.choices[0].message.content)
        
        if not os.path.exists(POSTS_DIR): os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Professional Article Generated for {date_str}")
        
    except Exception as e:
        print(f"❌ Generation Error: {e}")

if __name__ == "__main__":
    generate_premium_report()
