import os
import pytz
import re
from datetime import datetime
from google import genai

# FIXED: Removed the extra 'api_' from 'api_api_key'
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

posts_dir = os.path.join(os.getcwd(), '_posts')
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

# --- FORCE A TEST POST ---
with open(os.path.join(posts_dir, f"{date_str}-test-post.md"), "w") as f:
    f.write(f"---\nlayout: post\ntitle: 'System Update {date_str}'\n---\nAutomated sync successful.")

def generate_seo_post(region):
    print(f"Generating for {region}...")
    try:
        prompt = f"Write a 400-word market analysis for {region} stocks. Output in Jekyll format."
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        content = re.sub(r'^```markdown\n|```$', '', response.text, flags=re.MULTILINE)
        
        filename = f"{date_str}-ai-{region.lower()}.md"
        with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created {filename}")
    except Exception as e:
        print(f"❌ API Error: {e}")

for r in ["India", "US"]:
    generate_seo_post(r)
