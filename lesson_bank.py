"""
lesson_bank.py — evergreen lesson topic bank + picker + quality gate  (v1.0, 2026-10-18)
=========================================================================================
Part of the LESSON ENGINE for serious traders (see lesson_engine.py). Everything here is
EVERGREEN: lessons teach a rule, a risk idea or a documented story, backed by our own
data where possible, so a video made today is still useful in three years.

Types
  rule_chart   : a rule demonstrated on REAL historical charts (data: price history)
  autopsy      : one of OUR OWN closed paper trades, win or loss (data: History ledger)
  research     : our own backtests / audits, with the limits stated (data: our results)
  risk_math    : position sizing, drawdown, expectancy (data: pure maths, animated)
  psychology   : documented market events / behaviour stories told in our own words
  book_idea    : ideas from well-known trading books, in OUR words, credited (no copied text)

QUALITY GATE (quality_gate) — a lesson only publishes if its script has
  1. at least one real number from the supplied facts,
  2. a clear applicable "Rule:" line,
  3. an honest limit (what it does NOT prove),
  4. no hype / advice phrases (guaranteed, sure shot, buy now ...),
  5. a sensible length.
It is a pure function so it is unit-testable and never needs the network.
"""

import re
from datetime import date

# (id, type, title, angle)   angle = the one-sentence teaching idea the AI must keep
_T = [
 # ── rule_chart (10) ───────────────────────────────────────────────────────────
 ("rc01", "rule_chart", "The 50-day closing-high breakout: 3 real examples, wins and losses", "A breakout is a close above the highest close of 50 days; show a win, a stop-out and a chop."),
 ("rc02", "rule_chart", "Why we wait for the CLOSE, not the intraday spike", "Intraday breakouts reverse often; the closing price is the vote that counts."),
 ("rc03", "rule_chart", "The 50-day average as a trend filter: what it keeps you out of", "Only take longs above the 50-day average; show trades it would have avoided."),
 ("rc04", "rule_chart", "Trailing a stop with 3x ATR: letting winners run on a real chart", "A volatility-based trailing stop lets a trend breathe while capping the loss."),
 ("rc05", "rule_chart", "Base and breakout: how a tight 20-day range precedes big moves", "Tight ranges compress volatility; show examples and the false starts."),
 ("rc06", "rule_chart", "Support and retest: why broken resistance often becomes support", "Show a retest that held and one that failed."),
 ("rc07", "rule_chart", "Relative strength: picking the strongest stocks in a rising market", "Stocks outperforming the index tend to keep leading; show the comparison."),
 ("rc08", "rule_chart", "The failed breakout: how to spot it and exit small", "A close back below the level is information; exit rules limit the damage."),
 ("rc09", "rule_chart", "Gap-ups: when a gap is strength and when it is a trap", "Gaps with volume and follow-through vs gaps that fill."),
 ("rc10", "rule_chart", "Higher highs and higher lows: reading trend structure on a real chart", "Trend is structure, not a feeling; mark the swing points."),
 # ── autopsy (10) ──────────────────────────────────────────────────────────────
 ("au01", "autopsy", "Autopsy of our best closed trade: what went right", "Walk a real winning paper trade: setup, entry, stop, exit and why it worked."),
 ("au02", "autopsy", "Autopsy of our worst closed trade: what went wrong", "Walk a real losing trade honestly; what rule would have reduced the loss."),
 ("au03", "autopsy", "A stop-loss that saved us: the trade that kept falling", "Show a trade that kept falling after the stop; the stop did its job."),
 ("au04", "autopsy", "A stop-loss that cost us: the trade that bounced right after", "Stops will sometimes be wrong; the cost of that is the price of safety."),
 ("au05", "autopsy", "The trade we should not have taken: a rule we broke", "A real trade that broke our own entry rules and what it taught."),
 ("au06", "autopsy", "Three small losses in a row: how the ledger looks during a bad week", "Show a real losing streak and why it is normal."),
 ("au07", "autopsy", "Our intraday trades vs our swing trades: what the ledger says", "Real results by strategy; swing carried the profit, intraday did not."),
 ("au08", "autopsy", "Time-stop exits: the trades that went nowhere", "Many trades do nothing; a time stop frees capital."),
 ("au09", "autopsy", "One winner paid for many losers: the shape of our P/L", "Few large winners, many small losers; show the real distribution."),
 ("au10", "autopsy", "Options trades that hit the loss cap: what we learned", "Real option paper trades that were stopped at the cap and what changed."),
 # ── research (10) ─────────────────────────────────────────────────────────────
 ("rs01", "research", "We tested buying market bottoms for 5 years: it lost to random", "Buying deep drawdowns did not beat random entries in our test."),
 ("rs02", "research", "Previous-day high: why buying above it hurt our results", "Entries above the previous day high lost money in our ledger."),
 ("rs03", "research", "Breakouts by year: why one great year can fool you", "Most of the gain came from one year; show per-year results."),
 ("rs04", "research", "Survivorship bias: the flaw in almost every backtest you see", "Testing only today's winners flatters results; how to correct for it."),
 ("rs05", "research", "50 vs 100 days: does the breakout window matter", "Longer windows were similar; do not over-tune a rule."),
 ("rs06", "research", "Does the market trend change breakout results", "Breakouts did better with the index above its 50-day average."),
 ("rs07", "research", "ADX filter: did trend strength add anything to our breakouts", "Show what the ADX filter did and did not change."),
 ("rs08", "research", "Win rate is not the point: expectancy explained with our numbers", "41% winners can still make money when winners are bigger than losers."),
 ("rs09", "research", "Our volume filter: the shadow test we ran", "Show the shadow-ledger idea: track what a rule blocks."),
 ("rs10", "research", "How we test a trading rule honestly in 5 steps", "Define, backtest, split by year, add costs, track forward."),
 # ── risk_math (10) ────────────────────────────────────────────────────────────
 ("rm01", "risk_math", "Why a 50% loss needs a 100% gain", "Drawdown maths: recovery needs more than the loss; animate it."),
 ("rm02", "risk_math", "Position sizing in one formula: risk 1% per trade", "Size = risk amount / stop distance; worked example."),
 ("rm03", "risk_math", "Expectancy: the number that decides if a system works", "Expectancy = win% x avg win - loss% x avg loss; worked example."),
 ("rm04", "risk_math", "Ten losses in a row: how likely is it really", "Streak probability for a given win rate; animate a simulation."),
 ("rm05", "risk_math", "Risk-reward vs win rate: the trade-off chart", "Which combinations are profitable; show the break-even line."),
 ("rm06", "risk_math", "Costs matter: how brokerage and slippage eat small edges", "Show a small edge before and after costs."),
 ("rm07", "risk_math", "Leverage and margin: how it magnifies mistakes", "Same move, with and without leverage; the risk of ruin."),
 ("rm08", "risk_math", "Compounding vs consistency: why avoiding big losses wins", "Two equity curves with equal average return but different volatility."),
 ("rm09", "risk_math", "How big should your stop be: ATR explained", "ATR as a measure of normal noise; place stops outside it."),
 ("rm10", "risk_math", "The Kelly idea in plain words and why traders use half", "Optimal sizing theory and why it is dangerous to use in full."),
 # ── psychology (10) ───────────────────────────────────────────────────────────
 ("ps01", "psychology", "Why 90% of traders lose: it is rarely the strategy", "Behaviour, not method, is where most accounts fail."),
 ("ps02", "psychology", "Revenge trading: the anatomy of the worst trade of the day", "The pattern after a loss and a simple rule to break it."),
 ("ps03", "psychology", "FOMO: chasing a stock after it has already run", "Why chasing hurts and what a pullback plan looks like."),
 ("ps04", "psychology", "The disposition effect: why we sell winners too early", "Documented bias: cut winners, hold losers; the fix."),
 ("ps05", "psychology", "Overtrading: more trades, less money", "Show cost and attention maths of too many trades."),
 ("ps06", "psychology", "How a famous operator lost everything: the Livermore lesson", "A well-documented story about ignoring his own rules (told carefully and factually)."),
 ("ps07", "psychology", "The March 2020 crash: what panic looked like on a real chart", "Documented market event; discipline vs panic."),
 ("ps08", "psychology", "The 2008 crisis in 3 charts: what it teaches about risk", "Documented event; position sizing and diversification."),
 ("ps09", "psychology", "Keeping a trading journal that actually helps", "What to record and how to review monthly."),
 ("ps10", "psychology", "Patience: the trades you do not take", "Waiting for your setup is a skill; show how often nothing is the right move."),
 # ── book_idea (10) ────────────────────────────────────────────────────────────
 ("bk01", "book_idea", "Trading in the Zone: 5 ideas on probabilistic thinking", "Each trade is one of many; think in samples (own words, credited)."),
 ("bk02", "book_idea", "The Intelligent Investor: margin of safety explained", "Margin of safety idea in own words with a worked example."),
 ("bk03", "book_idea", "Market Wizards: what the traders had in common", "Common themes in own words: risk control, humility, process."),
 ("bk04", "book_idea", "How to Make Money in Stocks: the ideas behind breakouts", "Growth-stock breakout ideas in own words, with our own test."),
 ("bk05", "book_idea", "A Random Walk Down Wall Street: when indexing beats picking", "Index vs active idea in own words."),
 ("bk06", "book_idea", "The Psychology of Money: 5 lessons on risk and time", "Own-words lessons about time and behaviour."),
 ("bk07", "book_idea", "Reminiscences of a Stock Operator: 5 timeless lessons", "Public-domain-era story lessons in own words."),
 ("bk08", "book_idea", "Fooled by Randomness: luck vs skill in your results", "Survivorship and luck ideas in own words."),
 ("bk09", "book_idea", "Thinking, Fast and Slow: the biases that cost traders money", "Bias ideas in own words applied to trading."),
 ("bk10", "book_idea", "The Little Book of Common Sense Investing: the cost argument", "Costs compound; own-words summary with a worked example."),
]

