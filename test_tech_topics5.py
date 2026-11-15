import re
import tech_topics5 as X
import tech_topics4, tech_topics3, tech_topics2


def test_thirty_unique_topics():
    assert len(X.TOPICS5) == 30 and len(X.ORDER) == 30 and set(X.ORDER) == set(X.TOPICS5)


def test_no_clash_with_existing_keys():
    old = set(tech_topics4.TOPICS4) | set(tech_topics3.TOPICS3) | set(getattr(tech_topics2, "TOPICS2", {}))
    assert not (old & set(X.TOPICS5))


def test_structure_and_safety():
    for k, t in X.TOPICS5.items():
        assert len(t["lines"]) == 5 and len(t["caps"]) == 5 and len(t["scenes"]) == 5 and len(t["queries"]) == 5, k
        body = " ".join(t["lines"])
        assert not re.search(r"\d", body), (k, "digit in narration")
        words = len(body.split())
        assert 85 <= words <= 135, (k, words)
        assert "Kyun" not in t["yt_title"] and t["yt_title"].endswith("#shorts"), k
        assert len(t["yt_title"]) <= 100, k
        assert "कल मिलते हैं" in t["lines"][-1], k
        for ban in ("गारंटी", "100%", "पक्का", "हैक कर", "ज़रूर कमाओ"):
            assert ban not in body, (k, ban)
        assert t["kind"] in ("serious", "myth", "explain"), k
        assert X.OBJ3D.get(k), k


def test_scam_topics_name_the_helpline_as_words():
    for k in ("loan_app_scam", "sim_block_scam", "courier_scam", "screen_share_scam", "link_clicked", "apk_file_scam"):
        assert "एक नौ तीन शून्य" in " ".join(X.TOPICS5[k]["lines"]), k


def test_register_never_overwrites():
    d = {"phone_hang": {"keep": 1}}
    X.register(d)
    assert d["phone_hang"] == {"keep": 1} and len(d) == 30
