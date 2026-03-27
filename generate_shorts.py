import os
import sys
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip
from datetime import datetime
import pytz

# --- CONFIGURATION ---
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
IST = pytz.timezone('Asia/Kolkata')

def get_market_data():
    """Fetch live data for Global & Indian Markets"""
    print("[DATA] Fetching live market stats...")
    # Nifty Futures (Gift Nifty), Bitcoin, S&P 500
    tickers = {
        "NIFTY": "GIFTY=F", 
        "BITCOIN": "BTC-USD", 
        "S&P 500": "^GSPC"
    }
    
    stats = {}
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            # Fetch last 24h data for a small sparkline chart
            hist = ticker.history(period="1d", interval="15m")
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[0]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            stats[name] = {
                "price": f"{current_price:,.2f}",
                "change": f"{change_pct:+.2f}%",
                "color": "green" if change_pct >= 0 else "red",
                "history": hist['Close']
            }
        except Exception as e:
            print(f"[WARN] Could not fetch {name}: {e}")
    return stats

def generate_sparkline(name, data_series, color):
    """Generate a clean, human-style chart for the Short"""
    plt.figure(figsize=(4, 2), facecolor='none')
    ax = plt.axes([0, 0, 1, 1], frameon=False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    
    plt.plot(data_series.values, color=color, linewidth=4)
    chart_path = os.path.join(OUTPUT_DIR, f"chart_{name.lower()}.png")
    plt.savefig(chart_path, transparent=True, dpi=150)
    plt.close()
    return chart_path

def create_short_video():
    """Construct the Vertical Short with Live Data"""
    stats = get_market_data()
    today_str = datetime.now(IST).strftime("%d %b, %H:%M IST")
    
    # 1. Background (Solid Dark Professional Theme)
    bg = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=15)
    
    # 2. Header
    title = TextClip("LIVE MARKET PULSE", fontsize=80, color='white', font='Ubuntu-Bold')
    title = title.set_position(('center', 100)).set_duration(15)
    
    time_text = TextClip(today_str, fontsize=40, color='gray', font='Ubuntu')
    time_text = time_text.set_position(('center', 200)).set_duration(15)

    clips = [bg, title, time_text]
    
    # 3. Data Rows
    y_offset = 350
    for name, info in stats.items():
        # Text Label
        txt = TextClip(f"{name}: {info['price']} ({info['change']})", 
                       fontsize=60, color=info['color'], font='Ubuntu-Bold')
        txt = txt.set_position((100, y_offset)).set_duration(15)
        clips.append(txt)
        
        # Sparkline Chart
        chart_file = generate_sparkline(name, info['history'], info['color'])
        chart_img = ImageClip(chart_file).set_duration(15).resize(width=400)
        chart_img = chart_img.set_position((600, y_offset - 40))
        clips.append(chart_img)
        
        y_offset += 300

    # 4. Branding (AI360Trading)
    footer = TextClip("ai360trading.in", fontsize=50, color='orange', font='Ubuntu-Bold')
    footer = footer.set_position(('center', 1750)).set_duration(15)
    clips.append(footer)

    # 5. Export
    final_video = CompositeVideoClip(clips)
    video_path = os.path.join(OUTPUT_DIR, "daily_market_short.mp4")
    
    print("[VIDEO] Rendering final short...")
    final_video.write_videofile(video_path, fps=24, codec="libx264", audio=False)
    return video_path

if __name__ == "__main__":
    try:
        path = create_short_video()
        print(f"✅ Success! Short generated at: {path}")
    except Exception as e:
        print(f"❌ Error: {e}")
