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
    match = re.search(r'---.*---', text, re.DOTALL)
    if match:
        return text[match.start():].strip()
    return text.strip()

def generate_market_post():
    # Simple filename format from working version
    filename = f"{date_str}-market-update.md"
    posts_dir = os.path.join(os.getcwd(), '_posts')
    file_path = os.path.join(posts_dir, filename)

    print(f"Generating Stable Market Report for {date_str}...")
    
    prompt = (
        f"Write a professional Jekyll blog post for the Indian Stock Market on {date_str}. "
        "Use this EXACT Frontmatter:\n"
        "---\n"
        "layout: post\n"
        f"title: 'Indian Market Analysis: {date_str}'\n"
        "categories: [Market-Update]\n"
        "tags: [global-markets]\n"
        "--- \n\n"
        "Content: Market Sentiment, Global Cues, and Nifty/BankNifty Levels. Bold all numbers."
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
        print(f"✅ Success: {filename} created.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_market_post()
