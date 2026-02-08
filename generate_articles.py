import os
import pytz
import re
from datetime import datetime
from groq import Groq

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Timezone Setup
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")

def clean_markdown(text):
    """Ensures Jekyll compatibility by removing AI wrappers."""
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text.strip()

def generate_market_post():
    filename = f"{date_str}-market-intelligence.md"
    posts_dir = os.path.join(os.getcwd(), '_posts')
    file_path = os.path.join(posts_dir, filename)

    print(f"Generating Premium Intelligence Report for {date_str}...")
    
    # ADVANCED PROMPT FOR HIGH-VALUE VISITORS
    prompt = (
        f"Act as a Senior Market Strategist. Write a crisp Indian Market Intelligence report for {date_str}. "
        "Use this Frontmatter:\n"
        "---\n"
        "layout: post\n"
        f"title: 'Market Intelligence {date_str} | Nifty & Global Macro Outlook'\n"
        "categories: [Market-Update]\n"
        "tags: [global-markets]\n"
        "---\n\n"
        "### ⚡ Market Pulse\n"
        "Provide 3 bullet points on Global Sentiment (US Tech, Brent Oil, Dollar Index).\n\n"
        "### 📊 Key Pivot Levels\n"
        "Create a clean Markdown table with: Index, Support, Pivot, Resistance for NIFTY, BANKNIFTY, and FINNIFTY.\n\n"
        "### 🎯 Top Trending Stocks & Sectors\n"
        "List 3 stocks showing breakout potential and why.\n\n"
        "### 🗓️ Major Global Events Today\n"
        "List any RBI, Fed, or economic data releases.\n\n"
        "### 🏷️ Trending Hashtags\n"
        "#Nifty50 #BankNifty #StockMarketIndia #Investing #GlobalMacro #TradingStrategy #AI360Trading\n\n"
        "--- \n"
        "**Pro Tip:** Check our [Live Dashboards](/#dashboards) for real-time signals."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, # Lower temperature for more factual/professional data
        )
        
        content = clean_markdown(completion.choices[0].message.content)
        
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Premium Post Created: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_market_post()
