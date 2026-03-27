import os
import asyncio
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from moviepy.editor import *
from moviepy.video.fx.all import resize
from datetime import datetime
import pytz
import edge_tts

# --- SEO & BRANDING CONFIG ---
BRAND_NAME = "AI360Trading"
TELEGRAM_URL = "t.me/ai360trading"
WEBSITE_URL = "ai360trading.in"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
IST = pytz.timezone('Asia/Kolkata')

async def generate_voiceover(text, output_path):
    """Professional Global Voiceover (English-Indian accent for trust)"""
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural")
    await communicate.save(output_path)

def get_market_data():
    """Live Market Stats for Global Growth"""
    tickers = {"NIFTY": "GIFTY=F", "BITCOIN": "BTC-USD", "S&P 500": "^GSPC"}
    stats = {}
    for name, symbol in tickers.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="1d", interval="15m")
            price = hist['Close'].iloc[-1]
            change = ((price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            stats[name] = {"p": f"{price:,.1f}", "c": f"{change:+.2f}%", "color": "green" if change >= 0 else "red", "hist": hist['Close']}
        except: pass
    return stats

def generate_seo_metadata(stats):
    """Dynamic Caption & Description for Algorithm Boost"""
    nifty_p = stats.get('NIFTY', {}).get('p', 'Data N/A')
    btc_p = stats.get('BITCOIN', {}).get('p', 'Data N/A')
    
    # Auto-Translation Logic: Mix of Global English and Indian Context
    caption = f"🚀 Market Update: Nifty @ {nifty_p} | BTC @ {btc_p}"
    
    description = (
        f"📊 {BRAND_NAME} Daily Pulse - {datetime.now(IST).strftime('%d %b %Y')}\n\n"
        f"Aaj ka market sentiment global aur domestic levels pe setup ho raha hai.\n"
        f"Current Status:\n"
        f"✅ Gift Nifty: {nifty_p}\n"
        f"✅ Bitcoin: {btc_p}\n\n"
        f"Join our community for high-conviction trade setups:\n"
        f"📱 Telegram: {TELEGRAM_URL}\n"
        f"🌐 Web: {WEBSITE_URL}\n\n"
        f"#StockMarket #Nifty50 #TradingIndia #CryptoNews #S&P500 #Investing #AI360Trading #TechnicalAnalysis"
    )
    return caption, description

def create_short_video():
    stats = get_market_data()
    caption, description = generate_seo_metadata(stats)
    
    # 1. AUDIO GENERATION
    audio_text = f"Welcome to AI 360 Trading. Gift Nifty is trading at {stats['NIFTY']['p']}. Bitcoin is at {stats['BITCOIN']['p']}. Global sentiment looks { 'positive' if '+' in stats['S&P 500']['c'] else 'cautious' }. Check our Telegram for levels."
    audio_path = os.path.join(OUTPUT_DIR, "short_audio.mp3")
    asyncio.run(generate_voiceover(audio_text, audio_path))
    
    # 2. VISUALS
    bg = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=12)
    
    # Brand Watermark (Top Right)
    brand = TextClip(BRAND_NAME, fontsize=45, color='orange', font='Ubuntu-Bold', kerning=2).set_position((700, 50)).set_duration(12)
    
    # Main Headline
    head = TextClip("GLOBAL MARKET LIVE", fontsize=85, color='white', font='Ubuntu-Bold').set_position(('center', 150)).set_duration(12)
    
    # Data Rows Construction
    clips = [bg, brand, head]
    y_pos = 450
    for name, info in stats.items():
        txt = TextClip(f"{name}: {info['p']} ({info['c']})", fontsize=65, color=info['color'], font='Ubuntu-Bold').set_position((80, y_pos)).set_duration(12)
        clips.append(txt)
        y_pos += 350

    # Telegram CTA (Bottom)
    cta = TextClip(f"JOIN: {TELEGRAM_URL}", fontsize=55, color='yellow', font='Ubuntu-Bold', bg_color='black').set_position(('center', 1700)).set_duration(12)
    clips.append(cta)

    # 3. ASSEMBLY
    video = CompositeVideoClip(clips)
    audio = AudioFileClip(audio_path)
    final_video = video.set_audio(audio)
    
    output_file = os.path.join(OUTPUT_DIR, "viral_market_short.mp4")
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")
    
    # SAVE SEO FILE FOR MANUAL UPLOAD OR API
    with open(os.path.join(OUTPUT_DIR, "seo_meta.txt"), "w", encoding="utf-8") as f:
        f.write(f"TITLE: {caption}\n\nDESCRIPTION:\n{description}")
    
    return output_file

if __name__ == "__main__":
    create_short_video()
