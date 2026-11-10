"""
premarket_brief.py v0.1 (2026-11-10 SAMPLE) - the 'before the market opens' brief for the AI360Trading Facebook Page.
Owner 2026-11-10: intraday traders want TODAY's view before 09:15 (US close, crude, Asia, events), not a recap. Forward-looking, no prediction claims.
Free data only (Yahoo): Nasdaq/S&P/Dow, WTI + Brent, gold, USD/INR, US 10-year, India VIX, Nikkei, Hang Seng, Nifty last close. GIFT Nifty is NOT available from any free source we use - never claimed.
Results today: BotMemory EARNINGS_<SYM>_<date> rows (fetch_earnings.py). No free economic-calendar API, so no US-data events.
This file builds the DATA, the VERDICT, the NARRATION text and the PICTURES (thumbnail + 3 reel frames). Video assembly / upload are separate steps (not built yet).
USAGE: python premarket_brief.py --sample [YYYY-MM-DD]     (writes to _drafts_local/premarket/)
"""
import os
import sys
from datetime import date, datetime, timedelta

from PIL import Image, ImageDraw

SYMS = [("NASDAQ", "^IXIC", "us"), ("S&P 500", "^GSPC", "us"), ("DOW", "^DJI", "us"), ("CRUDE WTI", "CL=F", "cm"), ("BRENT", "BZ=F", "cm"), ("GOLD", "GC=F", "cm"),
        ("USD/INR", "INR=X", "fx"), ("US 10Y", "^TNX", "fx"), ("NIKKEI", "^N225", "as"), ("HANG SENG", "^HSI", "as"), ("INDIA VIX", "^INDIAVIX", "in"), ("NIFTY", "^NSEI", "in")]
GREEN, RED, GOLD, WHITE, MUTED = (40, 210, 120), (255, 80, 70), (255, 200, 50), (255, 255, 255), (170, 180, 205)


def pct_change(closes):
    """(last, prev, pct) from a list of closes (oldest first), or None. Pure."""
    c = [float(x) for x in closes if x == x]
    if len(c) < 2 or c[-2] <= 0:
        return None
    return c[-1], c[-2], (c[-1] / c[-2] - 1) * 100


def verdict(rows):
    """'POSITIVE' / 'NEGATIVE' / 'MIXED' from the five equity indices (US 3 + Asia 2). Pure.
    POSITIVE = at least 4 of 5 up and the average >= +0.3%; NEGATIVE = at least 4 of 5 down and the average <= -0.3%; else MIXED. Missing data -> MIXED (never a strong claim)."""
    eq = [rows[k]["pct"] for k in ("NASDAQ", "S&P 500", "DOW", "NIKKEI", "HANG SENG") if k in rows]
    if len(eq) < 4:
        return "MIXED"
    avg = sum(eq) / len(eq)
    up, dn = sum(1 for x in eq if x > 0), sum(1 for x in eq if x < 0)
    if up >= 4 and avg >= 0.3:
        return "POSITIVE"
    if dn >= 4 and avg <= -0.3:
        return "NEGATIVE"
    return "MIXED"


def fetch_rows():
    import yfinance as yf
    rows = {}
    for name, sym, grp in SYMS:
        try:
            h = yf.Ticker(sym).history(period="7d")["Close"].dropna().tolist()
            r = pct_change(h)
            if r:
                rows[name] = {"last": r[0], "prev": r[1], "pct": r[2], "grp": grp}
        except Exception:
            pass
    return rows


