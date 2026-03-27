import os, sys, json, random, asyncio, textwrap
from datetime import datetime
from pathlib import Path
import yfinance as yf
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip

OUT = Path("output")
OUT.mkdir(exist_ok=True)

def get_market_data():
    # Fetching Real-World Data for Human-Touch Analysis
    tickers = {
        "Nifty": "^NSEI", "BankNifty": "^NSEBANK", 
        "S&P500": "^GSPC", "BTC": "BTC-USD", 
        "Oil": "CL=F", "USDINR": "INR=X"
    }
    data_str = ""
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="2d")
            price = hist['Close'].iloc[-1]
            change = price - hist['Close'].iloc[-2]
            data_str += f"{name}: {price:.2f} ({change:+.2f}), "
        except: data_str += f"{name}: Data N/A, "
    return data_str

def generate_slides(client, market_data, mode):
    # Daily Perspective Rotation to avoid "AI-Template" feel
    perspectives = [
        "A Senior Institutional Mentor explaining 'Traps' to retail traders",
        "A Global Macro Expert linking War news and Oil prices to Nifty levels",
        "A Cautious Price-Action Trader focusing on 'Psychology of Support/Resistance'"
    ]
    chosen_voice = random.choice(perspectives)
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""You are a High-Level Market Strategist for ai360trading.in.
    Perspective: {chosen_voice}. Date: {today}. Mode: {mode}.
    Live Data: {market_data}

    TASK: Generate exactly 8 slides for a 15-MINUTE DEEP ANALYSIS in Hinglish.
    
    STRICT CONTENT RULES:
    1. Each slide's 'content' MUST be at least 250 words long (Total 2,000 words).
    2. Focus on: Global War impact, Oil price volatility, USD-INR pressure, and BTC-USD trends.
    3. Use Human Emotions: 'Doston, yahan panic mat kijiye', 'Bade players trap kar rahe hain'.
    4. NO AI-SPEAK: Avoid 'In conclusion', 'Firstly', 'Moreover'. Talk like a real trader.

    Respond ONLY with valid JSON:
    {{
      "video_title": "Viral Hinglish Title (Keywords: Nifty, S&P 500, War News)",
      "video_description": "Deep analysis of Global & Indian markets...",
      "slides": [
        {{
          "title": "Slide Title",
          "content": "250 words of deep human analysis...",
          "sentiment": "bullish/bearish/neutral"
        }}
      ]
    }}"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

async def make_video(client, mode):
    data = get_market_data()
    meta = generate_slides(client, data, mode)
    clips = []
    
    for i, s in enumerate(meta['slides']):
        aud_p = OUT / f"slide_{i}.mp3"
        communicate = edge_tts.Communicate(s['content'], "hi-IN-SwaraNeural")
        await communicate.save(str(aud_p))
        
        voice = AudioFileClip(str(aud_p))
        # ImageClip logic here (using your existing slide design)
        # For full code brevity, assuming slide_img_{i}.png is generated
        bg = ColorClip(size=(1920, 1080), color=(10, 20, 30)).set_duration(voice.duration + 0.5)
        clips.append(bg.set_audio(voice))

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(OUT / "analysis_video.mp4"), fps=24)
    # Save ID for Artifact Bridge
    (OUT / "analysis_video_id.txt").write_text("MANUAL_UPLOAD_ID") 

if __name__ == "__main__":
    # Integration with your existing Groq client
    pass
