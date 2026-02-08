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
    """Removes AI conversational filler and code block wrappers."""
    # 1. Remove ```markdown or ``` lines
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    # 2. Find the first '---' and treat everything before it as garbage
    match = re.search(r'---.*---', text, re.DOTALL)
    if match:
        return text[match.start():].strip()
    return text.strip()

def generate_market_post(region):
    print(f"Generating Groq report for {region}...")
    
    # Precise prompt to ensure Jekyll compatibility
    prompt = (
        f"Generate a Jekyll blog post for the {region} market on {date_str}. "
        "IMPORTANT: Start directly with '---' frontmatter. "
        "Title must include the date. Tags: [Market Analysis, AI Trading, global-markets]. "
        "Content must include: Market Sentiment, Key Levels (GIFT Nifty, Gold), and Action Plan."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, # Lower temperature = more professional/stable output
        )
        
        raw_content = completion.choices[0].message.content
        final_content = clean_markdown(raw_content)
        
        filename = f"{date_str}-{region.lower()}-market-pulse.md"
        posts_dir = os.path.join(os.getcwd(), '_posts')
        
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"✅ Created: {filename}")
        
    except Exception as e:
        print(f"❌ Groq Error: {e}")

# Run for Indian Market
generate_market_post("Indian")
