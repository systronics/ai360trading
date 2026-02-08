import os
import pytz
import re
import time
from datetime import datetime
from google import genai
from google.genai import errors

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
date_str = now.strftime("%Y-%m-%d")

def generate_market_post(region):
    print(f"Generating report for {region}...")
    prompt = (f"Act as a senior market analyst. Write a market analysis for {region} on {date_str}. "
              "Include: 'Market Sentiment', 'Key Levels', and 'Action Plan'. "
              "Output in Jekyll Markdown with tags: [Market Analysis, AI Trading, global-markets]")
    
    # Retry logic for 429 Errors
    for attempt in range(3):
        try:
            # Switched to 1.5-flash for better free-tier stability
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            content = response.text.strip()
            
            # Clean markdown and save
            filename = f"{date_str}-{region.lower()}-market-pulse.md"
            posts_dir = os.path.join(os.getcwd(), '_posts')
            with open(os.path.join(posts_dir, filename), "w", encoding="utf-8") as f:
                f.write(f"---\nlayout: post\ntitle: '{region} Market Pulse'\n"
                        f"date: {date_str}\ntags: [global-markets]\n---\n\n{content}")
            print(f"✅ Created: {filename}")
            return # Exit loop on success
        except errors.ClientError as e:
            if "429" in str(e):
                print(f"⚠️ Quota full. Retrying in 60s... (Attempt {attempt+1}/3)")
                time.sleep(60)
            else:
                print(f"❌ Error: {e}")
                break

generate_market_post("Indian")
