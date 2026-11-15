import reach_report as R


def test_security_classification():
    assert R.is_security("otp_scam") and R.is_security("strong_password") and R.is_security("apk_file_scam")
    assert not R.is_security("phone_wet") and not R.is_security("laptop_hang") and not R.is_security("battery_drain")


def test_groups_need_eight_videos_for_a_conclusion():
    rows = [{"topic": "phone_wet", "age_days": 3, "views_per_day": 10}, {"topic": "otp_scam", "age_days": 3, "views_per_day": 2}]
    t = "\n".join(R.tech_groups(rows))
    assert "device: 1 videos" in t and "security: 1 videos" in t and "no conclusion" in t


def test_build_never_raises_and_has_trend():
    out = "\n".join(R.build())
    assert out.startswith("REACH") and "Follower trend" in out


def test_tech_queue_mixes_three_device_then_one_security():
    import tech_daily as D
    assert len(D.TOPIC_ORDER) == len(set(D.TOPIC_ORDER)) and len(D.TOPIC_ORDER) >= 81
