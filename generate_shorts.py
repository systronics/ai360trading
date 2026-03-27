import os, sys, json, random, asyncio
from pathlib import Path
import yfinance as yf
import edge_tts
from moviepy.editor import ColorClip, AudioFileClip, TextClip, CompositeVideoClip

OUT = Path("output")
OUT.mkdir(exist_ok=True)

def get_morning_video_link():
    """
    The Artifact Bridge: Reads the Video ID saved by generate_analysis.py 
    to interlink the morning video into the mid-day short.
    """
    id_file = OUT / "analysis_video_id.txt"
    if id_file.exists():
        v_id = id_file.read_text().strip()
        # Fallback if the ID hasn't been updated from 'PENDING_ID' yet
        if v_id and v_id != "PENDING_ID":
            return f"https://youtube.com/watch?v={v_id}"
    return "https://ai360trading.in"

def get_midday_data():
    """Fetches trending news-related data: Oil, War-impact assets, and BTC."""
    tickers = {
        "Nifty": "^NSEI", "BankNifty": "^NSEBANK",
        "Crude_Oil": "CL=F", "USD_INR": "INR=X",
        "Bitcoin": "BTC-USD", "Gold": "GC=F"
    }
    data_str = ""
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            price = t.history(period="1d")['Close'].iloc[-1]
            data_str += f"{name}: {price:.2f}, "
        except: pass
    return data_str

async def generate_short_scripts(client):
    """Generates 2 high-retention 60-second scripts with real trader news."""
    morning_link = get_morning_video_link()
    midday_info = get_midday_data()
    
    # Rotating Human Perspectives for Daily Variety
    perspectives = [
        "A News Anchor reporting live from the trading floor",
        "A Professional Scalper spotting a mid-day trap",
        "A Global Analyst reacting to sudden news (War/Oil/Dollar)"
    ]
    view = random.choice(perspectives)

    prompt = f"""Write 2 Viral 60-second Shorts in Hinglish for ai360trading.in.
    Perspective: {view}. Mid-day Data: {midday_info}
    
    CONTENT THEMES:
    Short 1: 'The News Impact' (Focus on War news, Oil prices, USD-INR volatility).
    Short 2: 'Mid-day Levels' (Focus on Nifty/BankNifty Support/Resistance + BTC levels).

    STRICT RULES (For Human Touch & 60s Duration):
    1. Each script MUST be exactly 150 words long. 
    2. Start with a Hook: 'Breaking News jo market hila dega!' or 'Doston, bade players trap kar rahe hain!'
    3. Emotion: Use Human Fear/Greed triggers. Talk about 'Liquidity hunts' and 'News traps'.
    4. Call to Action: 'Iska full logic hamare morning analysis video mein hai: {morning_link}'
    5. NO AI-SPEAK: Avoid 'Greetings', 'In conclusion', 'Stay tuned'.

    Respond ONLY with JSON:
    {{
      "shorts": [
        {{
          "title": "Viral Title",
          "content": "150 words of urgent, emotional trader news...",
          "voice": "hi-IN-MadhurNeural"
        }},
        {{
          "title": "Viral Title 2",
          "content": "150 words of energetic price action news...",
          "voice": "hi-IN-SwaraNeural"
        }}
      ]
    }}"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

async def make_shorts(client):
    """Processes the scripts into 9:16 vertical videos."""
    print(f"[PROCESS] Generating 60-Second Short Scripts...")
    meta = await generate_short_scripts(client)
    
    for i, s in enumerate(meta['shorts']):
        print(f"[PROGRESS] Creating Short {i+1}/2...")
        
        # 1. Voiceover Generation
        aud_p = OUT / f"short_{i}.mp3"
        comm = edge_tts.Communicate(s['content'], s['voice'])
        await comm.save(str(aud_p))
        voice = AudioFileClip(str(aud_p))
        
        # 2. Vertical Background (9:16)
        # Deep dark red for News Impact, Deep blue for Levels
        color = (30, 5, 5) if i == 0 else (5, 10, 30)
        bg = ColorClip(size=(1080, 1920), color=color).set_duration(voice.duration + 0.5)
        
        # 3. Assemble Final Short
        short_clip = bg.set_audio(voice)
        output_file = str(OUT / f"short_{i}_final.mp4")
        short_clip.write_videofile(output_file, fps=24, codec="libx264")
        print(f"✅ Short {i+1} saved: {output_file}")

if __name__ == "__main__":
    # Integration with your specific Groq client setup
    pass
