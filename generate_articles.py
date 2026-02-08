import os
import pytz
from datetime import datetime
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Indian Time Zone (IST) - Critical for your workflow
ist = pytz.timezone('Asia/Kolkata')
current_ist_time = datetime.now(ist)
date_str = current_ist_time.strftime("%Y-%m-%d")

print(f"DEBUG: Current IST Date for Filename: {date_str}")

# Force path to the root _posts folder
posts_dir = os.path.join(os.getcwd(), '_posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

def generate_post(region):
    print(f"Generating for {region}...")
    prompt = f"Write a 300-word market update for {region} stocks. Use Jekyll Markdown with layout: post and categories: [global-news]."
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:-1])

    filename = f"{date_str}-ai-{region.lower()}.md"
    path = os.path.join(posts_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: {filename} created.")

for region in ["US", "UK", "Europe", "Asia"]:
    try:
        generate_post(region)
    except Exception as e:
        print(f"ERROR on {region}: {e}")
