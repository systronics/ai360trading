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
    print(f"Generating professional report for {region}...")
    try:
        # Prompt designed for professional financial reporting
        prompt = (f"Act as a senior market analyst. Write a 400-word stock market analysis for the {region} market on {date_str}. "
                  "Include specific sections: 'Market Sentiment', 'Key Support/Resistance Levels', and 'Top Sector Performance'. "
                  "Output strictly in Jekyll Markdown format with this frontmatter: "
                  f"---\nlayout: post\ntitle: '{region} Market Analysis: {date_str}'\n"
                  "tags: [Market Analysis, AI Trading]\n"
                  "excerpt: 'Daily AI-powered technical breakdown of the market trends, key levels, and sector-wise performance for professional traders.'\n---")
        
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        content = response.text.strip()
        
        # Remove any markdown code blocks the AI might wrap the text in
        content = re.sub(r'^```markdown\n|```$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```\n|```$', '', content, flags=re.MULTILINE)
        
        filename = f"{date_str}-ai-{region.lower()}-market.md"
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Successfully created: {filename}")
    except Exception as e:
        print(f"❌ Error generating {region} post: {e}")

# Run the generation for your core markets
for region in ["Indian", "US"]:
    generate_market_post(region)
