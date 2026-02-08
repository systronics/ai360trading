import os
import pytz
from datetime import datetime
from google import genai  # NEW 2026 SDK

# The client automatically uses your GEMINI_API_KEY from GitHub Secrets
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Indian Time Zone (IST)
ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

# Path to your _posts folder
posts_dir = os.path.join(os.getcwd(), '_posts')
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

def generate_seo_post(region):
    print(f"Creating SEO post for {region}...")
    # Updated to gemini-2.0-flash for better 2026 performance
    prompt = (f"Write a 400-word market analysis for {region} stocks. "
              "Include a 'Key Market Trends' section. Output in Jekyll Markdown format with: "
              "layout: post, title: 'Expert {region} Market News', "
              "description: 'Get latest {region} trading insights and stock trends for 2026.'")
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )
    
    content = response.text.strip()
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:-1])

    filename = f"{date_str}-ai-{region.lower()}.md"
    with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: {filename} generated.")

# Regions to cover for maximum traffic
for r in ["India", "US", "Asia"]:
    try:
        generate_seo_post(r)
    except Exception as e:
        print(f"Error on {r}: {e}")
