"""
premarket_brief.py v1.1 (2026-11-10) - the 'before the market opens' brief for the AI360Trading Facebook Page.
Owner 2026-11-10: intraday traders want TODAY's view before 09:15 (US close, crude, Asia, events), not a recap, and a TREND SIGNAL instead of a list of numbers (the numbers are already on screen).
Free data only (Yahoo): Nasdaq/S&P/Dow, WTI + Brent, gold, USD/INR, US 10-year, India VIX, Nikkei, Hang Seng, Nifty last close.
GIFT Nifty: NO free, reliable source exists (checked 2026-11-10: Yahoo has no symbol, Upstox publishes no NSE IX instruments (403), third-party pages are undocumented/unlicensed scraping). So the reel shows an
'opening indication' derived from the global cues (US + Asia + crude), clearly labelled as such, and tells viewers to look at GIFT Nifty on their own chart. Never claims a GIFT Nifty number.
Results today: BotMemory EARNINGS_<SYM>_<date> rows (fetch_earnings.py), only Nifty200/CashWatchlist symbols. No free economic-calendar API, so no US-data events.
Narration is DEVANAGARI Hindi with the usual English market words written in Devanagari (so the hi-IN voice pronounces everything correctly); on-screen text is Roman. Numbers are NOT read aloud.
USAGE: python premarket_brief.py --sample [YYYY-MM-DD]     (writes to _drafts_local/premarket/)
"""
import os
import sys
from datetime import date, timedelta

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


OPENING = {"POSITIVE": "UPAR KA SANKET", "NEGATIVE": "NEECHE KA SANKET", "MIXED": "FLAT / MILA-JULA"}


def opening_label(v):
    """On-screen text for the Nifty opening indication (derived from global cues, NOT GIFT Nifty). Pure."""
    return OPENING.get(v, OPENING["MIXED"])


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


# ------------------------------------------------------------------ narration (Devanagari Hindi, no numbers)
def _strength(p):
    a = abs(p)
    return "हल्की" if a < 0.5 else ("तेज़" if a >= 1.5 else "")


def narration_parts(rows, v, results, day):
    """Three Devanagari Hindi segments, one per picture: hook (the signal) / what drives it / today's watch-points. English market words are written in Devanagari so the voice pronounces them
    correctly; NO numbers are spoken (they are on screen); no advice, no guarantee. Pure."""
    cues = {"POSITIVE": "पॉज़िटिव", "NEGATIVE": "कमज़ोर", "MIXED": "मिले-जुले"}[v]
    open_txt = {"POSITIVE": "निफ्टी की ओपनिंग ऊपर रहने का इशारा है।", "NEGATIVE": "निफ्टी की ओपनिंग नीचे रहने का इशारा है।",
                "MIXED": "निफ्टी की ओपनिंग फ्लैट या मिली-जुली रह सकती है।"}[v]
    a = f"मार्केट खुलने से पहले एक मिनट। ग्लोबल क्यूज़ {cues} हैं, और {open_txt}"
    b = []
    us = [rows[k]["pct"] for k in ("NASDAQ", "S&P 500", "DOW") if k in rows]
    if us:
        avg = sum(us) / len(us)
        if all(x > 0 for x in us):
            b.append("अमेरिकी बाज़ार " + ("तेज़ी से " if avg >= 1.5 else ("हल्के " if avg < 0.5 else "")) + "ऊपर बंद हुए।")
        elif all(x < 0 for x in us):
            b.append("अमेरिकी बाज़ार " + ("तेज़ी से " if avg <= -1.5 else ("हल्के " if avg > -0.5 else "")) + "नीचे बंद हुए।")
        else:
            b.append("अमेरिकी बाज़ार मिले-जुले बंद हुए।")
    cr = rows.get("CRUDE WTI")
    if cr and abs(cr["pct"]) >= 0.5:
        if cr["pct"] < 0:
            b.append(f"क्रूड ऑयल में {_strength(cr['pct'])} गिरावट आई है, जो भारतीय बाज़ार के लिए आम तौर पर राहत की बात है।".replace("  ", " "))
        else:
            b.append(f"क्रूड ऑयल में {_strength(cr['pct'])} तेज़ी आई है, जो भारतीय बाज़ार पर दबाव बना सकती है।".replace("  ", " "))
    asia = [rows[k]["pct"] for k in ("NIKKEI", "HANG SENG") if k in rows]
    if asia:
        m = sum(asia) / len(asia)
        b.append("एशियाई बाज़ार " + ("मज़बूत हैं।" if m >= 0.3 else ("कमज़ोर हैं।" if m <= -0.3 else "मिले-जुले हैं।")))
    c = []
    vx = rows.get("INDIA VIX")
    if vx:
        lvl = vx["last"]
        c.append("इंडिया विक्स का स्तर " + ("कम है, यानी बाज़ार में ज़्यादा डर नहीं है।" if lvl < 15 else ("सामान्य है।" if lvl < 20 else "ऊँचा है, यानी उतार-चढ़ाव ज़्यादा रह सकता है।")))
    if results:
        c.append("आज कुछ कंपनियों के नतीजे हैं, लिस्ट स्क्रीन पर देखिए।")
    c.append("यह सिर्फ़ जानकारी है, सलाह नहीं। गिफ्ट निफ्टी अपने चार्ट पर देख लीजिए, और अपना स्टॉप लॉस ज़रूर रखिए।")
    return [a, " ".join(b), " ".join(c)]


