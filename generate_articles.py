import os
from datetime import datetime
from google import genai
from google.genai import types

# 1. Setup Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_ID = "gemini-1.5-flash"

regions = {
    "US": "Wall Street and US Tech Sector",
    "UK": "London Stock Exchange and FTSE 100",
    "Europe": "European Central Bank and DAX/CAC 40",
    "Asia": "Nikkei, Hang Seng, and Asian Emerging Markets"
}

def generate_seo_article(region_name, market_focus):
    print(f"Generating article for {region_name}...")
    
    # The prompt forces Jekyll Front Matter and International SEO focus
    prompt = f"""
    Using Google Search, find the top 3 stock market educational trends for {market_focus} this week.
    Write a high-quality educational article for a trading blog.
    
    Requirements:
    - Format: Jekyll Markdown
    - Layout: post
    - Category: global-news
    - Language: Professional English
    - Content: Analysis of trends, not live trading signals.
    """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]
        )
    )
    
    # 2. Save file with unique prefix to avoid overwriting manual posts
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    safe_name = region_name.lower().replace(" ", "-")
    file_path = f"_posts/{date_prefix}-ai-{safe_name}.md"
    
    # Ensure the directory exists (if you use the subfolder mentioned above)
    # os.makedirs("_posts/global-news", exist_ok=True)
    # file_path = f"_posts/global-news/{date_prefix}-ai-{safe_name}.md"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response.text)

# Execute for all 4 regions
for region, focus in regions.items():
    try:
        generate_seo_article(region, focus)
    except Exception as e:
        print(f"Error generating {region}: {e}")
