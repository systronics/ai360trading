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
    headlines = []
    url = "https://news.google.com/rss/search?q=nifty+50+analysis+us+market+nasdaq&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)
        for item in root.findall('.//item')[:10]:
            headlines.append(item.find('title').text)
    except: return "Market Volatility Observed"
    return "\n".join(headlines)

def generate_full_report():
    news = get_live_news()
    filename = f"{date_str}-global-market-analysis.md"
    file_path = os.path.join(POSTS_DIR, filename)

    # The prompt forces the AI to use our NEW CSS CLASSES
    prompt = (
        f"Today: {date_str}. Generate a 1,200-word financial report for ai360trading.in.\n"
        f"Context: {news}\n\n"
        "RULES:\n"
        "1. Include Jekyll Frontmatter (layout: post, title, categories).\n"
        "2. Use H2 for major sections and Markdown tables for Nifty levels.\n"
        "3. END WITH THIS EXACT HTML FOOTER:\n\n"
        '<h3>📢 Share this Analysis</h3>\n'
        '<div class="share-bar">\n'
        '  <a href="https://wa.me/?text={{ page.title }} - {{ site.url }}{{ page.url }}" class="share-btn btn-whatsapp"><i class="fa fa-whatsapp"></i> WhatsApp</a>\n'
        '  <a href="https://twitter.com/intent/tweet?text={{ page.title }}&url={{ site.url }}{{ page.url }}" class="share-btn btn-twitter"><i class="fa fa-twitter"></i> Twitter</a>\n'
        '  <a href="https://t.me/share/url?url={{ site.url }}{{ page.url }}&text={{ page.title }}" class="share-btn btn-telegram"><i class="fa fa-telegram"></i> Telegram</a>\n'
        '</div>\n\n'
        '<div class="sub-box">\n'
        '  <h3>🚀 Get Real-Time Trade Signals</h3>\n'
        '  <p>Join 5,000+ traders in our official Telegram channel.</p>\n'
        '  <a href="https://t.me/{{ site.telegram_username }}">Join Telegram Now</a>\n'
        '</div>'
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        content = completion.choices[0].message.content
        if not os.path.exists(POSTS_DIR): os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Success: Post created with dynamic Telegram links.")
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_full_report()
