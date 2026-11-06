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