TOPICS = [dict(id=i, type=t, title=ti, angle=an) for (i, t, ti, an) in _T]
TYPE_ORDER = ["rule_chart", "research", "autopsy", "risk_math", "psychology", "book_idea"]
# long-run mix (weights) — monthly feedback may adjust these from real view data
TYPE_WEIGHTS = {"rule_chart": 0.30, "research": 0.20, "autopsy": 0.20, "risk_math": 0.15, "psychology": 0.10, "book_idea": 0.05}


def pick_topic(done_ids=(), today=None):
    """Deterministic, balanced pick: follow TYPE_WEIGHTS over a rolling 20-slot cycle and
    take the first not-yet-done topic of that type; when a type is exhausted, move on."""
    today = today or date.today()
    slots = []
    for ty, w in TYPE_WEIGHTS.items():
        slots += [ty] * max(1, round(w * 20))
    # interleave so same types are not back to back (round-robin over TYPE_ORDER below)
    order = []
    buckets = {ty: [s for s in slots if s == ty] for ty in TYPE_WEIGHTS}
    while any(buckets.values()):
        for ty in TYPE_ORDER:
            if buckets[ty]:
                order.append(buckets[ty].pop())
    want = order[(today.toordinal() // 7) % len(order)]
    done = set(done_ids)
    for ty in [want] + [t for t in TYPE_ORDER if t != want]:
        for t in TOPICS:
            if t["type"] == ty and t["id"] not in done:
                return t
    return TOPICS[0]


# ───────────────────────────── quality gate ─────────────────────────────────

BANNED = ("guaranteed", "sure shot", "sure-shot", "100% profit", "risk free", "risk-free",
          "buy now", "sell now", "double your money", "easy money", "cannot lose", "no risk")
LIMIT_MARKERS = ("does not prove", "doesn't prove", "not a guarantee", "no guarantee", "can fail", "limit",
                 "limitation", "not advice", "not investment advice", "past results", "survivorship",
                 "small sample", "may not")


def quality_gate(script_text: str, facts: dict, min_words=250, max_words=1100):
    """Return (ok, [reasons]). script_text = the full narration, facts = {name: number or str}
    that came from our own data (at least one must be quoted in the script)."""
    reasons = []
    low = script_text.lower()
    words = len(script_text.split())
    if words < min_words:
        reasons.append(f"too short ({words} words < {min_words})")
    if words > max_words:
        reasons.append(f"too long ({words} words > {max_words})")
    nums = set()
    for v in (facts or {}).values():
        s = str(v)
        for m in re.findall(r"\d[\d,\.]*", s):
            nums.add(m.strip(",."))
    if not nums or not any(n and n in script_text for n in nums):
        reasons.append("no real number from our data is quoted")
    if "rule:" not in low:
        reasons.append("no clear 'Rule:' line the viewer can apply")
    if not any(m in low for m in LIMIT_MARKERS):
        reasons.append("no honest limit (what this does NOT prove)")
    bad = [b for b in BANNED if b in low]
    if bad:
        reasons.append("hype/advice phrases: " + ", ".join(bad))
    if "lorem" in low or "[insert" in low or "todo" in low:
        reasons.append("placeholder text left in script")
    return (not reasons), reasons


if __name__ == "__main__":
    from collections import Counter
    print(len(TOPICS), "topics", dict(Counter(t["type"] for t in TOPICS)))
    print("pick:", pick_topic()["id"], pick_topic()["title"])
