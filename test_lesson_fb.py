import datetime as dt
import types

import lesson_fb as fb


def test_off_by_default_and_hindi_india_only():
    assert not fb.enabled("in", "hi", {})
    assert not fb.enabled("in", "hi", {"LESSON_FB": "off"})
    assert fb.enabled("in", "hi", {"LESSON_FB": "on"})
    assert not fb.enabled("us", "en", {"LESSON_FB": "on"})
    assert not fb.enabled("in", "en", {"LESSON_FB": "on"})


def test_never_posts_the_same_lesson_twice():
    assert not fb.already_posted({}, "au01")
    assert not fb.already_posted({"au01": {"in-hi": {"video": "x"}}}, "au01")
    assert fb.already_posted({"au01": {"in-hi": {"video": "x", "fb_video": "123"}}}, "au01")


def test_schedule_window():
    now = 1_000_000.0
    assert not fb.schedule_ok(now + 60, now)
    assert fb.schedule_ok(now + 4 * 86400, now)
    assert not fb.schedule_ok(now + 80 * 86400, now)


def test_caption_is_compact_and_honest():
    c = fb.caption("T", "idea " * 200, "AI voice", "not advice")
    assert c.startswith("T") and "not advice" in c and "AI voice" in c and len(c) < 700


def test_bad_time_posts_nothing_and_valid_time_is_unpublished(tmp_path, monkeypatch):
    f = tmp_path / "v.mp4"
    f.write_bytes(b"x")
    calls = []

    class R:
        def json(self):
            return {"id": "999"}

    def fake_post(url, data=None, files=None, timeout=0):
        calls.append(data)
        return R()

    monkeypatch.setattr(fb.requests, "post", fake_post)
    monkeypatch.setattr(fb, "_page_token", lambda p, t: "tok")
    now = 1_000_000.0
    soon = dt.datetime.fromtimestamp(now + 60, dt.timezone.utc)
    assert fb.post_scheduled(str(f), "t", "x", soon, "p", "u", now_epoch=now) is None
    assert calls == []                                    # too soon: no upload, never an immediate post
    ok = dt.datetime.fromtimestamp(now + 3 * 86400, dt.timezone.utc)
    assert fb.post_scheduled(str(f), "t", "x", ok, "p", "u", now_epoch=now) == "999"
    assert calls[0]["published"] == "false" and calls[0]["unpublished_content_type"] == "SCHEDULED"
    assert calls[0]["scheduled_publish_time"] == str(int(ok.timestamp()))


def test_meta_error_returns_none(tmp_path, monkeypatch):
    f = tmp_path / "v.mp4"
    f.write_bytes(b"x")

    class R:
        def json(self):
            return {"error": {"message": "nope"}}

    monkeypatch.setattr(fb.requests, "post", lambda *a, **k: R())
    monkeypatch.setattr(fb, "_page_token", lambda p, t: "tok")
    now = 1_000_000.0
    ok = dt.datetime.fromtimestamp(now + 3 * 86400, dt.timezone.utc)
    assert fb.post_scheduled(str(f), "t", "x", ok, "p", "u", now_epoch=now) is None