def results_for(day):
    """Symbols with a result on `day` (date) from BotMemory EARNINGS_<SYM>_<date>. Fail-open -> []. """
    try:
        import json
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        sc = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON", "").strip()
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(raw), sc) if raw else ServiceAccountCredentials.from_json_keyfile_name("service_account.json", sc)
        sh = gspread.authorize(creds).open("Ai360tradingAlgo")
        v = sh.worksheet("BotMemory").get_all_values()
        known = set()
        for tab in ("Nifty200", "CashWatchlist"):                      # only stocks our members can actually trade (the earnings cache holds ~1,400 symbols)
            try:
                known |= {str(r[0]).replace("NSE:", "").strip() for r in sh.worksheet(tab).get_all_values()[1:] if r and r[0]}
            except Exception:
                pass
        suffix = "_" + day.isoformat()
        out = sorted(r[0][len("EARNINGS_"):-len(suffix)] for r in v if r and r[0].startswith("EARNINGS_") and r[0].endswith(suffix))
        return [x for x in out if x in known] if known else out
    except Exception:
        return []


def next_trading_day(d):
    d = d + timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def narration_parts(rows, v, results, day):
    """Three easy-Hinglish segments (Latin script; the TTS step converts through human_touch), one per picture: hook / numbers / today. No advice, no prediction. Pure."""
    def mv(k):
        r = rows.get(k)
        return None if not r else f"{k} {abs(r['pct']):.1f} percent {'upar' if r['pct'] >= 0 else 'neeche'}"
    verdict_txt = {"POSITIVE": "Global cues positive hain.", "NEGATIVE": "Global cues kamzor hain.", "MIXED": "Global cues mile-jule hain."}[v]
    a = "Market khulne se pehle ek minute. " + verdict_txt
    n = rows.get("NIFTY")
    if n:
        a += f" Nifty {n['last']:,.0f} par band hua tha."
    b = []
    us = [mv(k) for k in ("NASDAQ", "S&P 500", "DOW") if mv(k)]
    if us:
        b.append("Amrika mein " + ", ".join(us) + ".")
    for k, label in (("CRUDE WTI", "Crude"), ("GOLD", "Sona")):
        r = rows.get(k)
        if r:
            b.append(f"{label} {abs(r['pct']):.1f} percent {'upar' if r['pct'] >= 0 else 'neeche'}.")
    asia = [mv(k) for k in ("NIKKEI", "HANG SENG") if mv(k)]
    if asia:
        b.append("Asia mein " + " aur ".join(asia) + ".")
    c = []
    if "INDIA VIX" in rows:
        c.append(f"India VIX {rows['INDIA VIX']['last']:.1f}.")
    if results:
        c.append("Aaj results: " + ", ".join(results[:3]) + ".")
    c.append("GIFT Nifty apne chart par dekh lena.")
    c.append("Sirf jaankari hai, salah nahi.")
    return [a, " ".join(b), " ".join(c)]


def narration(rows, v, results, day):
    return " ".join(x for x in narration_parts(rows, v, results, day) if x)


# ------------------------------------------------------------------ pictures
def _font(sz):
    import tech_short as T
    return T.font(sz)


def _tc(d, xy, s, f, fill=WHITE, ow=4):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            d.text((x + dx, y + dy), s, font=f, fill=(0, 0, 0, 255), anchor="mm")
    d.text((x, y), s, font=f, fill=fill + (255,), anchor="mm")


def _bg(w, h):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=(int(8 + 14 * k), int(12 + 10 * k), int(32 + 26 * k)))
    d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, w, 90):
        d.line([(x, 0), (x, h)], fill=(255, 255, 255, 10))
    for y in range(0, h, 90):
        d.line([(0, y), (w, y)], fill=(255, 255, 255, 10))
    return im


def _tri(d, cx, cy, s, up, col):
    pts = [(cx, cy - s), (cx + s, cy + s * 0.8), (cx - s, cy + s * 0.8)] if up else [(cx, cy + s), (cx + s, cy - s * 0.8), (cx - s, cy - s * 0.8)]
    d.polygon(pts, fill=col + (255,), outline=(0, 0, 0, 255))


VCOL = {"POSITIVE": GREEN, "NEGATIVE": RED, "MIXED": GOLD}


