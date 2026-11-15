import json
import lesson_pages as P
import lesson_builders as B


def test_slug_and_url():
    assert P.slugify("Expectancy: The Number That Decides If Your Trading System Makes Money") == "expectancy-the-number-that-decides-if-your-trading-system-makes-money"[:70].rstrip("-")
    assert P.page_url("abc") == "https://ai360trading.in/trading-lessons/abc/"


def test_render_every_pure_lesson():
    for lid in P.PURE:
        pack = B.BUILDERS[lid]("us")
        text, entry = P.render(pack, "vid12345678", "2026-11-21T14:00:00+00:00", "hindiVid123")
        assert "{%" not in text and "{{" not in text
        assert f"/trading-lessons/{entry['slug']}/" in text and "vid12345678" in text and "not investment advice" in text.lower()
        assert "The rule to remember" in text and "hindiVid123" in text and "wa.me" in text
        fm = text.split("---")[1]
        assert "layout: default" in fm and json.loads(fm.split("title: ", 1)[1].split("\n", 1)[0])
        json.loads(text.split('application/ld+json">')[1].split("</script>")[0])


def test_skips_empty_or_unsafe():
    assert P.render({"title": {"en": "T"}, "scenes": []}, "v", "2026-11-21") is None
    assert P.render({"title": {"en": "T {{ x }}"}, "scenes": [{"text": {"en": "ok"}}]}, "v", "2026-11-21") is None


def test_english_video_picks_us_then_in():
    assert P.english_video({"us-en": {"video": "A", "publish_at": "x"}, "in-hi": {"video": "H"}}) == ("A", "x")
    assert P.english_video({"in-hi": {"video": "H"}}) == (None, "")
