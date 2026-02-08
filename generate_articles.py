import os
import pytz
from datetime import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

def generate_post():
    filename = f"{date_str}-market-update.md" # The stable filename
    path = os.path.join("_posts", filename)

    prompt = (
        f"Write a Jekyll post for Indian Market on {date_str}. "
        "Use Frontmatter: layout: post, title: 'Market Analysis', tags: [global-markets]."
    )

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = completion.choices[0].message.content
    if not os.path.exists("_posts"): os.makedirs("_posts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

if __name__ == "__main__":
    generate_post()
