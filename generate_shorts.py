import os
import asyncio
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from moviepy.editor import *
from datetime import datetime
import pytz
import edge_tts

# --- BRANDING & SEO SETTINGS ---
BRAND = "AI360Trading"
TELEGRAM = "https://t.me/ai360trading"
WEBSITE = "ai360trading.in"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
IST = pytz.timezone('Asia/Kolkata')

async def make_voice(text, path):
    """Clean professional voiceover"""
    comm = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
    await comm.save(path)

def fetch_market_pulse():
    """Live data for the visual trust factor"""
    stats = {}
    # Nifty (Gift), Bitcoin, S&P 500
    tickers = {"NIFTY": "GIFTY=F", "BITCOIN": "BTC-USD", "S&P 500": "^GSPC"}
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="1d", interval="15m")
            curr = h['Close'].iloc[-1]
            change = ((curr - h['Close'].iloc[0]) / h['Close'].iloc[0]) * 100
            stats[name] = {"p": f"{curr:,.1f}", "c": f"{change:+.2f}%", "color": "green" if change >= 0 else "red"}
        except: pass
    return stats

def get_viral_meta(stats):
    """Generates the SEO Package for YouTube/Instagram"""
    nifty = stats.get('NIFTY', {}).get('p', 'N/A')
    btc = stats.get('BITCOIN', {}).get('p', 'N/A')
    
    # 1. THE HOOK (Caption)
    caption = f"🚨 Market Shock? Nifty @ {nifty} | BTC Move!"
    
    # 2. THE DESCRIPTION (SEO + Translation)
    # Mixing Hindi and English for high engagement
    description = (
        f"📊 {BRAND} Daily Market Update - {datetime.now(IST).strftime('%d %b %Y')}\n\n"
        f"Global markets are moving fast! 🌍\n"
        f"Gift Nifty current level: {nifty}\n"
        f"Bitcoin price action: {btc}\n\n"
        f"Doston, levels ko dhyan se follow karein. Live setups ke liye Telegram join karein! 👇\n"
        f"🚀 Join Telegram: {TELEGRAM}\n"
        f"🌐 Website: {WEBSITE}\n\n"
        f"--- VIRAL HASHTAGS ---\n"
        f"#Shorts #Trading #Nifty50 #BitcoinNews #StockMarketIndia #Investing2026 #AI360Trading #PriceAction"
    )
    return caption, description

def create_viral_short():
    data = fetch_market_pulse()
    cap, desc = get_viral_meta(data)
    
    # 1. Voiceover (10-12 seconds is best for 100% completion rate)
    script = f"Quick market update from {BRAND}. Gift Nifty is at {data['NIFTY']['p']}. Bitcoin is trading at {data['BITCOIN']['p']}. Join our Telegram for the full trade plan."
    audio_file = os.path.join(OUTPUT_DIR, "v_audio.mp3")
    asyncio.run(make_voice(script, audio_file))
    
    # 2. Vertical Visuals (1080x1920)
    bg = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=11)
    
    # Branding Header
    brand_tag = TextClip(f"@{BRAND}", fontsize=50, color='orange', font='Ubuntu-Bold').set_position(('center', 80)).set_duration(11)
    
    # Live Data Rows
    y_pos = 400
    rows = []
    for name, info in data.items():
        row = TextClip(f"{name}: {info['p']} ({info['c']})", fontsize=75, color=info['color'], font='Ubuntu-Bold')
        rows.append(row.set_position((100, y_pos)).set_duration(11))
        y_pos += 400

    # Call to Action (CTA)
    cta = TextClip("LINK IN BIO / DESCRIPTION", fontsize=60, color='yellow', font='Ubuntu-Bold', bg_color='red').set_position(('center', 1700)).set_duration(11)
    
    # 3. Final Render
    final = CompositeVideoClip([bg, brand_tag, *rows, cta])
    final.audio = AudioFileClip(audio_file)
    
    output_path = os.path.join(OUTPUT_DIR, "viral_short.mp4")
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    
    # 4. Export SEO Text for you to copy
    with open(os.path.join(OUTPUT_DIR, "SEO_GUIDE.txt"), "w", encoding="utf-8") as f:
        f.write(f"--- TITLE ---\n{cap}\n\n--- DESCRIPTION ---\n{desc}")

if __name__ == "__main__":
    create_viral_short()
