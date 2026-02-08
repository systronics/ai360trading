import os
import pytz
from datetime import datetime
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Force Indian Time Zone (IST)
ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

# Use absolute path to the root _posts folder
# os.getcwd() points to the root of your repo in GitHub Actions
posts_dir = os.path.join(os.getcwd(), '_posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

def generate_post(region):
    prompt = f"Write a 300-word market update for {region}. Output in Jekyll Markdown format with title and categories: [global-news]."
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    # Clean AI markers
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:-1])

    filename = f"{date_str}-ai-{region.lower()}.md"
    path = os.path.join(posts_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"File created: {path}")

for region in ["US", "UK", "Europe", "Asia"]:
    generate_post(region)
