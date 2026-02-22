import os
import pytz
import requests
import random
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")
date_display = now.strftime("%B %d, %Y")
POSTS_DIR = os.path.join(os.getcwd(), '_posts')


def get_google_trends():
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
        return [
            "Stock Market Pulse", "Fed Interest Rates", "Nvidia AI", "Global Macro",
            "Bitcoin ETF", "Oil Prices", "China Economy", "S&P 500", "Inflation CPI", "Gold Rally"
        ]


def get_live_news():
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

    slug_options = ["market-intelligence", "global-macro-alert", "trading-shocker", "stock-market-update"]
    slug_suffix = random.choice(slug_options)
    # Timestamp added to prevent same-day slug collision
    chosen_slug = f"{date_str}-{slug_suffix}-{now.strftime('%H%M')}"
    file_path = os.path.join(POSTS_DIR, f"{chosen_slug}.md")

    # Reliable daily image via Picsum (no auth, always renders)
    img_seed = random.randint(1, 9999)
    img_url = f"https://picsum.photos/seed/{img_seed}/800/400"
    img_tag = f"![Global Market Intelligence Report — {date_display}]({img_url})"

    prompt = (
        f"Today is {date_str}. Write a 1,500-word Global Market Intelligence Report for ai360trading.in.\n"
        f"TOP GOOGLE TRENDS TODAY: {', '.join(trends)}\n"
        f"HEADLINE NEWS:\n{news}\n\n"

        "SEO RULES (follow strictly):\n"
        "- The exact phrase 'Global Market Intelligence Report' MUST appear in the very first sentence of the article body.\n"
        "- Use the trending keywords naturally throughout the article at least 2-3 times each.\n"
        "- Write a meta description of exactly 155 characters summarizing the article — place it at the very top labeled: META_DESCRIPTION: <text>\n\n"

        "HEADING HIERARCHY (never skip levels):\n"
        "- Do NOT write an H1 — that is already the page title.\n"
        "- Use ## (H2) for all major sections.\n"
        "- Use ### (H3) only inside an H2 section.\n"
        "- Use #### (H4) only inside an H3 section.\n"
        "- NEVER jump from ## to ####.\n\n"

        "ARTICLE STRUCTURE:\n"
        f"1. Start with: META_DESCRIPTION: <155-char summary>\n"
        f"2. Then place this image on its own line: {img_tag}\n"
        "3. ## Market Overview — mention 'Global Market Intelligence Report' in first sentence\n"
        "4. ## Incident of the Day — worldwide attention-grabbing event from the headlines\n"
        "5. ## NASDAQ & Tech Sector Analysis\n"
        "   ### AI & Semiconductors\n"
        "6. ## FTSE 100 & European Markets\n"
        "7. ## Asian Markets & China Macro\n"
        "8. ## Commodities: Oil & Gold\n"
        "9. ## Crypto & Digital Assets\n"
        "10. ## 🌍 Trending Hashtags — use #StockMarket, #GlobalMacro, and hashtags from trends\n"
        "11. ## Global Pivot Table\n"
        "    ### Support & Resistance Levels (format as a Markdown table)\n\n"

        "END WITH THIS EXACT HTML FOOTER (do not modify):\n"
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
                {
                    "role": "system",
                    "content": (
                        "You are a world-class financial analyst and SEO content strategist. "
                        "You write unique, high-impact market reports with perfect heading hierarchy. "
                        "You NEVER skip heading levels (H2 → H3 → H4 only). "
                        "You NEVER repeat your writing style across articles."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        content = completion.choices[0].message.content

        # Extract meta description from AI output
        meta_description = "AI360Trading Global Market Intelligence Report — daily macro analysis, NASDAQ, FTSE, crypto and trading signals."
        lines = content.split("\n")
        cleaned_lines = []
        for line in lines:
            if line.startswith("META_DESCRIPTION:"):
                extracted = line.replace("META_DESCRIPTION:", "").strip()
                if 50 < len(extracted) <= 160:
                    meta_description = extracted
            else:
                cleaned_lines.append(line)
        content = "\n".join(cleaned_lines)

        header = (
            "---\n"
            "layout: post\n"
            f"title: \"{date_display} | Global Market Intelligence Report\"\n"
            f"date: {date_str}\n"
            f"permalink: /analysis/{chosen_slug}/\n"
            f"description: \"{meta_description}\"\n"
            f"image: {img_url}\n"
            f"keywords: \"global market intelligence report, {', '.join(trends[:5]).lower()}\"\n"
            "categories: [Market-Intelligence]\n"
            "---\n\n"
        )

        if not os.path.exists(POSTS_DIR):
            os.makedirs(POSTS_DIR)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        print(f"✅ Success: Report created at /analysis/{chosen_slug}/")
        print(f"   Meta: {meta_description}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    generate_full_report()
