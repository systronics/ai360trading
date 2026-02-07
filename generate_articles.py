import os
from datetime import datetime
import google.generativeai as genai

# Setup Gemini 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Correct 2026 tool declaration for Search Grounding
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
    
    # Prompt optimized for your Jekyll design
    prompt = (f"Using Google Search, write a professional educational analysis of current stock market trends in {market_focus}. "
              "Format the output as a Jekyll Markdown post. "
              "Include this EXACT front matter at the top: "
              "---\nlayout: post\ntitle: 'Global Market News: " + region_name + " Update'\n"
              "categories: [global-news]\n---")
    
    response = model.generate_content(prompt)
    
    # File naming to stay separate from your manual posts
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"_posts/{date_prefix}-ai-{region_name.lower()}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(response.text)

for region, focus in regions.items():
    try:
        generate_seo_article(region, focus)
    except Exception as e:
        print(f"Error for {region}: {str(e)}")
