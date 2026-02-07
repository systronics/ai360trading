import os
from datetime import datetime
import google.generativeai as genai

# Setup Gemini 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash', tools=[{"google_search_retrieval": {}}])

# Force the folder to be in the repository root
# This ensures it doesn't create a 'ghost' _posts folder elsewhere
base_dir = os.path.dirname(os.path.abspath(__file__))
posts_dir = os.path.join(base_dir, '_posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)
    print(f"Created directory at: {posts_dir}")

regions = {
    "US": "Wall Street and NASDAQ",
    "UK": "London Stock Exchange",
    "Europe": "DAX and CAC 40",
    "Asia": "Nikkei and Hang Seng"
}

def generate_article(region, focus):
    print(f"Generating for {region}...")
    prompt = (f"Using Google Search, write a 300-word stock market update for {focus}. "
              "Output as Jekyll Markdown. Front matter must include: "
              f"layout: post, title: 'Global News: {region} Market', categories: [global-news].")
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Strip markdown wrappers if AI adds them
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:-1])

    filename = f"{datetime.now().strftime('%Y-%m-%d')}-ai-{region.lower()}.md"
    file_path = os.path.join(posts_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"File saved: {file_path}")

for region, focus in regions.items():
    try:
        generate_article(region, focus)
    except Exception as e:
        print(f"Error: {e}")
