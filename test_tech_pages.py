import json
import tech_pages as P
import tech_short as TS


def test_slug_and_url():
    assert P.slug("phone_heat") == "phone-heat" and P.page_url("phone_heat") == "https://ai360trading.in/tech-tips/phone-heat/"


def test_render_every_topic_is_liquid_safe_and_unique():
    seen = set()
    for key in ("phone_heat", "laptop_hang", "phone_hang", "apk_file_scam", "data_backup"):
        r = P.render(key, TS.TOPICS[key], "abcDEF12345", "2026-11-16T13:00:00+00:00")
        assert r, key
        text, entry = r
        assert "{%" not in text and "{{" not in text and "कल मिलते हैं" not in text
        assert f"/tech-tips/{P.slug(key)}/" in text and "abcDEF12345" in text and "technician" in text
        fm = text.split("---")[1]
        assert "layout: default" in fm and json.loads(fm.split("title: ", 1)[1].split("\n", 1)[0])
        assert text not in seen
        seen.add(text)
        assert entry["slug"] == P.slug(key) and entry["date"] == "2026-11-16"


def test_render_skips_unsafe_or_empty():
    assert P.render("x", {"lines": []}, "vid", "2026-11-16") is None
    assert P.render("x", {"yt_title": "a {{ b }}", "lines": ["ok line"]}, "vid", "2026-11-16T13:00:00+00:00") is None
    assert P.render("x", {"lines": ["ok"]}, "", "2026-11-16") is None


def test_description_link_in_tech_daily():
    import tech_daily as D
    src = open("tech_daily.py", encoding="utf-8").read()
    assert "page_line" in src and "tech_pages" in src
