import os
import pytz
from datetime import datetime
import google.generativeai as genai

# Setup Gemini - Fixed for current API version
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Force Indian Time Zone (IST)
ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

# Use absolute path to the root _posts folder
posts_dir = os.path.join(os.getcwd(), '_posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

def generate_post(region):
    print(f"Generating article for {region}...")
    # Using simple text generation to avoid search tool permission errors
    prompt = f"Write a 300-word market update for {region} stocks. Output in Jekyll Markdown format with layout: post and categories: [global-news]."
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    # Clean AI markers
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:-1])

    filename = f"{date_str}-ai-{region.lower()}.md"
    path = os.path.join(posts_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully created: {filename}")

for region in ["US", "UK", "Europe", "Asia"]:
    try:
        generate_post(region)
    except Exception as e:
        print(f"Error generating {region}: {e}")
