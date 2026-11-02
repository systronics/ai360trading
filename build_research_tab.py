"""build_research_tab.py v1.0 (2026-11-02) — creates/refreshes the `Research` tab: three live FILTER lists (Intraday / Swing / Positional-bottom)
built ONLY from BottomScanner + Nifty200 columns that already exist. Formulas only: nothing is computed or written by Python except the layout,
nothing reads this tab (informational, same doctrine as BottomScanner). Re-running just rewrites the same layout. Usage: python build_research_tab.py"""
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BS = "BottomScanner!"
HEAD = ["Symbol", "Sector", "CMP", "%Chg", "RS", "Vol vs Avg %", "Master", "Stage", "Prev Day High", "Prev Day Low", "Support", "Resistance", "Retest", "F&O?", "Buildup"]
SECTIONS = [
    ("1) INTRADAY / kal subah 15-min chart par dekho",
     "Retest buy zone ya support par (RS>=5). Dekho: prev-day high ke upar 15m close + volume; Support toote to chhodo.",
     f'(({BS}$AK$3:$AK$202="RETEST BUY ZONE")+(({BS}$AK$3:$AK$202="AT SUPPORT")*({BS}$I$3:$I$202>=5))>0)'),
    ("2) SWING / daily chart par dekho",
     "RS>=5 aur breakout signal ya retest zone. Dekho: daily close resistance ke upar, volume badha hua, SL support ke neeche.",
     f'({BS}$I$3:$I$202>=5)*((({BS}$AJ$3:$AJ$202<>"-")+({BS}$V$3:$V$202="RETEST ZONE")+({BS}$V$3:$V$202="NEAR BREAKOUT"))>0)'),
    ("3) POSITIONAL / BOTTOM weekly chart par dekho",
     "Accumulation zone ya base ban raha hai. Dekho: weekly chart par base, 10-week EMA ke upar close. Jaldi nahi, SIP jaisa dheere lena.",
     f'((({BS}$AI$3:$AI$202="ACCUMULATION ZONE")+({BS}$AG$3:$AG$202="BASING")+({BS}$AG$3:$AG$202="BASE + WEEK-HIGH CROSS"))>0)', 9),
]


def formula(cond, sort_col=11):
    return ('=IFERROR(LET(d,SORT(FILTER(BottomScanner!$A$3:$AL$202,' + cond + '),' + str(sort_col) + ',FALSE),n,ARRAY_CONSTRAIN(d,20,38),'
            'HSTACK(CHOOSECOLS(n,1,2,3,4,9,10,11,12,13,14,17,19,22),'
            'ARRAYFORMULA(IFERROR(VLOOKUP(CHOOSECOLS(n,1),Nifty200!$A$3:$AU$202,36,FALSE),"")),'
            'ARRAYFORMULA(IFERROR(VLOOKUP(CHOOSECOLS(n,1),Nifty200!$A$3:$AU$202,47,FALSE),"")))),"Abhi koi stock is filter mein nahi")')


def main():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip() or open("service_account.json").read()
    sh = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), scope)).open("Ai360tradingAlgo")
    try:
        ws = sh.worksheet("Research")
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet("Research", rows=100, cols=16)
    vals = [["RESEARCH LISTS (sirf chart padhne ke liye, entry signal NAHI. Asli entry alert Telegram se aata hai.)"],
            ["Ye list live hai: BottomScanner + Nifty200 se apne aap banti hai, har list max 20 stock, Master score (positional mein RS) ke hisaab se upar se neeche. Raat ko ya subah dekho."]]
    ws.update(range_name="A1", values=vals)
    row = 4
    for title, note, cond, *sc in SECTIONS:
        ws.update(range_name=f"A{row}", values=[[title], [note], HEAD])
        ws.update(range_name=f"A{row + 3}", values=[[formula(cond, *sc)]], value_input_option="USER_ENTERED")
        ws.format(f"A{row}", {"textFormat": {"bold": True, "fontSize": 12}})
        ws.format(f"A{row + 2}:O{row + 2}", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.88, "green": 0.92, "blue": 0.98}})
        row += 26
    ws.format("A1", {"textFormat": {"bold": True, "fontSize": 13}})
    ws.freeze(rows=2)
    print("Research tab ready")


if __name__ == "__main__":
    main()
