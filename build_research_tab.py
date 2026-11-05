"""build_research_tab.py v1.0 (2026-11-02) — creates/refreshes the `Research` tab: three live FILTER lists (Intraday / Swing / Positional-bottom)
built ONLY from BottomScanner + Nifty200 columns that already exist. Formulas only: nothing is computed or written by Python except the layout,
nothing reads this tab (informational, same doctrine as BottomScanner). Re-running just rewrites the same layout. Usage: python build_research_tab.py"""
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BS = "BottomScanner!"
HEAD = ["Symbol", "Sector", "CMP", "%Chg", "RS", "Vol vs Avg %", "Master", "Stage", "Prev Day High", "Prev Day Low", "Support", "Resistance", "Retest", "F&O?", "Buildup", "Div Yield %"]
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
            'ARRAYFORMULA(IFERROR(VLOOKUP(CHOOSECOLS(n,1),Nifty200!$A$3:$AU$202,47,FALSE),"")),'
            'ARRAYFORMULA(IFERROR(VLOOKUP(CHOOSECOLS(n,1),Nifty200!$A$3:$AU$202,41,FALSE),"")))),"Abhi koi stock is filter mein nahi")')


def rgb(h):
    return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}


def colour(sh, ws, starts):
    """Section bands + conditional colours (green = good/strong, red = weak/avoid). Old rules are deleted first so a rebuild never stacks duplicates."""
    meta = [x for x in sh.fetch_sheet_metadata()["sheets"] if x["properties"]["sheetId"] == ws.id][0]
    reqs = [{"deleteConditionalFormatRule": {"sheetId": ws.id, "index": 0}} for _ in meta.get("conditionalFormats", [])]
    band = ["1F5FA8", "1E8449", "B9770E"]
    for (r0, _), b in zip(starts, band):
        reqs.append({"repeatCell": {"range": {"sheetId": ws.id, "startRowIndex": r0 - 1, "endRowIndex": r0, "startColumnIndex": 0, "endColumnIndex": 16},
                                    "cell": {"userEnteredFormat": {"backgroundColor": rgb(b), "textFormat": {"bold": True, "fontSize": 12, "foregroundColor": rgb("FFFFFF")}}},
                                    "fields": "userEnteredFormat(backgroundColor,textFormat)"}})
    def rule(c0, c1, kind, val, bg, fg="000000", rows=None):
        cond = {"type": kind}
        if val is not None:
            cond["values"] = [{"userEnteredValue": val}]
        for r0, r1 in rows or [(a + 3, a + 23) for a, _ in starts]:
            reqs.append({"addConditionalFormatRule": {"index": 0, "rule": {
                "ranges": [{"sheetId": ws.id, "startRowIndex": r0, "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1}],
                "booleanRule": {"condition": cond, "format": {"backgroundColor": rgb(bg), "textFormat": {"foregroundColor": rgb(fg), "bold": True}}}}}})
    rule(3, 4, "NUMBER_GREATER", "0", "C8F0D2", "0B6B2A")      # %Chg up
    rule(3, 4, "NUMBER_LESS", "0", "F8CDCD", "A32020")         # %Chg down
    rule(4, 5, "NUMBER_GREATER_THAN_EQ", "5", "C8F0D2", "0B6B2A")   # RS strong
    rule(4, 5, "NUMBER_LESS", "0", "F8CDCD", "A32020")         # RS weak
    rule(5, 6, "NUMBER_GREATER_THAN_EQ", "50", "C8F0D2", "0B6B2A")  # volume 1.5x+
    rule(5, 6, "NUMBER_LESS", "-30", "F8CDCD", "A32020")       # volume dry
    rule(7, 8, "TEXT_CONTAINS", "BREAKOUT CONFIRMED", "C8F0D2", "0B6B2A")
    rule(7, 8, "TEXT_CONTAINS", "BREAKOUT ALERT", "FFF1B8", "7A5A00")
    rule(7, 8, "TEXT_CONTAINS", "Near Breakout", "FFF1B8", "7A5A00")
    rule(12, 13, "TEXT_CONTAINS", "RETEST", "D6E6FA", "1F5FA8")
    rule(12, 13, "TEXT_CONTAINS", "extended", "FDE3C4", "9A5200")
    rule(13, 14, "TEXT_EQ", "YES", "EFEFEF", "333333")
    rule(13, 14, "TEXT_EQ", "N50", "EFEFEF", "333333")
    rule(14, 15, "TEXT_EQ", "Long Buildup", "A5E3B5", "0B6B2A")
    rule(14, 15, "TEXT_EQ", "Short Covering", "D6F2DD", "1E8449")
    rule(14, 15, "TEXT_EQ", "Short Buildup", "F5B7B1", "A32020")
    rule(14, 15, "TEXT_EQ", "Long Unwinding", "FDE3C4", "9A5200")
    rule(15, 16, "NUMBER_GREATER_THAN_EQ", "2.5", "C8F0D2", "0B6B2A")   # high trailing dividend yield (informational: SIP-zone stocks with >= 2.5% did better in the 5y test)
    sh.batch_update({"requests": reqs})


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
        ws.format(f"A{row + 2}:P{row + 2}", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.88, "green": 0.92, "blue": 0.98}})
        row += 26
    starts = [(4 + 26 * i, 0) for i in range(len(SECTIONS))]
    colour(sh, ws, starts)
    ws.format("A1", {"textFormat": {"bold": True, "fontSize": 13}})
    ws.freeze(rows=2)
    print("Research tab ready")


if __name__ == "__main__":
    main()
