import os
from datetime import datetime
from google import genai
from google.genai import types

# Setup Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_ID = "gemini-1.5-flash"

# Targeted regions with specific SEO Keywords
regions = {
    "US": {"focus": "Wall Street and NASDAQ", "tags": "NASDAQ, NYSE, US-Economy"},
    "UK": {"focus": "London Stock Exchange", "tags": "FTSE100, London-Finance, LSE"},
    "Europe": {"focus": "DAX and CAC 40", "tags": "Eurozone, ECB, Frankfurt-Exchange"},
    "Asia": {"focus": "Nikkei and Hang Seng", "tags": "Tokyo-Market, Asia-Pivot, Hong-Kong-Finance"}
}

def generate_seo_article(region_name, data):
    print(f"Generating article for {region_name}...")
    
    prompt = f"""
    Search for the top 3 market educational trends for {data['focus']} this week.
    Write a 300-word educational article.
    
    Output ONLY the Jekyll Markdown content starting with this Front Matter:
    ---
    layout: post
    title: "Global Market Insights: {region_name} Update"
    categories: [global-news]
    tags: [{data['tags']}]
    excerpt: "Educational breakdown of the latest trends in the {region_name} stock markets."
    ---
    
    (Write the article here using Markdown headers)
    """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]
        )
    )
    
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"_posts/{date_prefix}-ai-{region_name.lower()}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(response.text)

for region, data in regions.items():
    try:
        generate_seo_article(region, data)
    except Exception as e:
        print(f"Error for {region}: {e}")
