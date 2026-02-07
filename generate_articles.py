import os
from datetime import datetime
import google.generativeai as genai

# Setup Gemini with API Key from GitHub Secrets
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Tool declaration for real-time market data
tools = [{"google_search_retrieval": {}}]
model = genai.GenerativeModel('gemini-1.5-flash', tools=tools)

regions = {
    "US": "Wall Street and NASDAQ",
    "UK": "London Stock Exchange",
    "Europe": "DAX and CAC 40",
    "Asia": "Nikkei and Hang Seng"
}

def generate_article(region, focus):
    print(f"Generating for {region}...")
    prompt = (f"Search for the latest stock market trends in {focus}. "
              "Write a 300-word educational update. Output as Jekyll Markdown. "
              "Start exactly with this front matter:\n---\nlayout: post\n"
              f"title: 'Global Market Insights: {region} Update'\n"
              "categories: [global-news]\n---")
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    # Remove AI's markdown code blocks if present
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:-1])

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"_posts/{date_str}-ai-{region.lower()}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

for region, focus in regions.items():
    try:
        generate_article(region, focus)
    except Exception as e:
        print(f"Error for {region}: {e}")
