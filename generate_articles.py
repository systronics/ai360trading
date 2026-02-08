import os
import pytz
import re
from datetime import datetime
from groq import Groq

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Set Timezone to India
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
    filename = f"{date_str}-{region.lower()}-market-pulse.md"
    posts_dir = os.path.join(os.getcwd(), '_posts')
    file_path = os.path.join(posts_dir, filename)

    print(f"Generating Fresh SEO report for {region}...")
    
    prompt = (
        f"Act as a Financial Journalist. Write a Jekyll blog post for the {region} market on {date_str}. "
        "CRITICAL INSTRUCTIONS:\n"
        "1. You MUST start with this EXACT Frontmatter:\n"
        "---\n"
        "layout: post\n"
        f"title: 'Daily {region} Market Analysis: {date_str}'\n"
        "categories: [Market-Update]\n"
        "tags: [global-markets, nifty, banknifty]\n"  # THIS TAG FIXES THE VISIBILITY
        "excerpt: 'AI-powered breakdown of market sentiment and key levels for today.'\n"
        "---\n"
        "\n"
        "2. Use H2 tags for: Market Sentiment, Global Cues, and Key Levels.\n"
        "3. BOLD all price levels (e.g., **18,500**).\n"
        "4. End with a Disclaimer in italics."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        
        raw_content = completion.choices[0].message.content
        final_content = clean_markdown(raw_content)
        
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"✅ Success: {filename} created with required tags.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_market_post("Indian")
