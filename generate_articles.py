import os
import pytz
from datetime import datetime
from google import genai

# Setup
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")
posts_dir = os.path.join(os.getcwd(), '_posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

# MANDATORY TEST POST (To prove the folder/git works)
test_file = os.path.join(posts_dir, f"{date_str}-test-manual.md")
with open(test_file, "w") as f:
    f.write("---\nlayout: post\ntitle: 'System Test'\n---\nTest success.")

def generate_seo_post(region):
    prompt = f"Write a 400-word market analysis for {region}. Jekyll format."
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    filename = f"{date_str}-ai-{region.lower()}.md"
    with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
        f.write(response.text)

for r in ["India", "US"]:
    try:
        generate_seo_post(r)
    except Exception as e:
        print(f"Error: {e}")
