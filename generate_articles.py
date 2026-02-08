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

# SET TO True to overwrite existing files for testing
FORCE_RUN = True 

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

    # CHECK: Does the post already exist?
    if os.path.exists(file_path) and not FORCE_RUN:
        print(f"⏩ Skipping: {filename} already exists. Set FORCE_RUN=True to overwrite.")
        return

    print(f"Generating Fresh SEO report for {region}...")
    
    prompt = (
        f"Act as a Financial Journalist and SEO Expert. Write a Jekyll blog post for the {region} market on {date_str}. "
        "INSTRUCTIONS:\n"
        "1. Start with Jekyll Frontmatter (title, date, categories, tags, excerpt).\n"
        "2. Use H2 tags: Market Sentiment, Global Cues, Key Levels, and Strategy.\n"
        "3. BOLD all price levels (e.g., **18,500**) and percentages.\n"
        "4. Include specific support/resistance for Nifty and BankNifty.\n"
        "5. End with a Disclaimer in italics."
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
        print(f"✅ Daily SEO Article Created/Updated: {filename}")
        
    except Exception as e:
        print(f"❌ Groq Error: {e}")

if __name__ == "__main__":
    generate_market_post("Indian")
