def run_trading_cycle():
    records = sheet.get_all_records()
    new_trades_count = 0
    
    print(f"🤖 Bot Started: {datetime.now().strftime('%H:%M')}")
    print(f"📊 Total Records Found: {len(records)}")
    
    for i, row in enumerate(records):
        row_num = i + 2
        
        symbol = row.get('Symbol')
        live_price = row.get('Price')
        status = str(row.get('Status', '')).strip()
        
        print(f"Row {row_num}: Symbol={symbol}, Price={live_price}, Status='{status}'")
        
        if status == "" and symbol != "":
            if new_trades_count < MAX_NEW_TRADES:
                print(f"✅ Executing Trade: {symbol} at {live_price}")
                
                sheet.update_cell(row_num, 11, "TRADED (PAPER)")
                sheet.update_cell(row_num, 12, live_price)
                sheet.update_cell(row_num, 13, datetime.now().strftime("%H:%M"))
                
                new_trades_count += 1
                print(f"✅ Trade #{new_trades_count} logged successfully")
            else:
                print(f"⏭️ Limit Reached: Skipping {symbol}")
        else:
            print(f"⏭️ Skipping: Status='{status}' or Symbol empty")
    
    print(f"🏁 Bot Finished: {new_trades_count} new trades executed")