def frame_hook(rows, v, day, path):
    im = _bg(1080, 1920)
    d = ImageDraw.Draw(im, "RGBA")
    _tc(d, (540, 150), f"PRE-MARKET BRIEF | {day.strftime('%d %b').upper()}", _font(46), MUTED, 3)
    _tc(d, (540, 520), "GLOBAL CUES", _font(122), WHITE, 6)
    col = VCOL[v]
    w = d.textlength(v, font=_font(190)) + 100
    d.rounded_rectangle((540 - w / 2, 650, 540 + w / 2, 880), radius=40, fill=col + (255,), outline=WHITE + (255,), width=8)
    _tc(d, (540, 770), v, _font(190), (10, 14, 28), 0)
    n = rows.get("NIFTY")
    if n:
        _tc(d, (540, 1120), f"NIFTY  {n['last']:,.0f}", _font(110), WHITE, 6)
        _tri(d, 215, 1250, 34, n["pct"] >= 0, GREEN if n["pct"] >= 0 else RED)
        _tc(d, (580, 1250), f"{n['pct']:+.2f}%  (last close)", _font(58), MUTED, 3)
    _tc(d, (540, 1520), "AAJ NIFTY KYA?", _font(120), GOLD, 7)
    _tc(d, (540, 1790), "Info only, not advice | AI voice", _font(34), MUTED, 2)
    im.save(path, quality=92)


def frame_table(rows, v, day, path):
    im = _bg(1080, 1920)
    d = ImageDraw.Draw(im, "RGBA")
    _tc(d, (540, 130), "KHULNE SE PEHLE", _font(78), GOLD, 5)
    y = 260
    groups = [("US CLOSE", ["NASDAQ", "S&P 500", "DOW"]), ("COMMODITY / FX", ["CRUDE WTI", "BRENT", "GOLD", "USD/INR"]), ("ASIA (LIVE)", ["NIKKEI", "HANG SENG"]), ("INDIA", ["INDIA VIX"])]
    for gname, names in groups:
        d.text((70, y), gname, font=_font(36), fill=MUTED + (255,), anchor="lm")
        y += 56
        for nme in names:
            r = rows.get(nme)
            d.rounded_rectangle((50, y - 38, 1030, y + 38), radius=22, fill=(255, 255, 255, 22))
            d.text((90, y), nme, font=_font(44), fill=WHITE + (255,), anchor="lm")
            if r:
                last = f"{r['last']:,.0f}" if r["last"] >= 1000 else f"{r['last']:,.2f}"
                d.text((650, y), last, font=_font(42), fill=WHITE + (255,), anchor="rm")
                up = r["pct"] >= 0
                c = (GREEN if up else RED) if nme != "INDIA VIX" else (RED if up else GREEN)
                _tri(d, 740, y, 18, up, c)
                d.text((960, y), f"{r['pct']:+.2f}%", font=_font(46), fill=c + (255,), anchor="rm")
            else:
                d.text((960, y), "-", font=_font(46), fill=MUTED + (255,), anchor="rm")
            y += 88
        y += 30
    d.text((540, 1850), "Source: public market data. Info only, not advice.", font=_font(30), fill=MUTED + (255,), anchor="mm")
    im.save(path, quality=92)


