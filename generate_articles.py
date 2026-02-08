import os
import pytz
import re
from datetime import datetime
from google import genai

# Authentication - The SDK automatically looks for GEMINI_API_KEY
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

# Use absolute path to prevent "File Not Found" errors in GitHub Actions
base_path = os.path.dirname(os.path.abspath(__file__))
posts_dir = os.path.join(base_path, '_posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

def generate_seo_post(region):
    print(f"🚀 Generating SEO post for {region}...")
    
    # Prompt with specific instructions to help you rank and grow followers
    prompt = (f"Analyze the current 2026 stock market trends for {region}. "
              "Focus on high-growth sectors. Output in Jekyll Markdown. "
              "Include Front Matter: layout: post, title: 'Weekly {region} Trading Update', "
              "categories: [market-analysis], description: 'Pro insights on {region} stocks.' "
              "Use H2 headers and bullet points for readability.")
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    
    content = response.text.strip()
    
    # Remove Markdown code blocks if the AI wraps the whole post in them
    content = re.sub(r'^```markdown\n|```$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^```\n|```$', '', content, flags=re.MULTILINE)

    filename = f"{date_str}-ai-{region.lower()}-update.md"
    file_path = os.path.join(posts_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ SUCCESS: {filename} created.")

# Running for your target markets
for r in ["India", "US", "Asia"]:
    try:
        generate_seo_post(r)
    except Exception as e:
        print(f"❌ Error on {r}: {e}")
