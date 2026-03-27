import os, sys, json, random, asyncio, textwrap
from datetime import datetime
from pathlib import Path
import yfinance as yf
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip, TextClip

OUT = Path("output")
OUT.mkdir(exist_ok=True)

def get_market_data():
    """Fetches real-time global and local market data."""
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
        except Exception: 
            data_str += f"{name}: Data N/A, "
    return data_str

def generate_slides(client, market_data, mode):
    """Generates 8 high-depth analysis slides with human-centric perspectives."""
    perspectives = [
        "A Senior Institutional Mentor explaining 'Traps' and 'Big Player' moves to retail traders",
        "A Global Macro Strategist linking Current War News, Oil Volatility, and USD-INR pressure to Indian Market levels",
        "A Cautious Price-Action Veteran focusing on 'Psychology of Support/Resistance' and the fear/greed cycle"
    ]
    chosen_voice = random.choice(perspectives)
    today = datetime.now().strftime("%Y-%m-%d")

    # This prompt forces the AI to provide massive detail per slide to ensure 15 min duration
    prompt = f"""You are a professional Market Strategist at ai360trading.in. 
    Perspective: {chosen_voice}. Date: {today}. Mode: {mode}.
    Live Market Data: {market_data}

    TASK: Generate exactly 8 slides for a 15-MINUTE DEEP ANALYSIS video in Hinglish.
    
    STRICT CONTENT RULES:
    1. Each slide 'content' MUST be at least 300 words long. This is non-negotiable for watch time.
    2. Daily Variety: Talk about Today's specific Trending Topics (War threats, Oil supply chaos, Dollar Index surges, or BTC dominance).
    3. Human Touch: Use phrases like 'Dhyan se dekhiye doston', 'Yahan retailers panic karenge', 'Bade players ka game samajhiye'.
    4. Market Logic: Explain the 'Why' behind every price level, not just the price itself.
    5. NO AI-Speak: Strictly avoid 'In conclusion', 'Moreover', 'Firstly'. Talk like a mentor on a live call.

    Respond ONLY with a valid JSON object:
    {{
      "video_title": "Viral SEO Hinglish Title (Keywords: Nifty, S&P 500, News Impact)",
      "video_description": "Deep professional analysis for real traders...",
      "slides": [
        {{
          "title": "Slide Title",
          "content": "300 words of deep, emotional, and technical analysis...",
          "sentiment": "bullish/bearish/neutral",
          "overlay_text": "Key Level to Watch"
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
    """Coordinates the AI generation, TTS, and video rendering."""
    print(f"[PROCESS] Fetching Market Data...")
    data = get_market_data()
    
    print(f"[PROCESS] Generating High-Depth Scripts...")
    meta = generate_slides(client, data, mode)
    
    clips = []
    
    for i, s in enumerate(meta['slides']):
        print(f"[PROGRESS] Processing Slide {i+1}/8...")
        
        # 1. Generate Voiceover
        aud_p = OUT / f"slide_{i}.mp3"
        communicate = edge_tts.Communicate(s['content'], "hi-IN-SwaraNeural")
        await communicate.save(str(aud_p))
        voice = AudioFileClip(str(aud_p))
        
        # 2. Create Dynamic Background with Slide Title
        # Using ColorClip for stability; you can replace with your manual image logic
        bg = ColorClip(size=(1920, 1080), color=(10, 15, 25)).set_duration(voice.duration + 0.5)
        
        # 3. Combine Audio and Visuals
        slide_clip = bg.set_audio(voice)
        clips.append(slide_clip)

    print(f"[PROCESS] Merging 15-Minute Analysis Video...")
    final = concatenate_videoclips(clips, method="compose")
    output_filename = str(OUT / "analysis_video.mp4")
    final.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    
    # 4. Save Metadata for Artifact Bridge
    # This ID should be replaced by your real YouTube Upload logic result
    (OUT / "analysis_video_id.txt").write_text("PENDING_ID") 
    print(f"✅ Video Complete: {output_filename}")

if __name__ == "__main__":
    # This part depends on how you initialize your Groq client in your main script
    pass
