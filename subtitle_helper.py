"""
subtitle_helper.py — AI360Trading
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.0 (2026-05-31):
  Builds a real .srt subtitle track from the spoken script and uploads it to
  YouTube, so YouTube can AUTO-TRANSLATE the captions into the viewer's own
  language (US / UK / Brazil / India ...). This multiplies reach with zero new
  content and ₹0 cost.

  Two pieces, both FULLY FAIL-OPEN (a subtitle problem must never break the
  income-critical upload):
    - build_srt()      : pure text/timing, no heavy deps → writes an .srt.
    - upload_caption() : YouTube captions().insert. NOTE this needs the
                         `youtube.force-ssl` OAuth scope; if the token lacks it
                         we log a clear "re-auth" hint and skip (no crash).

  IMPORTANT — hook offset: reels/shorts now start with a ~1.4s bold hook intro
  (hook_helper) and the narration begins AFTER it, so pass start_offset = the
  hook length for those videos or the captions will run early.

  Even without the .srt, setting `defaultAudioLanguage` on the upload lets
  YouTube auto-generate + auto-translate captions on its own — callers do that
  too as a no-scope fallback.
"""

import os
from pathlib import Path


def _fmt_ts(sec: float) -> str:
    if sec < 0:
        sec = 0.0
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms == 1000:
        ms = 0
        s += 1
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(spoken_text: str, duration: float, out_path,
              start_offset: float = 0.0, words_per_cue: int = 7):
    """
    Write an .srt whose cues are spread PROPORTIONALLY across `duration`
    (same word-timing model as the burned-in captions → ₹0, deterministic,
    no speech alignment). `start_offset` shifts every cue (use the hook length
    for hooked reels/shorts). Returns the path, or None on any problem.
    """
    try:
        text = " ".join((spoken_text or "").split())
        if not text or not duration or duration <= 0:
            return None
        words = text.split()
        total = len(words)
        if total == 0:
            return None

        cues = [" ".join(words[i:i + words_per_cue])
                for i in range(0, total, words_per_cue)]

        out, t = [], float(start_offset)
        for idx, cue in enumerate(cues):
            seg = duration * (len(cue.split()) / total)
            start = t
            end = (start_offset + duration) if idx == len(cues) - 1 else (t + seg)
            if end <= start:
                end = start + 0.4
            out.append(str(idx + 1))
            out.append(f"{_fmt_ts(start)} --> {_fmt_ts(end)}")
            out.append(cue)
            out.append("")
            t += seg

        Path(out_path).write_text("\n".join(out), encoding="utf-8")
        return str(out_path)
    except Exception as e:
        print(f"  ⚠️ subtitle build skipped (fail-open): {e}")
        return None


def build_srt_segments(segments, out_path, words_per_cue: int = 7):
    """
    Multi-segment .srt for videos assembled from timed pieces (e.g. the education
    video's per-slide audio, or kids per-scene narration).
    `segments` = list of (text, start_sec, duration_sec). Each segment's text is
    chunked into cues spread across its own window, with continuous numbering.
    Fail-open → returns None on any problem.
    """
    try:
        out, idx = [], 1
        for text, seg_start, seg_dur in segments:
            text = " ".join((text or "").split())
            if not text or not seg_dur or seg_dur <= 0:
                continue
            words = text.split()
            total = len(words)
            cues = [" ".join(words[i:i + words_per_cue])
                    for i in range(0, total, words_per_cue)]
            t = float(seg_start)
            for j, cue in enumerate(cues):
                cdur = seg_dur * (len(cue.split()) / total)
                start = t
                end = (seg_start + seg_dur) if j == len(cues) - 1 else (t + cdur)
                if end <= start:
                    end = start + 0.4
                out.append(str(idx))
                out.append(f"{_fmt_ts(start)} --> {_fmt_ts(end)}")
                out.append(cue)
                out.append("")
                idx += 1
                t += cdur
        if not out:
            return None
        Path(out_path).write_text("\n".join(out), encoding="utf-8")
        return str(out_path)
    except Exception as e:
        print(f"  ⚠️ subtitle (segments) skipped (fail-open): {e}")
        return None


def upload_caption(youtube, video_id: str, srt_path, language: str,
                   name: str = "AI360Trading") -> bool:
    """
    Upload an .srt as a YouTube caption track (enables viewer auto-translate).
    FAIL-OPEN — needs the youtube.force-ssl scope; if the token lacks it we log
    a clear hint and return False without raising.
    """
    if not youtube or not video_id or not srt_path or not os.path.exists(str(srt_path)):
        return False
    try:
        from googleapiclient.http import MediaFileUpload
        body = {"snippet": {"videoId": video_id, "language": language,
                            "name": name, "isDraft": False}}
        media = MediaFileUpload(str(srt_path), mimetype="application/octet-stream", resumable=False)
        youtube.captions().insert(part="snippet", body=body, media_body=media).execute()
        print(f"  ✅ Caption track uploaded ({language}) — YouTube can now auto-translate it")
        return True
    except Exception as e:
        msg = str(e)
        if any(k in msg.lower() for k in ("insufficient", "scope", "forbidden", "403")):
            print("  ⚠️ Caption upload needs the youtube.force-ssl scope — re-auth the "
                  "YouTube token to enable auto-translate subtitles (skipped, fail-open)")
        else:
            print(f"  ⚠️ Caption upload skipped (fail-open): {msg[:120]}")
        return False
