import re
import tech_short as T
import tech_daily as D

NEW = ["battery_drain", "digital_arrest", "mobile_virus", "whatsapp_hack"]


def test_new_topics_are_complete_and_safe():
    for k in NEW:
        t = T.TOPICS[k]
        assert len(t["lines"]) == len(t["caps"]) == len(t["scenes"]) == len(t["queries"]) == 5
        assert not re.search(r"\d", " ".join(t["lines"])), "narration must spell numbers as words"
        assert t["yt_title"].endswith("#shorts") and len(t["yt_title"]) <= 100
        assert k in T.OBJ3D and k in D.TOPIC_ORDER


def test_kyu_spelling_and_hashtags():
    assert "Kyun" not in T.TOPICS["laptop_hang"]["yt_title"]
    h = T.topic_hashtags(T.TOPICS["battery_drain"])
    assert h.endswith("#TechTips") and "#Hinglish" not in h and h.count("#") == 3


def test_queue_order_puts_new_topics_before_old_queue():
    o = D.TOPIC_ORDER
    assert o.index("battery_drain") < o.index("laptop_hang") and o.index("charge_overnight") < o.index("battery_drain")
