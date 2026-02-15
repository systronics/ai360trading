import os
import pytz
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

    prompt = (
        f"Today: {date_str}. Write a 1,500-word Market Intelligence Report for ai360trading.in.\n"
        f"Context News:\n{news}\n\n"
        "PERFORMANCE RULES (For Google PageSpeed):\n"
        "1. If you include an image, use this HTML: <img src='URL' width='800' height='450' loading='lazy' alt='Description'>.\n"
        "2. Use clean H2 and H3 tags. Avoid huge walls of text.\n\n"
        "CONTENT STRUCTURE:\n"
        "Analyze NASDAQ, FTSE 100, and China markets. Provide a 'Global Pivot Table' for traders.\n\n"
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
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        content = completion.choices[0].message.content
        if not os.path.exists(POSTS_DIR): os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Success: Global Performance-Optimized Post Created.")
    except Exception as e: 
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_full_report()
