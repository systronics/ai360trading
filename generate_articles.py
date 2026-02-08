import os
import pytz
from datetime import datetime
import google.generativeai as genai

# Setup Gemini - Final Stable Config for 2026
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Indian Time Zone (IST) - Matches your _config.yml
ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

# Explicit Root Path
posts_dir = os.path.join(os.getcwd(), '_posts')
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

def generate_post(region):
    prompt = f"Write a 300-word stock update for {region}. Format in Jekyll Markdown (layout: post, categories: [global-news])."
    response = model.generate_content(prompt)
    content = response.text.strip()
    if content.startswith("```"): content = "\n".join(content.split("\n")[1:-1])
    
    filename = f"{date_str}-ai-{region.lower()}.md"
    with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {filename}")

for r in ["US", "UK", "Europe", "Asia"]:
    generate_post(r)
