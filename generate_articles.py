import os
from datetime import datetime
import google.generativeai as genai

# Configuration
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash', tools=[{"google_search_retrieval": {}}])

# Force path to the root _posts folder
repo_root = os.getcwd()
posts_dir = os.path.join(repo_root, '_posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)
    print(f"Created directory: {posts_dir}")

regions = ["US", "UK", "Europe", "Asia"]

def generate_article(region):
    print(f"Generating article for {region}...")
    prompt = (f"Search for the latest stock market news in {region}. "
              "Write a 300-word analysis. Output as Jekyll Markdown. "
              "Include front matter: layout: post, title: 'Global News: {region} Update', categories: [global-news].")
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    # Remove AI markdown blocks
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:-1])

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-ai-{region.lower()}.md"
    file_path = os.path.join(posts_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: Saved {filename} to {posts_dir}")

for r in regions:
    try:
        generate_article(r)
    except Exception as e:
        print(f"Error for {r}: {e}")
