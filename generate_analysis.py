import os, json, asyncio
from datetime import datetime
import pytz
import yfinance as yf
from pathlib import Path
from groq import Groq

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUT = Path("output")
IST = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(IST)
os.makedirs(OUT, exist_ok=True)

# ─── CACHE-BUSTING DATA FETCH ────────────────────────────────────────────────
def get_live_market_snapshot():
    """Fetches high-accuracy live data to share with Shorts/Reels."""
    print("📊 Fetching Market Snapshot for AI360TRADING...")
    
    tickers = {
        "nifty": "^NSEI",
        "btc": "BTC-USD",
        "gold": "GC=F",
        "sp500": "^GSPC"
    }
    
    snapshot = {}
    for name, sym in tickers.items():
        try:
            # interval="1m" forces GitHub to pull NEW data, not cached data
            df = yf.download(sym, period="1d", interval="1m", progress=False)
            if df.empty:
                df = yf.download(sym, period="5d", interval="1d", progress=False)
            
            current_price = float(df["Close"].iloc[-1])
            open_price = float(df["Open"].iloc[0])
            change_pct = ((current_price - open_price) / open_price) * 100
            
            snapshot[name] = {
                "price": round(current_price, 2),
                "change": f"{change_pct:+.2f}%",
                "is_bullish": change_pct >= 0,
                "timestamp": now_ist.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"⚠️ Error fetching {name}: {e}")
            snapshot[name] = {"price": 0, "change": "0.00%", "is_bullish": True}
            
    return snapshot

# ─── MAIN ANALYSIS ENGINE ────────────────────────────────────────────────────
async def run_analysis():
    # 1. Get Fresh Data
    market_data = get_live_market_snapshot()
    
    # 2. Save for SHORTS (This stops the 'Old Data' bug)
    today_str = now_ist.strftime("%Y%m%d")
    data_file = OUT / f"market_snapshot_{today_str}.json"
    
    with open(data_file, "w") as f:
        json.dump(market_data, f, indent=4)
    print(f"✅ Market Snapshot saved: {data_file}")

    # 3. Generate Script for Main Video via Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Custom Prompt for your "Worldwide/Beginner" Brand
    prompt = f"""
    Write a professional 2-minute market analysis script.
    Data: Nifty is at {market_data['nifty']['price']} ({market_data['nifty']['change']}).
    Focus on: Global trends and simple logic for beginners.
    Tone: Expert yet encouraging.
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    
    main_script = chat_completion.choices[0].message.content
    
    # 4. Save Metadata for the Workflow 'Handshake'
    meta = {
        "title": f"Market Analysis {now_ist.strftime('%d %b %Y')}",
        "script": main_script,
        "video_url": "PENDING_UPLOAD", # Updated after YouTube upload step
        "market_data": market_data
    }
    
    meta_path = OUT / f"analysis_meta_{today_str}.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=4)
        
    print("✅ Analysis Metadata created for YouTube & Shorts.")

if __name__ == "__main__":
    asyncio.run(run_analysis())
