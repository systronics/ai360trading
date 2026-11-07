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


def test_hashtags_for():
    import tech_daily as T
    assert T.hashtags_for({"tags": ["phone hot kyun hota hai", "x"]}) == "#PhoneHot #TechTips #Hinglish"
    assert T.hashtags_for({}) == "#TechTips #Hinglish"
