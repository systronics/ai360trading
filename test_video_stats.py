from datetime import datetime, timezone
import video_stats as V


def test_summarize_orders_by_views_per_day():
    now = datetime(2026, 11, 10, tzinfo=timezone.utc)
    vids = [{"id": "a", "title": "A", "published": "2026-11-08T00:00:00Z", "views": 10},      # 2 days -> 5/day
            {"id": "b", "title": "B", "published": "2026-11-01T00:00:00Z", "views": 54},      # 9 days -> 6/day
            {"id": "bad", "title": "X", "published": "not a date", "views": 5}]
    out = V.summarize(vids, now, {"b": "phone_heat"})
    assert [x["id"] for x in out] == ["b", "a"]
    assert out[0]["topic"] == "phone_heat" and out[0]["views_per_day"] == 6.0
    assert V.summarize([], now) == []


def test_topic_hashtags():
    import tech_short as T
    assert T.topic_hashtags({"tags": ["phone hot kyun hota hai", "phone heating problem", "x"]}) == "#PhoneHot #PhoneHeating #TechTips"
    assert T.topic_hashtags({}) == "#TechTips"
    assert T.topic_hashtags({"tags": ["tech explained hinglish", "hinglish tips now"]}) == "#TipsNow #TechTips"


def test_extra_tags_reads_real_phrases(tmp_path, monkeypatch):
    import json
    import tech_daily as T
    (tmp_path / "_data").mkdir()
    (tmp_path / "_data" / "tech_keywords.json").write_text(json.dumps({"phone garam kyun hota hai": {"youtube": ["phone garam kyu hota hai", "फोन गर्म क्यों होता है", "phone garam kyun hota hai"]}}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    out = T.extra_tags({"tags": ["phone hot kyun hota hai", "phone garam kyun hota hai"]})
    assert out == ["phone garam kyu hota hai"]          # the Devanagari one is skipped, the duplicate tag is skipped
    assert T.extra_tags({"tags": ["wifi slow"]}) == []
