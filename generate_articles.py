import os
import pytz
from datetime import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
ist = pytz.timezone('Asia/Kolkata')
date_str = datetime.now(ist).strftime("%Y-%m-%d")

def generate_post():
    # FILENAME: Simplified format from your working version
    filename = f"{date_str}-market-update.md"
    path = os.path.join("_posts", filename)

    prompt = (
        f"Write a professional Jekyll blog post for the Indian Stock Market on {date_str}. "
        "Use this EXACT Frontmatter:\n"
        "---\n"
        "layout: post\n"
        f"title: 'Market Analysis: {date_str}'\n"
        "categories: [Market-Update]\n"
        "tags: [global-markets]\n"
        "---\n\n"
        "Include sections for Nifty, BankNifty, and Global Cues. Bold all price levels."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        content = completion.choices[0].message.content
        # Remove markdown code blocks if AI adds them
        if content.startswith("```"):
            content = "\n".join(content.split("\n")[1:-1])

        if not os.path.exists("_posts"): os.makedirs("_posts")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"✅ Success: {filename} created.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_post()
