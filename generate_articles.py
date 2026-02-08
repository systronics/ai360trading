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

def generate_market_post(region):
    filename = f"{date_str}-{region.lower()}-market-pulse.md"
    posts_dir = os.path.join(os.getcwd(), '_posts')
    file_path = os.path.join(posts_dir, filename)

    # CHECK: Does the post already exist?
    if os.path.exists(file_path):
        print(f"⏩ Skipping: {filename} already exists in _posts folder.")
        return

    print(f"Generating Daily SEO-Optimized report for {region}...")
    
    prompt = (
        f"Act as a Financial Journalist and SEO Expert. Write a Jekyll blog post for the {region} market on {date_str}. "
        "INSTRUCTIONS:\n"
        "1. Start with Jekyll Frontmatter (title, date, categories, tags, excerpt).\n"
        "2. Use H2 tags for structure: Market Sentiment, Global Cues, Key Levels, and Strategy.\n"
        "3. BOLD all price levels (e.g., **18,500**).\n"
        "4. Strategy: Specifically mention Nifty and BankNifty levels.\n"
        "5. End with a Disclaimer in italics."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        
        raw_content = completion.choices[0].message.content
        
        # Simple cleanup to ensure frontmatter is at the top
        text = re.sub(r'^```[a-zA-Z]*\n', '', raw_content, flags=re.MULTILINE)
        text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
        
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text.strip())
        print(f"✅ Daily SEO Article Created: {filename}")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")

if __name__ == "__main__":
    generate_market_post("Indian")
