import os
import pytz
import re
import requests
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
    """Scrapes Global Macro news for US, UK, and China attraction."""
    headlines = []
    # Targeted search for global high-volume keywords
    query = "US+Fed+Rate+NASDAQ+analysis+FTSE+100+UK+economy+China+stimulus+market"
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)
        for item in root.findall('.//item')[:12]:
            headlines.append(item.find('title').text)
    except: 
        return "Global Market Macro Trends"
    return "\n".join(headlines)

def generate_full_report():
    news = get_live_news()
    filename = f"{date_str}-global-market-intelligence-report.md"
    file_path = os.path.join(POSTS_DIR, filename)

    # SEO Optimized Prompt for Global Reach
    prompt = (
        f"Today: {date_str}. Write a 1,500-word Market Intelligence Report for ai360trading.in.\n"
        f"Context News:\n{news}\n\n"
        "SEO GOAL: Rank on Google/Bing for US, UK, and Asian investors.\n\n"
        "CONTENT STRUCTURE:\n"
        "1. TITLE: Use a global headline (e.g., 'Global Market Outlook: US Tech Resilience vs China Stimulus').\n"
        "2. US MARKET: Analyze NASDAQ/S&P 500 and Fed Policy.\n"
        "3. EUROPE/UK: Analyze FTSE 100 and inflation data.\n"
        "4. ASIA: Analyze China's economy and Nifty (India) as a secondary correlation.\n"
        "5. TABLES: Provide a 'Global Pivot Table' including NASDAQ, FTSE, and Nifty levels.\n"
        "6. TONE: Institutional financial analyst. NO AI FLUFF.\n\n"
        "END WITH THIS EXACT HTML FOOTER:\n"
        '<h3>📢 Share this Analysis</h3>\n'
        '<div class="share-bar">\n'
        '  <a href="https://wa.me/?text={{ page.title }} - {{ site.url }}{{ page.url }}" class="share-btn btn-whatsapp"><i class="fa fa-whatsapp"></i> WhatsApp</a>\n'
        '  <a href="https://twitter.com/intent/tweet?text={{ page.title }}&url={{ site.url }}{{ page.url }}" class="share-btn btn-twitter"><i class="fa fa-twitter"></i> Twitter</a>\n'
        '  <a href="https://t.me/share/url?url={{ site.url }}{{ page.url }}&text={{ page.title }}" class="share-btn btn-telegram"><i class="fa fa-telegram"></i> Telegram</a>\n'
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
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5, # Lower temperature for more factual financial reporting
        )
        content = completion.choices[0].message.content
        if not os.path.exists(POSTS_DIR): os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Success: Global Post Created.")
    except Exception as e: 
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_full_report()
