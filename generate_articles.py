import os
import pytz
import re
from datetime import datetime
from groq import Groq

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Set Timezone to India for consistent daily posting
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")

def clean_markdown(text):
    """Removes AI filler and ensures Jekyll compatibility."""
    # Remove markdown code block wrappers if the AI includes them
    text = re.sub(r'^```[a-zA-Z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    
    # Ensure the post starts with the YAML frontmatter
    match = re.search(r'---.*---', text, re.DOTALL)
    if match:
        return text[match.start():].strip()
    return text.strip()

def generate_market_post(region):
    print(f"Generating Daily SEO-Optimized report for {region}...")
    
    # Enhanced prompt for better SEO and Trading Authority
    prompt = (
        f"Act as a Financial Journalist and SEO Expert. Write a Jekyll blog post for the {region} market on {date_str}. "
        "INSTRUCTIONS:\n"
        "1. Start with Jekyll Frontmatter:\n"
        "   ---\n"
        f"   title: 'Daily {region} Market Pulse: {date_str} Analysis'\n"
        f"   date: {date_str}\n"
        "   categories: [Market-Update]\n"
        "   tags: [Nifty, BankNifty, Trading-Strategy, AI-Insights]\n"
        "   excerpt: 'Daily AI-powered breakdown of market sentiment, key levels, and actionable trading insights.'\n"
        "   ---\n"
        "2. Structure: Use H2 tags for 'Market Sentiment', 'Global Cues', 'Key Levels to Watch', and 'Algo Trading Perspective'.\n"
        "3. Readability: Use bullet points and BOLD all price levels (e.g., **18,500**) and support/resistance zones.\n"
        "4. Strategy: Include specific levels for Nifty and BankNifty based on recent trends.\n"
        "5. Final Touch: End with a 'Trading Disclaimer' in italics."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4, # Lower temperature for more factual financial data
        )
        
        raw_content = completion.choices[0].message.content
        final_content = clean_markdown(raw_content)
        
        # Consistent filename format for Jekyll _posts folder
        filename = f"{date_str}-{region.lower()}-market-pulse.md"
        posts_dir = os.path.join(os.getcwd(), '_posts')
        
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"✅ Daily SEO Article Created: {filename}")
        
    except Exception as e:
        print(f"❌ Groq Error: {e}")

# Run for Indian Market (Scheduled for 06:30 AM IST)
if __name__ == "__main__":
    generate_market_post("Indian")
