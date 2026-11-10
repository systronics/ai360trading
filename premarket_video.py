"""
premarket_video.py v1.0 (2026-11-10) - assembles the daily 'before the market opens' reel (1080x1920, under 59 s) from premarket_brief.py: 3 pictures + Hinglish voice (Edge hi-IN-MadhurNeural, same voice as the
morning reel), no music, no sound effects (owner 2026-11-10: sfx between sentences sounded like a breath). Writes <out>/<date>_premarket.mp4 + <date>_premarket_meta.json (caption for Facebook/Instagram).
Forward-looking only; every number is real public data; GIFT Nifty is never claimed. Info only, AI voice disclosed.
USAGE: python premarket_video.py --out output/premarket [--day YYYY-MM-DD]
Fail-open: on ANY error nothing is written and the exit code stays 0 (the workflow then simply posts nothing that day).
"""
import asyncio
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

VOICE = "hi-IN-MadhurNeural"
RATE = "+12%"
PITCH = "+10Hz"
MAX_SECONDS = 58.0


def tts(text, path):
    import edge_tts
    from human_touch import safe_tts_par
    t = safe_tts_par(text)

    async def go():
        await edge_tts.Communicate(t, VOICE, rate=RATE, pitch=PITCH).save(str(path))
    asyncio.run(go())
    return path


def push_in(path, dur, zoom=0.04):
    """get_frame(t) for a slow 4% push-in on a 1080x1920 picture. Done with numpy + PIL because moviepy 1.0.3's resize() calls Image.ANTIALIAS, which Pillow 10+ removed."""
    import numpy as np
    from PIL import Image
    arr = np.asarray(Image.open(path).convert("RGB"))
    h, w = arr.shape[:2]

    def get(t):
        z = 1.0 + zoom * min(max(t / max(dur, 0.1), 0.0), 1.0)
        cw, ch = int(w / z), int(h / z)
        x0, y0 = (w - cw) // 2, (h - ch) // 2
        return np.asarray(Image.fromarray(arr[y0:y0 + ch, x0:x0 + cw]).resize((w, h), Image.BILINEAR))
    return get


def caption(rows, v, results, day):
    tg = "t.me/ai360trading"
    try:
        import money_funnel as _mf
        tg = _mf.tg_link("facebook").replace("https://", "")
    except Exception:
        pass
    n = rows.get("NIFTY")
    head = f"Market khulne se pehle: global cues {v}" + (f" | Nifty {n['last']:,.0f}" if n else "")
    lines = [head, ""]
    for k in ("NASDAQ", "S&P 500", "CRUDE WTI", "GOLD", "NIKKEI", "INDIA VIX"):
        r = rows.get(k)
        if r:
            lines.append(f"{k}: {r['last']:,.2f} ({r['pct']:+.2f}%)")
    if results:
        lines += ["", "Aaj results: " + ", ".join(results[:6])]
    try:
        from human_touch import ai_disclosure
        disc = ai_disclosure("hi")
    except Exception:
        disc = "AI voice."
    lines += ["", f"Roz subah ka brief: {tg}", "Sirf jaankari, salah nahi. SEBI registered nahi.", disc, "", "#Nifty #PreMarket #StockMarketIndia"]
    return "\n".join(lines)


def build(out_dir, day_arg=None):
    from moviepy.editor import AudioFileClip, VideoClip, concatenate_videoclips
    import premarket_brief as PB
    today = date.fromisoformat(day_arg) if day_arg else date.today()
    day = PB.next_trading_day(today) if today.weekday() >= 5 else today
    rows = PB.fetch_rows()
    need = [k for k in ("NASDAQ", "S&P 500", "DOW", "NIKKEI", "HANG SENG", "NIFTY") if k in rows]
    if len(need) < 4:
        print(f"[PREMARKET] only {len(need)} of 6 key rows available - not building (a half-empty brief is worse than none)")
        return None
    v = PB.verdict(rows)
    results = PB.results_for(day)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_tmp"
    tmp.mkdir(exist_ok=True)
    PB.frame_hook(rows, v, day, tmp / "f1.jpg")
    PB.frame_table(rows, v, day, tmp / "f2.jpg")
    PB.frame_today(rows, v, results, day, tmp / "f3.jpg")
    PB.thumbnail(rows, v, day, out / f"{day.isoformat()}_premarket_thumb.jpg")
    parts = [p for p in PB.narration_parts(rows, v, results, day) if p.strip()]
    clips, total = [], 0.0
    for i, text in enumerate(parts):
        mp3 = tts(text, tmp / f"v{i}.mp3")
        a = AudioFileClip(str(mp3))
        dur = a.duration + 0.2
        total += dur
        clips.append(VideoClip(push_in(tmp / f"f{i + 1}.jpg", dur), duration=dur).set_audio(a))
    if total > MAX_SECONDS:
        print(f"[PREMARKET] {total:.1f}s is over {MAX_SECONDS:.0f}s - not building")
        return None
    final = concatenate_videoclips(clips, method="compose")
    mp4 = out / f"{day.isoformat()}_premarket.mp4"
    final.write_videofile(str(mp4), fps=24, codec="libx264", audio_codec="aac", preset="medium", logger=None)
    cap = caption(rows, v, results, day)
    meta = {"title": f"Market khulne se pehle: global cues {v}", "description": cap.split("\n\n")[0], "caption": cap, "verdict": v, "date": day.isoformat(), "duration_s": round(total, 1),
            "results": results[:6], "built_at": datetime.now().isoformat(timespec="seconds")}
    (out / f"{day.isoformat()}_premarket_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[PREMARKET] built {mp4.name} {total:.1f}s verdict={v} results={results}")
    return mp4


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    out = argv[argv.index("--out") + 1] if "--out" in argv else "output/premarket"
    day = argv[argv.index("--day") + 1] if "--day" in argv else None
    try:
        build(out, day)
    except Exception as e:
        print(f"[PREMARKET] skipped (fail-open): {str(e)[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
