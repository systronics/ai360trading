import os
import pytz
import re
from datetime import datetime
from google import genai

# Setup 2026 SDK
client = genai.Client(api_api_key=os.environ["GEMINI_API_KEY"])
ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

# Force absolute path to ensure GitHub Actions stays in the root
posts_dir = os.path.join(os.getcwd(), '_posts')
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

# --- MANDATORY TEST POST ---
# This ensures there is ALWAYS a change for Git to detect
with open(os.path.join(posts_dir, f"{date_str}-test-post.md"), "w") as f:
    f.write(f"---\nlayout: post\ntitle: 'System Update {date_str}'\n---\nAutomated sync successful.")

def generate_seo_post(region):
    print(f"Generating for {region}...")
    try:
        prompt = f"Write a 400-word market analysis for {region} stocks. Layout: post."
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        content = re.sub(r'^```markdown\n|```$', '', response.text, flags=re.MULTILINE)
        
        filename = f"{date_str}-ai-{region.lower()}.md"
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created {filename}")
    except Exception as e:
        print(f"❌ API Error: {e}")

# Run for your target markets
for r in ["India", "US"]:
    generate_seo_post(r)