def narration(rows, v, results, day):
    return " ".join(x for x in narration_parts(rows, v, results, day) if x)


# ------------------------------------------------------------------ pictures
def _font(sz):
    import tech_short as T
    return T.font(sz)


def fit_font(d, text, maxw, start, minsize=34):
    """Largest font (<= start) whose rendering of `text` is at most `maxw` wide. The CI font (DejaVu) is wider than the Windows one, so nothing may be sized by eye. Pure on the draw object."""
    size = start
    while size > minsize and d.textlength(text, font=_font(size)) > maxw:
        size -= 4
    return _font(size)


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
SAFE_W = 940          # text must stay inside 70..1010 on the 1080 wide reel (platform buttons/edges crop the rest)


def frame_hook(rows, v, day, path):
    im = _bg(1080, 1920)
    d = ImageDraw.Draw(im, "RGBA")
    t = f"PRE-MARKET BRIEF | {day.strftime('%d %b').upper()}"
    _tc(d, (540, 150), t, fit_font(d, t, SAFE_W, 46), MUTED, 3)
    _tc(d, (540, 430), "GLOBAL CUES", fit_font(d, "GLOBAL CUES", SAFE_W, 130), WHITE, 6)
    col = VCOL[v]
    fv = fit_font(d, v, 800, 170)
    w = d.textlength(v, font=fv) + 100
    d.rounded_rectangle((540 - w / 2, 540, 540 + w / 2, 760), radius=40, fill=col + (255,), outline=WHITE + (255,), width=8)
    _tc(d, (540, 650), v, fv, (10, 14, 28), 0)
    _tc(d, (540, 880), "NIFTY OPENING", fit_font(d, "NIFTY OPENING", SAFE_W, 80), MUTED, 4)
    ol = opening_label(v)
    _tc(d, (540, 1000), ol, fit_font(d, ol, SAFE_W, 100), col, 6)
    n = rows.get("NIFTY")
    if n:
        s1 = f"NIFTY  {n['last']:,.0f}"
        _tc(d, (540, 1200), s1, fit_font(d, s1, SAFE_W, 100), WHITE, 6)
        s2 = f"{n['pct']:+.2f}%  (last close)"
        f2 = fit_font(d, s2, 700, 56)
        wid = d.textlength(s2, font=f2)
        _tri(d, 540 - wid / 2 - 60, 1305, 30, n["pct"] >= 0, GREEN if n["pct"] >= 0 else RED)
        _tc(d, (540 + 20, 1305), s2, f2, MUTED, 3)
    q = "AAJ NIFTY KYA?"
    _tc(d, (540, 1560), q, fit_font(d, q, SAFE_W, 120), GOLD, 7)
    f = "Info only, not advice | AI voice"
    _tc(d, (540, 1800), f, fit_font(d, f, SAFE_W, 34), MUTED, 2)
    im.save(path, quality=92)


def frame_table(rows, v, day, path):
    im = _bg(1080, 1920)
    d = ImageDraw.Draw(im, "RGBA")
    _tc(d, (540, 130), "KHULNE SE PEHLE", fit_font(d, "KHULNE SE PEHLE", SAFE_W, 78), GOLD, 5)
    y = 260
    groups = [("US CLOSE", ["NASDAQ", "S&P 500", "DOW"]), ("COMMODITY / FX", ["CRUDE WTI", "BRENT", "GOLD", "USD/INR"]), ("ASIA (LIVE)", ["NIKKEI", "HANG SENG"]), ("INDIA", ["INDIA VIX"])]
    for gname, names in groups:
        d.text((70, y), gname, font=_font(36), fill=MUTED + (255,), anchor="lm")
        y += 56
        for nme in names:
            r = rows.get(nme)
            d.rounded_rectangle((50, y - 38, 1030, y + 38), radius=22, fill=(255, 255, 255, 22))
            d.text((90, y), nme, font=fit_font(d, nme, 330, 44, 30), fill=WHITE + (255,), anchor="lm")
            if r:
                last = f"{r['last']:,.0f}" if r["last"] >= 1000 else f"{r['last']:,.2f}"
                d.text((680, y), last, font=fit_font(d, last, 230, 42, 30), fill=WHITE + (255,), anchor="rm")
                up = r["pct"] >= 0
                c = (GREEN if up else RED) if nme != "INDIA VIX" else (RED if up else GREEN)
                _tri(d, 740, y, 18, up, c)
                d.text((985, y), f"{r['pct']:+.2f}%", font=_font(42), fill=c + (255,), anchor="rm")
            else:
                d.text((985, y), "-", font=_font(46), fill=MUTED + (255,), anchor="rm")
            y += 88
        y += 30
    s = "Source: public market data. Info only, not advice."
    d.text((540, 1850), s, font=fit_font(d, s, SAFE_W, 30, 22), fill=MUTED + (255,), anchor="mm")
    im.save(path, quality=92)


