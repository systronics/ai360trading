import os
import pytz
from datetime import datetime
from groq import Groq

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")

def generate_market_post(region):
    print(f"Generating Groq report for {region}...")
    
    prompt = (f"Act as a senior market analyst. Write a professional market analysis for the {region} market on {date_str}. "
              "Focus on GIFT Nifty and Gold trends. Include: 'Market Sentiment', 'Key Levels', and 'Action Plan'. "
              "Output strictly in Jekyll Markdown format with frontmatter tags: [Market Analysis, AI Trading, global-markets]")

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        
        content = completion.choices[0].message.content
        filename = f"{date_str}-{region.lower()}-market-pulse.md"
        
        posts_dir = os.path.join(os.getcwd(), '_posts')
        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)
            
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {filename}")
        
    except Exception as e:
        print(f"❌ Groq Error: {e}")

generate_market_post("Indian")
