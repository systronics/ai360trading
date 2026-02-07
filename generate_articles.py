import os
import pytz
from datetime import datetime
import google.generativeai as genai

# Setup
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash', tools=[{"google_search_retrieval": {}}])

# Force IST Timezone
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist)
date_str = current_time.strftime("%Y-%m-%d")

# Root path check
posts_dir = os.path.join(os.getcwd(), '_posts')
if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

regions = ["US", "UK", "Europe", "Asia"]

def generate_article(region):
    print(f"Generating article for {region} in IST context...")
    prompt = (f"Provide a 300-word stock market update for {region}. "
              "Output MUST start with this Jekyll front matter:\n"
              "---\nlayout: post\n"
              f"title: 'Market Update: {region}'\n"
              "categories: [global-news]\n---\n")
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:-1])

    filename = f"{date_str}-ai-{region.lower()}.md"
    file_path = os.path.join(posts_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Verified: Saved {filename} to _posts")

for r in regions:
    try:
        generate_article(r)
    except Exception as e:
        print(f"Error: {e}")
