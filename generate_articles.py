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
    """Fetches real-time trending search terms to ensure fresh SEO content."""
    url = "https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-330&geo=US"
    try:
        r = requests.get(url, timeout=10)
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
    """Scrapes varying topics so the AI has new information to write about every morning."""
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
    
    # SEO SLUG: Creates a unique URL for every post
    slug_options = ["market-intelligence", "global-macro-alert", "trading-shocker", "stock-market-update"]
    chosen_slug = f"{date_str}-{random.choice(slug_options)}"
    file_path = os.path.join(POSTS_DIR, f"{chosen_slug}.md")

    # FIXED IMAGE: Direct Unsplash URL that renders correctly in Jekyll/Markdown
    # Adding a random 'sig' number ensures the image is different every single day.
    img_url = f"https://images.unsplash.com/photo-1611974714013-3c7456ca017a?auto=format&fit=crop&w=800&q=80&sig={random.randint(1,999)}"
    img_tag = f"![Market Analysis]({img_url})"

    prompt = (
        f"Today is {date_str}. Write a 1,500-word VIRAL Market Report for ai360trading.in.\n"
        f"TOP GOOGLE TRENDS TODAY: {', '.join(trends)}\n"
        f"HEADLINE NEWS:\n{news}\n\n"
        "ARTICLE STRUCTURE:\n"
        f"1. Start with this image: {img_tag}\n"
        "2. Analyze why the Google Trends above are moving the markets.\n"
        "3. Focus on 'Incident of the Day' for worldwide attraction.\n"
        "4. Include a section: '🌍 TRENDING HASHTAGS' using #StockMarket and the trends found.\n"
        "5. Analyze NASDAQ, FTSE 100, and Asian markets.\n"
        "6. Provide a 'Global Pivot Table' with Support/Resistance levels.\n\n"
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
            temperature=0.8, # Keeps the content creative and unique daily
        )
        content = completion.choices[0].message.content
        
        # FRONT MATTER: This is where the magic happens for unique URLs and Formatting
        header = (
            "---\n"
            "layout: post\n"
            f"title: \"{date_str} | Global Market Intelligence Report\"\n"
            f"date: {date_str}\n"
            f"permalink: /analysis/{chosen_slug}/\n"
            "categories: [Market-Intelligence]\n"
            "---\n\n"
        )
        
        if not os.path.exists(POSTS_DIR): os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        print(f"✅ Success: Unique Report Created at /analysis/{chosen_slug}/")
    except Exception as e: 
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_full_report()
