import os
import pytz
import re
from datetime import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")

def generate_market_post(region):
    filename = f"{date_str}-{region.lower()}-market-pulse.md"
    posts_dir = os.path.join(os.getcwd(), '_posts')
    file_path = os.path.join(posts_dir, filename)

    prompt = (
        f"Write a Jekyll blog post for {region} market on {date_str}. "
        "Use this EXACT Frontmatter format:\n"
        "---\n"
        "layout: post\n"
        f"title: '{region} Market Analysis {date_str}'\n"
        "categories: [blog]\n"
        "tags: [global-markets]\n"
        "---\n"
        "## Daily Market Report\n"
        "Provide a summary of Nifty and BankNifty levels."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = completion.choices[0].message.content
        content = re.sub(r'^```[a-zA-Z]*\n|```$', '', content, flags=re.MULTILINE)

        if not os.path.exists(posts_dir):
            os.makedirs(posts_dir)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"✅ Created: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_market_post("Indian")