def frame_today(rows, v, results, day, path):
    im = _bg(1080, 1920)
    d = ImageDraw.Draw(im, "RGBA")
    _tc(d, (540, 150), "AAJ DHYAN RAKHO", fit_font(d, "AAJ DHYAN RAKHO", SAFE_W, 100), GOLD, 6)
    y = 330
    d.text((70, y), "RESULTS AAJ", font=_font(40), fill=MUTED + (255,), anchor="lm")
    y += 80
    if results:
        x = 70
        for sym in results[:8]:
            f = fit_font(d, sym, 700, 46, 30)
            w = d.textlength(sym, font=f) + 50
            if x + w > 1010:
                x, y = 70, y + 100
            d.rounded_rectangle((x, y - 36, x + w, y + 36), radius=26, fill=(255, 200, 50, 235))
            d.text((x + w / 2, y), sym, font=f, fill=(10, 14, 28, 255), anchor="mm")
            x += w + 18
        y += 130
    else:
        t = "Koi bada result nahi (hamare data me)"
        d.text((70, y), t, font=fit_font(d, t, 940, 42, 28), fill=WHITE + (255,), anchor="lm")
        y += 130
    notes = []
    if "CRUDE WTI" in rows and abs(rows["CRUDE WTI"]["pct"]) >= 2:
        notes.append(("CRUDE " + ("UPAR" if rows["CRUDE WTI"]["pct"] > 0 else "NEECHE") + f" {abs(rows['CRUDE WTI']['pct']):.1f}%", "Oil / airline / paint par nazar"))
    if "INDIA VIX" in rows:
        notes.append((f"INDIA VIX {rows['INDIA VIX']['last']:.1f}", "Option premium ki keemat ka andaza"))
    notes.append(("GIFT NIFTY", "Free data nahi: apne chart par dekho"))
    for t1, t2 in notes:
        d.rounded_rectangle((50, y - 60, 1030, y + 70), radius=26, fill=(255, 255, 255, 24))
        d.text((90, y - 18), t1, font=fit_font(d, t1, 880, 52, 30), fill=WHITE + (255,), anchor="lm")
        d.text((90, y + 36), t2, font=fit_font(d, t2, 880, 36, 24), fill=MUTED + (255,), anchor="lm")
        y += 170
    col = VCOL[v]
    t = "NIFTY OPENING: " + opening_label(v)
    f = fit_font(d, t, 800, 64)
    d.rounded_rectangle((60, 1470, 1020, 1690), radius=40, fill=col + (255,), outline=WHITE + (255,), width=6)
    d.text((540, 1580), t, font=f, fill=(10, 14, 28, 255), anchor="mm")
    t2 = "(global cues se sanket, GIFT Nifty nahi)"
    d.text((540, 1660), t2, font=fit_font(d, t2, 880, 30, 22), fill=(10, 14, 28, 255), anchor="mm")
    s = "Roz ek brief: t.me/ai360trading | Info only, not advice"
    d.text((540, 1790), s, font=fit_font(d, s, SAFE_W, 34, 22), fill=MUTED + (255,), anchor="mm")
    im.save(path, quality=92)


def thumbnail(rows, v, day, path):
    im = _bg(1280, 720)
    d = ImageDraw.Draw(im, "RGBA")
    t = f"MARKET KHULNE SE PEHLE | {day.strftime('%d %b').upper()}"
    _tc(d, (640, 110), t, fit_font(d, t, 1100, 46), MUTED, 3)
    _tc(d, (640, 270), "GLOBAL CUES", fit_font(d, "GLOBAL CUES", 1100, 150), WHITE, 7)
    col = VCOL[v]
    fv = fit_font(d, v, 900, 150)
    w = d.textlength(v, font=fv) + 90
    d.rounded_rectangle((640 - w / 2, 390, 640 + w / 2, 580), radius=34, fill=col + (255,), outline=WHITE + (255,), width=7)
    _tc(d, (640, 485), v, fv, (10, 14, 28), 0)
    n = rows.get("NIFTY")
    s = f"NIFTY OPENING: {opening_label(v)}"
    _tc(d, (640, 650), s, fit_font(d, s, 1100, 56), GOLD, 4)
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
