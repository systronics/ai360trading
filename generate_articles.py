import os
import pytz
import re
from datetime import datetime
from google import genai

# Correct 2026 SDK Client initialization
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

posts_dir = os.path.join(os.getcwd(), '_posts')
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

def generate_market_post(region):
    print(f"Generating live report for {region}...")
    try:
        # Optimized prompt for Indian trading hours and SEO
        prompt = (f"Write a 400-word stock market analysis for {region} on {date_str}. "
                  "Include specific sections for 'Market Sentiment', 'Support & Resistance', and 'Sector Trends'. "
                  "Output strictly in Jekyll Markdown format with frontmatter: "
                  f"layout: post, title: '{region} Market Update - {date_str}', "
                  "tags: [Market Analysis, AI Trading]")
        
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        content = response.text.strip()
        
        # Clean AI markdown syntax
        content = re.sub(r'^```markdown\n|```$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```\n|```$', '', content, flags=re.MULTILINE)
        
        filename = f"{date_str}-ai-{region.lower()}.md"
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {filename}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Run for both India and US markets
for region in ["India", "US"]:
    generate_market_post(region)
