import os
import pytz
import re
from datetime import datetime
from google import genai

# SDK Client initialization
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")

posts_dir = os.path.join(os.getcwd(), '_posts')
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

def generate_market_post(region):
    print(f"Generating professional report for {region}...")
    try:
        prompt = (f"Act as a senior market analyst. Write a high-quality market analysis for the {region} market on {date_str}. "
                  "Focus on GIFT Nifty, Nasdaq, and Gold trends. Include: 'Market Sentiment', 'Key Levels', and 'Action Plan'. "
                  "Output strictly in Jekyll Markdown format with this frontmatter: "
                  f"---\nlayout: post\ntitle: '{region} Market Pulse: {date_str}'\n"
                  "tags: [Market Analysis, AI Trading, global-markets]\n"
                  "excerpt: 'AI-powered technical breakdown for professional traders.'\n---")
        
        # Using Gemini 2.0 Flash
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        content = response.text.strip()
        
        # Clean markdown code blocks
        content = re.sub(r'^```markdown\n|```$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```\n|```$', '', content, flags=re.MULTILINE)
        
        filename = f"{date_str}-{region.lower()}-market-pulse.md"
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created: {filename}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Generate Indian market report (runs every morning)
generate_market_post("Indian")
