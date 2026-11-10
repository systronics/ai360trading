import re
import tech_topics4 as X
import tech_topics3, tech_topics2


def test_thirty_unique_topics():
    assert len(X.TOPICS4) == 30 and len(X.ORDER) == 30 and set(X.ORDER) == set(X.TOPICS4)


def test_no_clash_with_existing_keys():
    old = set(tech_topics3.TOPICS3) | set(tech_topics2.TOPICS2 if hasattr(tech_topics2, "TOPICS2") else [])
    assert not (old & set(X.TOPICS4))


def test_structure_and_safety():
    for k, t in X.TOPICS4.items():
        assert len(t["lines"]) == 5 and len(t["caps"]) == 5 and len(t["scenes"]) == 5 and len(t["queries"]) == 5, k
        body = " ".join(t["lines"])
        assert not re.search(r"\d", body), (k, "digit in narration")
        words = len(body.split())
        assert 85 <= words <= 135, (k, words)
        assert "Kyun" not in t["yt_title"] and t["yt_title"].endswith("#shorts"), k
        assert len(t["yt_title"]) <= 100, k
        assert "कल मिलते हैं" in t["lines"][-1], k
        for ban in ("गारंटी", "100%", "पक्का"):
            assert ban not in body, (k, ban)


def test_register_never_overwrites():
    d = {"phone_slow": {"keep": 1}}
    X.register(d)
    assert d["phone_slow"] == {"keep": 1} and len(d) == 30


def test_engage_lines_ask_a_question_and_a_follow():
    import tech_daily as D
    for kind in ("serious", "myth", "explain", "anything"):
        t = D.engage_lines(kind)
        assert "Comment mein batao" in t and "Follow karo" in t and "\n" in t
    assert "Hinglish" not in D.engage_lines("explain")


def test_short_hook_never_empty_and_never_longer():
    import tech_short as T
    for k, t in T.TOPICS.items():
        if "lines" not in t:
            continue
        s = T.short_hook(t["lines"][0])
        assert s.strip() and len(s) <= len(t["lines"][0]), k
        assert len(s.split()) <= 10 or s == t["lines"][0], k
    assert T.short_hook("फ़ोन गर्म क्यों होता है? इसकी वजह जानो।") == "फ़ोन गर्म क्यों होता है?"
    assert T.short_hook("एक दो तीन चार पाँच छह सात आठ नौ दस ग्यारह बारह? बाक़ी।").startswith("एक दो")   # too long -> unchanged
