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
    """Removes all but the 10 most recent posts for AdSense compliance."""
    if not os.path.exists(POSTS_DIR):
        return
    
    all_posts = sorted(
        [f for f in os.listdir(POSTS_DIR) if f.endswith('.md')],
        reverse=True
    )
    
    if len(all_posts) > 10:
        posts_to_delete = all_posts[10:]
        for post in posts_to_delete:
            os.remove(os.path.join(POSTS_DIR, post))
            print(f"🗑️ Deleted old post: {post}")

def get_live_market_news():
    """Fetches high-authority global and Indian news for worldwide reach."""
    headlines = []
    url = "https://news.google.com/rss/search?q=nifty+50+analysis+fed+rate+hike+global+economy&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        for item in root.findall('.//item')[:12]:
            headlines.append(item.find('title').text)
    except Exception as e:
        print(f"News Fetch Error: {e}")
        return "Global Market Trends"
    return "\n".join(headlines)

def clean_markdown(text):
    """Ensures Jekyll compatibility."""
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text.strip()

def generate_premium_report():
    filename = f"{date_str}-global-market-analysis.md"
    file_path = os.path.join(POSTS_DIR, filename)

    # 1. Maintenance: Keep only latest 10
    keep_only_latest_10()

    # 2. Get Data
    news_context = get_live_market_news()

    # 3. Create Human-Like, Professional Prompt
    prompt = (
        f"Today is {date_str}. Write a 1,200-word Deep-Dive Market Intelligence Report for ai360trading.in.\n\n"
        f"REAL-TIME CONTEXT:\n{news_context}\n\n"
        "REQUIREMENTS FOR ADSENSE APPROVAL:\n"
        "- Tone: Professional, authoritative, financial journalist style.\n"
        "- NO AI CLICHES: Avoid 'unlock', 'delve', 'comprehensive', or 'dive deep'.\n"
        "- Formatting: Use H2/H3 tags and Markdown tables for Nifty Support/Resistance levels.\n"
        "- Content: Analyze how Global Macro (US/Global) affects Indian Markets today.\n"
        "- MANDATORY FOOTER (Social & Subscription):\n"
        "At the very end of the post, add this exact HTML:\n\n"
        '<h3>📢 Share this Intelligence</h3>\n'
        '<div class="share-bar">\n'
        '  <a href="https://wa.me/?text=Check out today\'s market intelligence: {{ site.url }}{{ page.url }}" class="share-btn btn-whatsapp"><i class="fa fa-whatsapp"></i> WhatsApp</a>\n'
        '  <a href="https://twitter.com/intent/tweet?text=Market Intelligence&url={{ site.url }}{{ page.url }}" class="share-btn btn-twitter"><i class="fa fa-twitter"></i> Twitter</a>\n'
        '</div>\n\n'
        '<div class="sub-box">🚀 <b>Join our Telegram</b> for real-time market signals: <a href="https://t.me/YOUR_TELEGRAM_LINK">Click Here to Join</a></div>'
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        
        content = clean_markdown(completion.choices[0].message.content)
        
        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Success: 1,200-word professional report with social buttons created.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_premium_report()
