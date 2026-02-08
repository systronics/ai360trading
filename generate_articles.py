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
    print(f"Generating report for {region}...")
    
    prompt = (
        f"Write a professional Jekyll blog post for {region} market on {date_str}. "
        "INSTRUCTIONS:\n"
        "1. Start with Jekyll Frontmatter:\n"
        "---\n"
        "layout: post\n"
        f"title: '{region} Market Analysis {date_str}'\n"
        "categories: news\n"
        "tags: [global-markets]\n"
        "---\n"
        "2. Content: Market Sentiment, Global Cues, Key Levels, and Trading Strategy.\n"
        "3. BOLD all price levels.\n"
        "4. Finish with a disclaimer."
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
        print(f"✅ Article Created: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Run for Indian Market
generate_market_post("Indian")
