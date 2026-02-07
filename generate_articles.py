import os
from datetime import datetime
import google.generativeai as genai

# Setup Gemini with the 2026 stable tool format
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use the stable Search tool declaration
tools = [{"google_search_retrieval": {}}]
model = genai.GenerativeModel('gemini-1.5-flash', tools=tools)

regions = {
    "US": "Wall Street and NASDAQ Trends",
    "UK": "London Stock Exchange (FTSE 100)",
    "Europe": "European Markets (DAX, CAC 40)",
    "Asia": "Asian Markets (Nikkei, Hang Seng)"
}

def generate_seo_article(region_name, market_focus):
    print(f"Generating article for {region_name}...")
    
    prompt = f"Using Google Search, write a 300-word educational analysis of current stock trends in {market_focus}. Output as Jekyll Markdown with layout: post and categories: [global-news]."
    
    # Use the corrected generation call
    response = model.generate_content(prompt)
    
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"_posts/{date_prefix}-ai-{region_name.lower()}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(response.text)

for region, focus in regions.items():
    try:
        generate_seo_article(region, focus)
    except Exception as e:
        print(f"Error for {region}: {str(e)}")
