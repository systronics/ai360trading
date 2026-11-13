from pathlib import Path

import upload_facebook as U


def _run(results, stages):
    calls = []

    def fake(ig, path, caption, token):
        calls.append(str(path))
        i = len(calls) - 1
        U._IG_STAGE = stages[min(i, len(stages) - 1)]
        return results[min(i, len(results) - 1)]

    U._upload_reel_to_instagram_once = fake
    U.time.sleep = lambda s: None
    U._ig_safe_copy = lambda p: Path(str(p) + "_ig.mp4")
    return calls


def test_success_first_try_no_retry():
    calls = _run(["123"], ["publish"])
    assert U.upload_reel_to_instagram("ig", Path("a.mp4"), "c", "t") == "123" and len(calls) == 1


def test_pre_publish_failure_retries_then_succeeds():
    calls = _run([None, "55"], ["pre", "publish"])
    assert U.upload_reel_to_instagram("ig", Path("a.mp4"), "c", "t") == "55" and len(calls) == 2


def test_two_failures_then_reencoded_copy():
    calls = _run([None, None, "77"], ["pre", "pre", "publish"])
    assert U.upload_reel_to_instagram("ig", Path("a.mp4"), "c", "t") == "77"
    assert len(calls) == 3 and calls[2].endswith("_ig.mp4")


def test_publish_stage_failure_never_retries():
    calls = _run([None], ["publish"])
    assert U.upload_reel_to_instagram("ig", Path("a.mp4"), "c", "t") is None and len(calls) == 1


def test_no_account_skips():
    calls = _run([None], ["pre"])
    assert U.upload_reel_to_instagram("", Path("a.mp4"), "c", "t") is None and len(calls) == 1
