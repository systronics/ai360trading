import os
import pytz
import requests
import random
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

# Initialize Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")
POSTS_DIR = os.path.join(os.getcwd(), '_posts')

def get_google_trends():
    """Fetches the actual top 10 trending search terms globally."""
    # Targeting US & Global trends for worldwide attraction
    url = "https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-330&geo=US"
    try:
        r = requests.get(url, timeout=10)
        # Google Trends API has a safety prefix: )]}',
        clean_json = r.text.replace(")]}',\n", "")
        data = json.loads(clean_json)
        trends = []
        for day in data['default']['trendingSearchesDays']:
            for item in day['trendingSearches']:
                trends.append(item['title']['query'])
        return trends[:10]
    except:
        return ["Stock Market Pulse", "Fed Interest Rates", "Nvidia AI", "Global Macro"]

def get_live_news():
    """Scrapes diverse news topics to ensure the AI gets new context daily."""
    queries = [
        "NASDAQ+Nvidia+AI+tech+earnings",
        "Fed+interest+rate+inflation+CPI",
        "China+stimulus+market+economy+Yuan",
        "Crude+Oil+Gold+geopolitical+risk",
        "Crypto+Bitcoin+ETF+regulation"
    ]
    query = random.choice(queries)
    headlines = []
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)
        items = root.findall('.//item')
        random.shuffle(items)
        for item in items[:12]:
            headlines.append(item.find('title').text)
    except: 
        return "Global Market Macro Trends"
    return "\n".join(headlines)

def generate_full_report():
    news = get_live_news()
    trends = get_google_trends()
    
    # Randomize filename slightly to avoid SEO conflicts
    slug = random.choice(["intelligence-report", "market-shocker", "macro-alert", "trading-insights"])
    filename = f"{date_str}-{slug}.md"
    file_path = os.path.join(POSTS_DIR, filename)

    prompt = (
        f"Today is {date_str}. Write a 1,500-word VIRAL Market Report for ai360trading.in.\n"
        f"TOP GOOGLE TRENDS TODAY: {', '.join(trends)}\n"
        f"HEADLINE NEWS:\n{news}\n\n"
        "INSTRUCTIONS:\n"
        "1. Focus on the 'Incident of the Day'—why are these terms trending?\n"
        "2. Analyze NASDAQ, FTSE 100, and China markets specifically.\n"
        "3. Provide a 'Global Pivot Table' with Support/Resistance for traders.\n"
        "4. Include a section: '🌍 TRENDING HASHTAGS' using the keywords above.\n"
        "5. Use H2/H3 tags. Performance rule: <img src='https://images.unsplash.com/photo-1611974714013-3c7456ca017a?w=800' width='800' height='450' loading='lazy' alt='Market Analysis'>.\n\n"
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
                {"role": "system", "content": "You are a world-class financial analyst. You write unique, high-impact news reports and NEVER repeat your style."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        content = completion.choices[0].message.content
        
        # Add Jekyll Front Matter so your website displays it as a post
        header = f"---\nlayout: post\ntitle: \"Global Market Report: {date_str}\"\ndate: {date_str}\ncategories: [Market-Intelligence]\n---\n\n"
        
        if not os.path.exists(POSTS_DIR): os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        print(f"✅ Success: Unique Global Report Created.")
    except Exception as e: 
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_full_report()
