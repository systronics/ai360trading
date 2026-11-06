import live_prices_upstox as U


def test_parse_quote_pct_from_prev_close():
    q = U.parse_quote({"last_price": 105.0, "prev_close_price": 100.0, "volume": 12345, "net_change": 5.0})
    assert q == {"cmp": 105.0, "pct": 5.0, "vol": 12345}


def test_parse_quote_pct_from_net_change():
    q = U.parse_quote({"last_price": 95.0, "net_change": -5.0, "volume": 1})
    assert q["pct"] == -5.0


def test_parse_quote_bad_inputs():
    assert U.parse_quote(None) is None
    assert U.parse_quote({}) is None
    assert U.parse_quote({"last_price": 0}) is None
    assert U.parse_quote({"last_price": "x"}) is None
    q = U.parse_quote({"last_price": 10})
    assert q["pct"] is None and q["vol"] is None


class FakeResp:
    def __init__(self, code, js): self.status_code, self._js, self.text = code, js, str(js)
    def json(self): return self._js


class FakeHTTP:
    def __init__(self, resp): self.resp, self.calls = resp, []
    def get(self, url, params=None, headers=None, timeout=0):
        self.calls.append((url, params, headers)); return self.resp


def test_fetch_quotes_maps_by_instrument_token_and_hides_nothing_on_error():
    data = {"data": {"NSE_EQ:AAA": {"instrument_token": "NSE_EQ|K1", "last_price": 50, "prev_close_price": 40, "volume": 7},
                     "NSE_EQ:BBB": {"instrument_token": "NSE_EQ|K2", "last_price": 0}}}
    h = FakeHTTP(FakeResp(200, data))
    out = U.fetch_quotes("TOKEN", {"NSE:AAA": "NSE_EQ|K1", "NSE:BBB": "NSE_EQ|K2"}, session=h)
    assert list(out) == ["NSE:AAA"] and out["NSE:AAA"]["pct"] == 25.0
    assert h.calls[0][2]["Authorization"] == "Bearer TOKEN"
    bad = U.fetch_quotes("TOKEN", {"NSE:AAA": "NSE_EQ|K1"}, session=FakeHTTP(FakeResp(401, {"errors": "bad TOKEN"})))
    assert bad == {}                                            # fail-open
    assert U.fetch_quotes("", {"NSE:AAA": "k"}) == {}           # no token


def test_chunking_over_500():
    m = {f"NSE:S{i}": f"NSE_EQ|K{i}" for i in range(1200)}
    h = FakeHTTP(FakeResp(200, {"data": {}}))
    U.fetch_quotes("T", m, session=h)
    assert len(h.calls) == 3


def test_key_for():
    assert U.key_for("NSE:NIFTY50", {}) == "NSE_INDEX|Nifty 50"
    assert U.key_for("NSE:TCS", {"TCS": "NSE_EQ|X"}) == "NSE_EQ|X"
    assert U.key_for("NSE:ZZZ", {"TCS": "NSE_EQ|X"}) is None
