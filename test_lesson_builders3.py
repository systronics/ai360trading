import lesson_builders as B
import lesson_bank as LB
import lesson_engine as E


def _texts(pack, lang):
    return " ".join(sc["text"][lang] for sc in pack["scenes"])


def test_registered_after_existing_queue():
    assert B.QUEUE[-3:] == ["sw01", "ct01", "sv01"]
    for k in ("sw01", "ct01", "sv01"):
        assert B.LESSON_REGIONS[k] == ["us", "in"] and k in B.BUILDERS


def test_quality_gate_and_hindi_numbers_for_every_edition():
    for lid in ("sw01", "ct01", "sv01"):
        for region in ("us", "in"):
            pack = B.BUILDERS[lid](region)
            en = _texts(pack, "en")
            ok, why = LB.quality_gate(en, pack["facts"])
            assert ok, (lid, region, why)
            assert len(pack["scenes"]) == 5
            if region == "in":
                okn, miss = E.numbers_preserved(en, _texts(pack, "hi"))
                assert okn, (lid, miss)
                assert "रूल" not in _texts(pack, "hi")


def test_survivorship_example_arithmetic():
    pack = B.BUILDERS["sv01"]("in")
    assert "22.5" in _texts(pack, "en")
    assert (100 * 10 + 20 * 40) / 80 == 22.5
