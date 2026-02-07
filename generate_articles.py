import os
import google.generativeai as genai
from datetime import datetime

# 1. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash', tools=[{'google_search': {}}])

regions = ["US", "UK", "Europe", "Asia"]

def create_article(region):
    prompt = f"Write a professional educational analysis of the current week's stock market trends in {region}. Focus on educational value for traders. Format as Jekyll Markdown with front matter: title, date, and category 'global-news'."
    
    response = model.generate_content(prompt)
    content = response.text
    
    # 2. File Naming (avoids overwriting manual posts)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"_posts/{date_str}-ai-news-{region.lower()}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# Run for all regions
for r in regions:
    create_article(r)
