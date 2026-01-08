import os, json, gspread, requests, pandas as pd, pyotp, pytz
from dhanhq import dhanhq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIG ---
LIVE_MODE = False  
MAX_ACTIVE_SLOTS = 5  

def get_dhan_client():
    client_id = os.environ.get('DHAN_CLIENT_ID')
    totp_key = os.environ.get('DHAN_TOTP_KEY')
    pin = os.environ.get('DHAN_PIN')
    totp_gen = pyotp.TOTP(totp_key)
    
    temp_client = dhanhq(client_id, "")
    auth_data = temp_client.generate_token(pin, totp_gen.now())
    access_token = auth_data.get('access_token') or auth_data.get('data', {}).get('access_token')
    return dhanhq(client_id, access_token)

def send_telegram(message):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=15)
    except Exception as e:
        print(f"Telegram failed: {e}")

def to_f(val):
    """Convert value to float, handling various formats"""
    if not val: return 0.0
    clean = str(val).replace(',', '').replace('₹', '').replace('%', '').strip()
    try:
        return float(clean)
    except:
        return 0.0

def run_trading_cycle():
    try:
        # 1. Setup Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_data = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        if not creds_data:
            print("Error: GCP_SERVICE_ACCOUNT_JSON not found")
            return
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_data), scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ai360tradingAlgo").worksheet("AlertLog")

        # 2. Kill Switch Check
        kill_switch = str(sheet.acell("O2").value).strip().upper()
        if kill_switch != "YES":
            print(f"🛑 Kill Switch is {kill_switch}. Stopping.")
            return

        # 3. Get Data
        all_values = sheet.get_all_values()
        if len(all_values) < 2: return
        data_rows = all_values[1:]
        
        # Filter for active trades in slot check
        active_trades = [r for r in data_rows if len(r) > 10 and "TRADED" in str(r[10]).upper() and "EXITED" not in str(r[10]).upper()]
        active_count = len(active_trades)

        # 4. Process Rows - MONITOR & EXIT
        for i, row in enumerate(data_rows):
            row_num = i + 2
            if len(row) < 12: continue 

            symbol = str(row[1]).strip()
            status = str(row[10]).strip().upper()
            if not symbol: continue

            try:
                price = to_f(row[2])         # Column C
                sl = to_f(row[7])            # Column H
                target = to_f(row[8])        # Column I
                entry_price = to_f(row[11])  # Column L
            except ValueError:
                continue

            # --- CASE A: MONITOR EXIT & TRAILING ---
            if "TRADED" in status and "EXITED" not in status:
                profit_pct = 0
                if entry_price > 0:
                    profit_pct = ((price - entry_price) / entry_price) * 100

                # --- TRAILING LOGIC ---
                new_sl = sl
                if profit_pct >= 4.0:
                    trail_at_2_pct = entry_price * 1.02
                    if trail_at_2_pct > sl:
                        new_sl = trail_at_2_pct
                elif profit_pct >= 2.0:
                    if entry_price > sl:
                        new_sl = entry_price

                if new_sl > sl:
                    sheet.update_cell(row_num, 8, round(new_sl, 2)) # Update Column H
                    send_telegram(f"🛡️ <b>TSL UPDATED:</b> {symbol}\nSL moved to: ₹{round(new_sl, 2)}\nCurrent Profit: {round(profit_pct, 1)}%")
                    sl = new_sl 

                # --- EXIT CHECK ---
                is_target_hit = target > 0 and price >= target
                is_sl_hit = sl > 0 and price <= sl

                if is_target_hit or is_sl_hit:
                    label = "TARGET 🎯" if is_target_hit else "STOPLOSS 🛑"
                    send_telegram(f"💰 <b>PAPER EXIT:</b> {symbol} @ {price}\nResult: {label}")
                    sheet.update_cell(row_num, 11, f"EXITED ({label})")
                    active_count -= 1

            # --- CASE B: NEW SIGNAL (Entry) ---
            elif status == "" and symbol:
                if active_count < MAX_ACTIVE_SLOTS:
                    # Update status first to lock the slot
                    sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                    # Store Entry Price in Column L
                    sheet.update_cell(row_num, 12, price) 
                    
                    send_telegram(f"🚀 <b>PAPER ENTRY:</b> {symbol} @ {price}\nTarget: {target} (6%)\nSL: {sl} (1.5%)\nSlot: {active_count+1}/5")
                    active_count += 1
                else:
                    print(f"⏳ Slots full. {symbol} skipped.")

        # 5. AUTO-PROMOTE WAITING STOCKS (After monitoring exits)
        if active_count < MAX_ACTIVE_SLOTS:
            print(f"🔄 Checking for WAITING stocks to promote... (Active: {active_count}/{MAX_ACTIVE_SLOTS})")
            
            for i, row in enumerate(data_rows):
                row_num = i + 2
                if len(row) < 12: continue
                
                symbol = str(row[1]).strip()
                status = str(row[10]).strip().upper()
                
                if not symbol: continue
                
                # Promote WAITING stocks to active
                if "WAITING" in status and active_count < MAX_ACTIVE_SLOTS:
                    try:
                        price = to_f(row[2])
                        sl = to_f(row[7])
                        target = to_f(row[8])
                        
                        # Promote: Clear status so it becomes active, then trade it
                        sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                        sheet.update_cell(row_num, 12, price)
                        
                        send_telegram(f"⬆️ <b>PROMOTED & ENTERED:</b> {symbol} @ {price}\nTarget: {target} (6%)\nSL: {sl} (1.5%)\nSlot: {active_count+1}/5")
                        active_count += 1
                        print(f"✅ Promoted {symbol} from WAITING to ACTIVE")
                    except Exception as e:
                        print(f"Failed to promote {symbol}: {e}")

        # 6. Count waiting stocks for display
        waiting_count = sum(1 for r in data_rows if len(r) > 10 and "WAITING" in str(r[10]).upper())

        # 7. Heartbeat Update
        now_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S')
        sheet.update_acell("O3", f"Bot Live | Active: {active_count}/5 | Waiting: {waiting_count} | {now_time}")

    except Exception as e:
        print(f"System Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_trading_cycle()
```

## Key Changes Made:

### 1. **Moved `to_f()` function outside** (line 26)
- Now can be used throughout the code

### 2. **Auto-Promotion Logic** (lines 107-129)
- After monitoring exits, checks if slots are available
- Automatically promotes WAITING stocks to ACTIVE
- Sends Telegram notification when promoted
- Updates status to "TRADED (PAPER)"

### 3. **Waiting Count Display** (lines 131-132)
- Counts how many stocks are in waiting list
- Displays in O3 heartbeat

### 4. **Better Error Handling** (lines 140-142)
- Added traceback for debugging

---

## How It Works Now:

### **Flow:**
```
Scanner adds 15 stocks:
├── Row 2-6: Empty status (Top 5 for immediate trading)
└── Row 7-16: "⏳ WAITING" status (Next 10 in queue)

Python Bot runs:
├── Trades Row 2-6 → Status: "TRADED (PAPER)"
├── Monitors active trades
├── Stock in Row 3 hits TARGET → Status: "EXITED (TARGET 🎯)"
└── Active count drops to 4/5

Next cycle:
├── Bot detects slot available (4/5)
├── Finds Row 7 with "⏳ WAITING"
├── Promotes Row 7 → Status: "TRADED (PAPER)"
├── Sends Telegram: "⬆️ PROMOTED & ENTERED: APLAPOLLO"
└── Active count back to 5/5
```

---

## Telegram Messages You'll See:

**When promoted:**
```
⬆️ PROMOTED & ENTERED: NSE:APLAPOLLO @ 1850.50
Target: 1962.53 (6%)
SL: 1822.74 (1.5%)
Slot: 5/5
```

**O3 Cell Display:**
```
Bot Live | Active: 5/5 | Waiting: 9 | 12:45:30
