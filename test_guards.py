"""Guards added 2026-11-06 after the silent `subs=` bug (ATR read as 0 for 3.5 months)."""
import wave
import numpy as np
import check_calls


def test_no_call_mismatches_in_repo():
    assert check_calls.main(["--quiet"]) == 0


def test_trim_breath_cuts_edges(tmp_path):
    import tech_short as T
    sr = 24000
    t = np.arange(sr * 2) / sr
    breath = (np.random.randn(sr) * 400).astype(np.int16)
    speech = (np.sin(2 * np.pi * 180 * t) * np.hanning(len(t)) * 12000).astype(np.int16)
    p = tmp_path / "x.wav"
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(np.concatenate([breath, speech, breath]).tobytes())
    assert T.trim_breath(p) is True
    with wave.open(str(p)) as w:
        assert 1.5 < w.getnframes() / sr < 2.2


def test_source_and_docs_are_excluded_from_the_public_website():
    """2026-11-17: GitHub Pages publishes every non-excluded root file. Jekyll's exclude uses explicit names (a '*.md' glob would also hide _posts/_pages), so each root
    .py / .gs / .bat / .ps1 and every root .md WITHOUT front matter must be listed in _config.yml exclude."""
    import os
    import re
    root = os.path.dirname(os.path.abspath(__file__))
    cfg = open(os.path.join(root, "_config.yml"), encoding="utf-8").read().replace("\r\n", "\n")
    block = re.search(r"^exclude:\n((?:  - .*\n)+)", cfg, re.M).group(1)
    excluded = {ln.strip()[2:].strip() for ln in block.splitlines()}
    missing = []
    for f in sorted(os.listdir(root)):
        p = os.path.join(root, f)
        if not os.path.isfile(p):
            continue
        if f.endswith((".py", ".gs", ".bat", ".ps1")):
            need = True
        elif f.endswith(".md"):
            need = not open(p, encoding="utf-8", errors="ignore").read(4).startswith("---")
        else:
            need = False
        if need and f not in excluded:
            missing.append(f)
    assert not missing, f"served publicly by GitHub Pages - add to _config.yml exclude: {missing}"
