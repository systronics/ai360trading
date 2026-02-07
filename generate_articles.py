import os
from datetime import datetime
import google.generativeai as genai

# Configuration
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash', tools=[{"google_search_retrieval": {}}])

# Identify the absolute root of your repository
repo_root = os.getcwd()
posts_dir = os.path.join(repo_root, '_posts')

# Create directory if it somehow doesn't exist
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)
    print(f"Created: {posts_dir}")

regions = ["US", "UK", "Europe", "Asia"]

def generate_article(region):
    print(f"--- Generating for {region} ---")
    prompt = f"Write a 300-word stock update for {region}. Output in Jekyll Markdown format with layout: post and categories: [global-news]."
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Clean AI code blocks (```markdown ... ```)
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:-1])

    filename = f"{datetime.now().strftime('%Y-%m-%d')}-ai-{region.lower()}.md"
    file_path = os.path.join(posts_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    # Check if file actually exists before finishing
    if os.path.exists(file_path):
        print(f"VERIFIED: {filename} exists at {file_path}")
    else:
        raise Exception(f"Failed to write {filename}")

for r in regions:
    generate_article(r)
