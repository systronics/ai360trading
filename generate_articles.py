import os
import pytz
import re
from datetime import datetime
from groq import Groq

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")

def clean_markdown(text):
    """Removes AI filler and ensures Jekyll compatibility."""
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    match = re.search(r'---.*---', text, re.DOTALL)
    if match:
        return text[match.start():].strip()
    return text.strip()

def generate_market_post(region):
    print(f"Generating SEO-Optimized report for {region}...")
    
    prompt = (
        f"Act as a Financial Journalist and SEO Expert. Write a Jekyll blog post for {region} market on {date_str}. "
        "INSTRUCTIONS:\n"
        "1. Start with Jekyll Frontmatter (title, date, categories, tags, excerpt).\n"
        "2. Use H2 and H3 tags for structure.\n"
        "3. BOLD all price levels, support/resistance numbers, and percentages (e.g., **18,500**).\n"
        "4. Content: Market Sentiment, Global Cues (Nasdaq/Dow), Key Levels (Nifty/BankNifty/Gold), and Trading Strategy.\n"
        "5. Include a section 'Why This Matters for Algo Traders'.\n"
        "6. Finish with a 'Standard Trading Disclaimer' in italics."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        
        raw_content = completion.choices[0].message.content
        final_content = clean_markdown(raw_content)
        
        filename = f"{date_str}-{region.lower()}-market-pulse.md"
        posts_dir = os.path.join(os.getcwd(), '_posts')
        
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"✅ SEO Article Created: {filename}")
        
    except Exception as e:
        print(f"❌ Groq Error: {e}")

# Run for Indian Market
generate_market_post("Indian")
