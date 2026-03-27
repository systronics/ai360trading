import os, json, random, asyncio
from pathlib import Path
import edge_tts
import yfinance as yf
from moviepy.editor import ColorClip, AudioFileClip

OUT = Path("output")

def get_morning_link():
    id_file = OUT / "analysis_video_id.txt"
    if id_file.exists():
        v_id = id_file.read_text().strip()
        return f"https://youtube.com/watch?v={v_id}"
    return "https://ai360trading.in"

async def generate_short_scripts(client):
    morning_url = get_morning_link()
    # Trending topics: War, Oil, Dollar-Rupee, BTC
    prompt = f"""Write 2 Viral 60-second Shorts in Hinglish for Real Traders.
    Topics: War News Impact, Oil Price Surge, USD-INR Volatility, and BTC Resistance.
    
    STRICT RULES:
    1. Each script MUST be 150 words exactly (for 60s duration).
    2. Start with a Hook: 'Breaking News jo market hila dega!'
    3. Call to Action: 'Full logic samjhne ke liye morning analysis dekhiye: {morning_url}'
    4. Tone: Urgent, Authoritative, Human. No robotic greetings.

    Respond ONLY with JSON:
    {{ "shorts": [ {{ "title": "T1", "content": "150 words...", "voice": "hi-IN-MadhurNeural" }} ] }}"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

async def main_shorts(client):
    scripts = await generate_short_scripts(client)
    for i, s in enumerate(scripts['shorts']):
        aud_p = OUT / f"short_{i}.mp3"
        comm = edge_tts.Communicate(s['content'], s['voice'])
        await comm.save(str(aud_p))
        
        voice = AudioFileClip(str(aud_p))
        # Create Vertical 9:16 Video
        bg = ColorClip(size=(1080, 1920), color=(20, 10, 10)).set_duration(voice.duration)
        bg.set_audio(voice).write_videofile(str(OUT / f"short_{i}.mp4"), fps=24)

if __name__ == "__main__":
    pass