def frame_today(rows, v, results, day, path):
    im = _bg(1080, 1920)
    d = ImageDraw.Draw(im, "RGBA")
    _tc(d, (540, 150), "AAJ DHYAN RAKHO", _font(100), GOLD, 6)
    y = 330
    d.text((70, y), "RESULTS AAJ", font=_font(40), fill=MUTED + (255,), anchor="lm")
    y += 80
    if results:
        x = 70
        for sym in results[:8]:
            w = d.textlength(sym, font=_font(46)) + 50
            if x + w > 1010:
                x, y = 70, y + 100
            d.rounded_rectangle((x, y - 36, x + w, y + 36), radius=26, fill=(255, 200, 50, 235))
            d.text((x + w / 2, y), sym, font=_font(46), fill=(10, 14, 28, 255), anchor="mm")
            x += w + 18
        y += 130
    else:
        d.text((70, y), "Koi bada result nahi (hamare data me)", font=_font(42), fill=WHITE + (255,), anchor="lm")
        y += 130
    notes = []
    if "CRUDE WTI" in rows and abs(rows["CRUDE WTI"]["pct"]) >= 2:
        notes.append(("CRUDE " + ("UPAR" if rows["CRUDE WTI"]["pct"] > 0 else "NEECHE") + f" {abs(rows['CRUDE WTI']['pct']):.1f}%", "Oil / airline / paint par nazar"))
    if "INDIA VIX" in rows:
        notes.append((f"INDIA VIX {rows['INDIA VIX']['last']:.1f}", "Option premium ki keemat ka andaza"))
    notes.append(("GIFT NIFTY", "Hamare free data me nahi, apne broker/chart par dekho"))
    for t1, t2 in notes:
        d.rounded_rectangle((50, y - 60, 1030, y + 70), radius=26, fill=(255, 255, 255, 24))
        d.text((90, y - 18), t1, font=_font(52), fill=WHITE + (255,), anchor="lm")
        d.text((90, y + 36), t2, font=_font(36), fill=MUTED + (255,), anchor="lm")
        y += 170
    col = VCOL[v]
    d.rounded_rectangle((90, 1500, 990, 1680), radius=40, fill=col + (255,), outline=WHITE + (255,), width=6)
    _tc(d, (540, 1590), "GLOBAL CUES: " + v, _font(70), (10, 14, 28), 0)
    d.text((540, 1790), "Roz ek brief: t.me/ai360trading | Info only, not advice", font=_font(34), fill=MUTED + (255,), anchor="mm")
    im.save(path, quality=92)


def thumbnail(rows, v, day, path):
    im = _bg(1280, 720)
    d = ImageDraw.Draw(im, "RGBA")
    _tc(d, (640, 120), f"MARKET KHULNE SE PEHLE | {day.strftime('%d %b').upper()}", _font(46), MUTED, 3)
    _tc(d, (640, 290), "GLOBAL CUES", _font(150), WHITE, 7)
    col = VCOL[v]
    w = d.textlength(v, font=_font(150)) + 90
    d.rounded_rectangle((640 - w / 2, 400, 640 + w / 2, 590), radius=34, fill=col + (255,), outline=WHITE + (255,), width=7)
    _tc(d, (640, 495), v, _font(150), (10, 14, 28), 0)
    n = rows.get("NIFTY")
    if n:
        _tc(d, (640, 660), f"NIFTY {n['last']:,.0f}: AAJ KYA?", _font(60), GOLD, 4)
    im.save(path, quality=92)


def build_sample(day_arg=None):
    today = date.fromisoformat(day_arg) if day_arg else date.today()
    day = next_trading_day(today) if today.weekday() >= 5 else today
    rows = fetch_rows()
    v = verdict(rows)
    res = results_for(day)
    out = os.path.join("_drafts_local", "premarket")
    os.makedirs(out, exist_ok=True)
    frame_hook(rows, v, day, os.path.join(out, "frame1_hook.jpg"))
    frame_table(rows, v, day, os.path.join(out, "frame2_table.jpg"))
    frame_today(rows, v, res, day, os.path.join(out, "frame3_today.jpg"))
    thumbnail(rows, v, day, os.path.join(out, "thumbnail.jpg"))
    text = narration(rows, v, res, day)
    with open(os.path.join(out, "narration.txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"verdict={v} rows={len(rows)} results={res}\n{text}")
    return rows, v, res, text


if __name__ == "__main__":
    if "--sample" in sys.argv:
        i = sys.argv.index("--sample")
        build_sample(sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("-") else None)
    else:
        print(__doc__)
