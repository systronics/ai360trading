import xml.etree.ElementTree as ET
from datetime import date
import site_posts as S
import threads_post as T
import pin_feed as P

FM = '---\nlayout: post\ntitle: "Gold Hits 4,050: What It Means"\ndate: 2026-11-07\npermalink: /world-markets/gold-hits-1732/\nexcerpt: "A calm look at gold, fear and your plan."\ncontent_mode: "weekend"\npillar: "world-markets"\nimage: /public/image/articles/x.png\n---\nbody'


def test_front_matter_and_url():
    fm = S.parse_front_matter(FM)
    assert fm["title"] == "Gold Hits 4,050: What It Means" and fm["content_mode"] == "weekend"
    assert S.post_url(fm) == "https://ai360trading.in/world-markets/gold-hits-1732/"
    assert S.parse_front_matter("no front matter") == {}
    assert S.post_url({}) == ""


def test_threads_text_limits_and_disclosure():
    t = T.build_text("T" * 120, "word " * 200)
    assert len(t) <= 480 and "AI-assisted" in t and "http" not in t
    short = T.build_text("Short title", "")
    assert short.startswith("Short title") and len(short) <= 480


def test_threads_pick_skips_posted():
    posts = [{"url": "a"}, {"url": "b"}]
    assert T.pick_article(posts, ["a"])["url"] == "b"
    assert T.pick_article(posts, ["a", "b"]) is None


def test_dry_run_never_posts(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "_posts").mkdir()
    (tmp_path / "_posts" / "2026-11-07-x.md").write_text(FM, encoding="utf-8")
    monkeypatch.setattr(S, "recent_posts", lambda posts_dir="_posts", max_age_days=3, today=None: [{"title": "X", "url": "https://ai360trading.in/x/", "excerpt": "e"}])
    called = []
    monkeypatch.setattr(T.requests, "post", lambda *a, **k: called.append(1))
    monkeypatch.delenv("THREADS_MODE", raising=False)
    monkeypatch.setenv("THREADS_ACCESS_TOKEN", "tok")
    monkeypatch.setenv("THREADS_USER_ID", "1")
    assert T.run() == 0 and not called
    monkeypatch.setenv("THREADS_MODE", "scheduled")
    monkeypatch.delenv("THREADS_ACCESS_TOKEN")
    assert T.run() == 0 and not called                                  # scheduled but no token: still nothing posted


def test_pinterest_feed_is_rss2_with_images_and_claimed_domain():
    items = [{"title": 'Gold & "Fear" <ok>', "url": "https://ai360trading.in/a/", "excerpt": "x " * 300, "date": "2026-11-07", "image_url": "https://ai360trading.in/public/image/pins/a.jpg"}]
    root = ET.fromstring(P.build_feed(items))
    assert root.tag == "rss" and root.attrib["version"] == "2.0"
    it = root.find("channel/item")
    assert it.find("link").text.startswith("https://ai360trading.in/")
    assert it.find("enclosure").attrib["url"].endswith("a.jpg")
    assert len(it.find("title").text) <= 100


def test_pin_image_is_written(tmp_path):
    from PIL import Image
    p = tmp_path / "pins" / "a.jpg"
    assert P.make_pin("A very long article title about gold fear greed and what a calm Indian investor should do next week", "world-markets", p)
    assert Image.open(p).size == (1000, 1500)
