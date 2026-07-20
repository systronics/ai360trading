---
layout: default
title: "Membership — AI360Trading"
permalink: /membership/
description: "AI360Trading Membership — Live Telegram signals, TradingView indicator, Chartink screener, private videos and live sessions. Advance ₹699/month. Premium ₹1,499/month."
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Mulish:wght@300;400;500;600;700&display=swap');
:root {
  --bg:#05080f; --surface:#0b0f1a; --card:#0f1520; --border:#1c2535;
  --gold:#fbbf24; --green:#10b981; --red:#ef4444; --blue:#3b82f6;
  --purple:#8b5cf6; --orange:#f97316; --text:#e2e8f0; --muted:#64748b;
  --shadow:0 8px 32px rgba(0,0,0,0.4);
}
*{box-sizing:border-box;margin:0;padding:0;}
.mp{background:var(--bg);font-family:'Mulish',sans-serif;color:var(--text);min-height:100vh;overflow-x:hidden;}

/* ── NAV ── */
.mp-nav{background:rgba(11,15,26,0.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:10px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:200;}
.mp-nav-home{display:flex;align-items:center;gap:6px;text-decoration:none;color:var(--text);font-size:0.82rem;font-weight:700;padding:6px 14px;border-radius:8px;background:var(--card);border:1px solid var(--border);transition:all 0.2s;}
.mp-nav-home:hover{border-color:var(--gold);color:var(--gold);}
.mp-nav-links{display:flex;gap:4px;}
.mp-nav-link{text-decoration:none;color:var(--muted);font-size:0.75rem;font-weight:700;padding:5px 10px;border-radius:6px;transition:all 0.2s;text-transform:uppercase;letter-spacing:0.04em;}
.mp-nav-link:hover{color:var(--text);background:var(--card);}
@media(max-width:480px){.mp-nav-links{display:none;}}

/* ── HERO ── */
.mp-hero{padding:28px 20px 22px;text-align:center;position:relative;overflow:hidden;}
.mp-hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 60% 40% at 50% 0%,rgba(251,191,36,0.07) 0%,transparent 70%);pointer-events:none;}
.mp-eyebrow{display:inline-flex;align-items:center;gap:8px;background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.2);color:var(--gold);font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:5px 12px;border-radius:100px;margin-bottom:12px;}
.live-dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:blink 1.4s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
/* FIXED: text size reduced from clamp(1.5rem,4vw,2.6rem) */
.mp-hero h1{font-family:'Syne',sans-serif;font-size:clamp(1.4rem,3vw,2.0rem);line-height:1.15;color:#fff;letter-spacing:-0.02em;margin-bottom:8px;}
.mp-hero h1 em{font-style:normal;color:var(--gold);}
.mp-hero p{font-size:0.82rem;color:var(--muted);max-width:480px;margin:0 auto 20px;line-height:1.6;}

/* Billing toggle */
.billing-toggle{display:inline-flex;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:3px;gap:3px;margin-bottom:24px;}
.billing-btn{padding:7px 16px;border-radius:8px;border:none;font-family:'Mulish',sans-serif;font-size:0.8rem;font-weight:700;cursor:pointer;transition:all 0.2s;color:var(--muted);background:transparent;}
.billing-btn.active{background:var(--gold);color:#000;}
.billing-save{font-size:0.62rem;background:var(--green);color:#fff;padding:2px 5px;border-radius:100px;margin-left:3px;}

/* ── LEDGER ── */
.ledger-section{max-width:900px;margin:0 auto 32px;padding:0 16px;}
.ledger-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px 22px;}
.ledger-title{font-family:'Syne',sans-serif;font-size:1rem;color:#fff;margin-bottom:4px;}
.ledger-sub{font-size:0.74rem;color:var(--muted);margin-bottom:14px;line-height:1.5;}
.ledger-stats{display:flex;flex-wrap:wrap;gap:10px 24px;margin-bottom:14px;}
.ledger-stat b{display:block;font-family:'Syne',sans-serif;font-size:1.15rem;color:#fff;}
.ledger-stat span{font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.06em;}
.ledger-table-wrap{overflow-x:auto;}
/* Explicit + nested under .ledger-card so these beat the site's global
   table/td/th rules (gpstyle.css, poole.css) — those bare-element and
   nth-child selectors were winning on specificity and washing out the
   text color, this was the 2026-07-21 low-contrast bug. */
.ledger-card table.ledger-table{width:100%;border-collapse:collapse;font-size:0.76rem;background:transparent;border:none;margin:0;}
.ledger-card table.ledger-table th{text-align:left;padding:6px 10px;color:var(--muted);font-weight:700;border:none;border-bottom:1px solid var(--border);font-size:0.68rem;text-transform:uppercase;background:transparent;}
.ledger-card table.ledger-table td{padding:6px 10px;border:none;border-bottom:1px solid rgba(255,255,255,0.06);background:transparent;color:var(--text);}
.ledger-card table.ledger-table tbody tr:nth-child(odd) td{background:transparent;}
.ledger-win{color:var(--green);font-weight:700;}
.ledger-loss{color:var(--red);font-weight:700;}
.ledger-foot{font-size:0.68rem;color:var(--muted);margin-top:12px;line-height:1.6;}
.ledger-foot a{color:var(--gold);}

/* ── PLANS ── */
.plans-section{max-width:900px;margin:0 auto;padding:0 16px 48px;}
.plans-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;}
@media(max-width:640px){.plans-grid{grid-template-columns:1fr;}}

.plan-card{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:28px 24px;position:relative;display:flex;flex-direction:column;overflow:hidden;transition:transform 0.25s,border-color 0.25s;}
.plan-card::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;border-radius:20px 20px 0 0;}
.plan-card.advance::before{background:linear-gradient(90deg,#3b82f6,#60a5fa);}
.plan-card.premium::before{background:linear-gradient(90deg,#fbbf24,#f59e0b);}
.plan-card.premium{border-color:rgba(251,191,36,0.3);}
.plan-card:hover{transform:translateY(-4px);border-color:rgba(251,191,36,0.5);}

.plan-badge{position:absolute;top:16px;right:16px;font-size:0.6rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;padding:3px 8px;border-radius:100px;}
.plan-card.premium .plan-badge{background:rgba(251,191,36,0.15);color:var(--gold);border:1px solid rgba(251,191,36,0.3);}
.plan-card.advance .plan-badge{background:rgba(59,130,246,0.15);color:#60a5fa;border:1px solid rgba(59,130,246,0.3);}

/* FIXED: plan name font size reduced */
.plan-name{font-family:'Syne',sans-serif;font-size:1.2rem;color:#fff;margin-bottom:4px;}
.plan-tagline{font-size:0.75rem;color:var(--muted);margin-bottom:16px;}
.plan-price{font-family:'Syne',sans-serif;font-size:2.0rem;color:#fff;font-weight:800;line-height:1;}
.plan-price span{font-size:0.8rem;color:var(--muted);font-weight:400;}
.plan-price-annual{font-size:0.72rem;color:var(--green);margin-top:4px;margin-bottom:20px;display:none;}
.plan-price-annual.show{display:block;}
.plan-strike{font-size:0.7rem;color:var(--muted);text-decoration:line-through;margin-right:4px;}

.plan-features{list-style:none;flex:1;margin-bottom:22px;}
.plan-features li{font-size:0.78rem;color:var(--text);padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;align-items:flex-start;gap:8px;line-height:1.45;}
.plan-features li:last-child{border-bottom:none;}
.feat-check{color:var(--green);font-size:0.85rem;flex-shrink:0;margin-top:1px;}
.feat-star{color:var(--gold);font-size:0.85rem;flex-shrink:0;margin-top:1px;}

.plan-cta{display:block;text-align:center;padding:12px 20px;border-radius:10px;font-size:0.82rem;font-weight:800;text-decoration:none;cursor:pointer;border:none;font-family:'Mulish',sans-serif;transition:all 0.2s;letter-spacing:0.02em;}
.plan-cta.advance-cta{background:rgba(59,130,246,0.15);color:#60a5fa;border:1px solid rgba(59,130,246,0.3);}
.plan-cta.advance-cta:hover{background:#3b82f6;color:#fff;}
.plan-cta.premium-cta{background:var(--gold);color:#000;}
.plan-cta.premium-cta:hover{background:#f59e0b;}

/* Section labels */
.feat-section{font-size:0.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;font-weight:700;padding:10px 0 4px;border-top:1px solid var(--border);margin-top:4px;}
.feat-section:first-child{border-top:none;padding-top:0;margin-top:0;}

/* ── COMPARISON TABLE ── */
.compare-section{max-width:860px;margin:0 auto 48px;padding:0 16px;}
.compare-title{font-size:0.75rem;color:var(--muted);text-align:center;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;font-weight:700;}
.compare-table{width:100%;border-collapse:collapse;font-size:0.76rem;background-color:transparent !important;}
.compare-table th{padding:10px 14px;text-align:left;color:#cbd5e1 !important;background-color:transparent !important;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;border-bottom:1px solid var(--border);}
.compare-table th:nth-child(2),.compare-table th:nth-child(3){text-align:center;}
.compare-table tr{background-color:transparent !important;}
.compare-table td{padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.08);color:#e2e8f0 !important;background-color:transparent !important;vertical-align:middle;}
.compare-table td:nth-child(2),.compare-table td:nth-child(3){text-align:center;}
.compare-table tr:last-child td{border-bottom:none;}
.ct-yes{color:var(--green);font-size:1rem;}
.ct-no{color:var(--muted);font-size:1rem;}
.ct-adv{color:#60a5fa;font-size:0.62rem;font-weight:700;text-transform:uppercase;}
.ct-prem{color:var(--gold);font-size:0.62rem;font-weight:700;text-transform:uppercase;}
.compare-table .section-row td{background-color:rgba(255,255,255,0.05) !important;color:#f1f5f9 !important;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;font-weight:700;padding:8px 14px;}

/* ── HOW IT WORKS ── */
.how-section{max-width:680px;margin:0 auto 48px;padding:0 16px;text-align:center;}
.how-title{font-size:0.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;font-weight:700;margin-bottom:20px;}
.steps-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}
@media(max-width:560px){.steps-grid{grid-template-columns:repeat(2,1fr);}}
.step{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 12px;text-align:center;}
.step-num{width:28px;height:28px;background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.3);color:var(--gold);border-radius:50%;font-size:0.75rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin:0 auto 10px;}
.step-label{font-size:0.72rem;font-weight:700;color:#fff;margin-bottom:4px;}
.step-desc{font-size:0.65rem;color:var(--muted);line-height:1.5;}

/* ── FAQ ── */
.faq-section{max-width:680px;margin:0 auto 48px;padding:0 16px;}
.faq-title{font-size:0.75rem;color:var(--muted);text-align:center;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;margin-bottom:16px;}
.faq-item{background:var(--card);border:1px solid var(--border);border-radius:10px;margin-bottom:8px;overflow:hidden;}
.faq-q{padding:14px 16px;font-size:0.8rem;font-weight:700;color:var(--text);cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:12px;}
.faq-q:hover{color:var(--gold);}
.faq-q::after{content:'+';color:var(--gold);font-size:1.1rem;flex-shrink:0;}
.faq-a{padding:0 16px 14px;font-size:0.76rem;color:var(--muted);line-height:1.6;}

/* ── PAYMENT MODAL ── */
.pay-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:500;align-items:center;justify-content:center;padding:16px;}
.pay-overlay.open{display:flex;}
.pay-modal{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:28px 24px;max-width:380px;width:100%;position:relative;}
.pay-close{position:absolute;top:14px;right:16px;background:none;border:none;color:var(--muted);font-size:1.2rem;cursor:pointer;padding:4px;}
.pay-close:hover{color:var(--text);}
.pay-plan-name{font-family:'Syne',sans-serif;font-size:1rem;color:#fff;margin-bottom:4px;}
.pay-amount{font-size:1.6rem;font-weight:800;color:var(--gold);margin-bottom:16px;}
.upi-box{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:14px;}
.upi-label{font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;}
.upi-id{font-size:0.95rem;font-weight:800;color:#fff;letter-spacing:0.02em;}
.upi-copy{display:inline-block;font-size:0.68rem;color:var(--gold);cursor:pointer;margin-top:4px;padding:3px 8px;border:1px solid rgba(251,191,36,0.3);border-radius:6px;}
.upi-copy:hover{background:rgba(251,191,36,0.1);}
.pay-steps{font-size:0.72rem;color:var(--muted);line-height:1.9;margin-bottom:16px;}
.pay-steps span{color:var(--text);}
.pay-wa{display:block;text-align:center;padding:12px;background:var(--green);color:#fff;font-size:0.82rem;font-weight:800;border-radius:10px;text-decoration:none;transition:opacity 0.2s;}
.pay-wa:hover{opacity:0.9;}
.pay-disclaimer{font-size:0.62rem;color:var(--muted);text-align:center;margin-top:10px;line-height:1.5;}

/* ── FOOTER NOTE ── */
.mp-footer{text-align:center;padding:20px 16px 40px;font-size:0.7rem;color:var(--muted);line-height:1.8;}
.mp-footer a{color:var(--muted);text-decoration:underline;}
</style>

<div class="mp">

<!-- NAV -->
<nav class="mp-nav">
  <a href="/" class="mp-nav-home">← AI360Trading</a>
  <div class="mp-nav-links">
    <a href="/tools/" class="mp-nav-link">Tools</a>
    <a href="/about/" class="mp-nav-link">About</a>
    <a href="/contact/" class="mp-nav-link">Contact</a>
  </div>
</nav>

<!-- HERO -->
<section class="mp-hero">
  <div class="mp-eyebrow"><span class="live-dot"></span> Live Membership</div>
  <h1>AI360 <em>Membership</em></h1>
  <p>Signals, TradingView indicator, Chartink screener, private videos and live sessions — everything in two simple plans.</p>
  <div class="billing-toggle">
    <button class="billing-btn active" onclick="setBilling('monthly',this)">Monthly</button>
    <button class="billing-btn" onclick="setBilling('annual',this)">Annual <span class="billing-save">Save 33%</span></button>
  </div>
</section>

{% if site.data.performance %}
{% assign perf = site.data.performance %}
<!-- LEDGER (2026-07-20: real, sourced live from the paper-trading History
     ledger by performance_stats.write_data_json — never hardcoded) -->
<section class="ledger-section">
  <div class="ledger-card">
    <div class="ledger-title">📊 Our Real Signal Performance — Verified Ledger</div>
    <div class="ledger-sub">Every closed trade from our automated system's live paper-trading ledger — wins <b>and</b> losses, as of {{ perf.as_of }}. Not a marketing number — this is what following every signal exactly would have produced.</div>
    <div class="ledger-stats">
      <div class="ledger-stat"><b>{{ perf.total }}</b><span>Closed trades</span></div>
      <div class="ledger-stat"><b>{{ perf.win_rate }}%</b><span>Win rate</span></div>
      <div class="ledger-stat"><b>{% if perf.net_pnl_rs >= 0 %}+{% endif %}₹{{ perf.net_pnl_rs }}</b><span>Net P/L</span></div>
      <div class="ledger-stat"><b class="ledger-win">+{{ perf.avg_win_pct }}%</b><span>Avg winner</span></div>
      <div class="ledger-stat"><b class="ledger-loss">{{ perf.avg_loss_pct }}%</b><span>Avg loser</span></div>
    </div>
    <div class="ledger-table-wrap">
    <table class="ledger-table">
      <thead><tr><th>Latest trades</th><th>Closed</th><th>Result</th></tr></thead>
      <tbody>
        {% for t in perf.recent %}
        <tr>
          <td><b>{{ t.sym }}</b></td>
          <td>{{ t.exit_date }}</td>
          <td class="{% if t.is_win %}ledger-win{% else %}ledger-loss{% endif %}">{% if t.pct >= 0 %}+{% endif %}{{ t.pct }}% {% if t.is_win %}✅{% else %}❌{% endif %}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    </div>
    <div class="ledger-foot">Published for transparency — losses included. Paper trading (no real money). See live setups on the <a href="/swing-dashboard/">signal dashboard</a>. Educational only — not SEBI-registered advice.</div>
  </div>
</section>
{% endif %}

<!-- PLANS -->
<section class="plans-section">
  <div class="plans-grid">

    <!-- ADVANCE -->
    <div class="plan-card advance">
      <div class="plan-badge">Advance</div>
      <div class="plan-name">Advance</div>
      <div class="plan-tagline">For active traders who want daily signals + tools</div>
      <div class="plan-price" id="adv-price">₹699 <span>/ month</span></div>
      <div class="plan-price-annual" id="adv-annual">
        <span class="plan-strike">₹8,388</span>₹5,588/year — save ₹2,800
      </div>
      <ul class="plan-features">
        <li class="feat-section">📱 Telegram Signals</li>
        <li><span class="feat-check">✓</span> Daily swing + positional trade alerts</li>
        <li><span class="feat-check">✓</span> Entry, stop loss, target levels for every trade</li>
        <li><span class="feat-check">✓</span> Market regime alerts (bullish/bearish)</li>
        <li><span class="feat-check">✓</span> Weekly performance report</li>
        <li class="feat-section">🛠️ Tools</li>
        <li><span class="feat-check">✓</span> Chartink screener access (Nifty200 filter)</li>
        <li><span class="feat-check">✓</span> TradingView Pine Script indicator (open source)</li>
        <li><span class="feat-check">✓</span> TradingView strategy script access</li>
        <li><span class="feat-check">✓</span> Setup guide PDF</li>
        <li class="feat-section">📺 Content</li>
        <li><span class="feat-check">✓</span> Private YouTube market analysis videos</li>
        <li><span class="feat-check">✓</span> Trade setup walkthroughs weekly</li>
      </ul>
      <button class="plan-cta advance-cta" onclick="openPay('Advance','699','5588')">Get Advance →</button>
    </div>

    <!-- PREMIUM -->
    <div class="plan-card premium">
      <div class="plan-badge">⭐ Best Value</div>
      <div class="plan-name">Premium</div>
      <div class="plan-tagline">For serious traders who want everything + live sessions</div>
      <div class="plan-price" id="prem-price">₹1,499 <span>/ month</span></div>
      <div class="plan-price-annual" id="prem-annual">
        <span class="plan-strike">₹17,988</span>₹11,988/year — save ₹6,000
      </div>
      <ul class="plan-features">
        <li class="feat-section">📱 Telegram Signals</li>
        <li><span class="feat-star">★</span> Everything in Advance</li>
        <li><span class="feat-star">★</span> Options CE/PE candidate alerts</li>
        <li><span class="feat-star">★</span> Intraday momentum alerts (10:30 AM)</li>
        <li class="feat-section">🛠️ Tools</li>
        <li><span class="feat-star">★</span> All Advance tools included</li>
        <li><span class="feat-star">★</span> Chartink screener + email alerts setup</li>
        <li><span class="feat-star">★</span> Full Nifty200 watchlist with scores (Google Sheet access)</li>
        <li class="feat-section">🎥 Live Sessions</li>
        <li><span class="feat-star">★</span> 2× live trading sessions per month</li>
        <li><span class="feat-star">★</span> Live Q&A with Amit Kumar</li>
        <li><span class="feat-star">★</span> Session recordings available</li>
        <li class="feat-section">💎 Premium Only</li>
        <li><span class="feat-star">★</span> Priority WhatsApp support</li>
        <li><span class="feat-star">★</span> Monthly 1:1 portfolio review (15 min)</li>
        <li><span class="feat-star">★</span> Early access to new indicators</li>
      </ul>
      <button class="plan-cta premium-cta" onclick="openPay('Premium','1499','11988')">Get Premium →</button>
    </div>

  </div>
</section>

<!-- COMPARISON TABLE -->
<section class="compare-section">
  <div class="compare-title">Full Feature Comparison</div>
  <table class="compare-table">
    <thead>
      <tr>
        <th>Feature</th>
        <th><span class="ct-adv">Advance</span></th>
        <th><span class="ct-prem">Premium</span></th>
      </tr>
    </thead>
    <tbody>
      <tr class="section-row"><td colspan="3">📱 Telegram Signals</td></tr>
      <tr><td>Daily swing + positional alerts</td><td><span class="ct-yes">✓</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Options CE/PE alerts</td><td><span class="ct-no">—</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Intraday momentum alerts</td><td><span class="ct-no">—</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Weekly performance report</td><td><span class="ct-yes">✓</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr class="section-row"><td colspan="3">🛠️ Tools &amp; Screeners</td></tr>
      <tr><td>TradingView Pine Script indicator</td><td><span class="ct-yes">✓</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>TradingView strategy script</td><td><span class="ct-yes">✓</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Chartink screener link</td><td><span class="ct-yes">✓</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Chartink email alerts setup</td><td><span class="ct-no">—</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Nifty200 Google Sheet (live scores)</td><td><span class="ct-no">—</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr class="section-row"><td colspan="3">📺 Videos &amp; Learning</td></tr>
      <tr><td>Private YouTube videos</td><td><span class="ct-yes">✓</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Trade setup walkthroughs</td><td><span class="ct-yes">✓</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Live trading sessions (2×/month)</td><td><span class="ct-no">—</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Session recordings</td><td><span class="ct-no">—</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr class="section-row"><td colspan="3">💎 Support</td></tr>
      <tr><td>Priority WhatsApp support</td><td><span class="ct-no">—</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr><td>Monthly 1:1 portfolio review</td><td><span class="ct-no">—</span></td><td><span class="ct-yes">✓</span></td></tr>
      <tr class="section-row"><td colspan="3">💰 Pricing</td></tr>
      <tr><td>Monthly</td><td>₹699</td><td>₹1,499</td></tr>
      <tr><td>Annual (save 33%)</td><td>₹5,588/yr</td><td>₹11,988/yr</td></tr>
    </tbody>
  </table>
</section>

<!-- HOW IT WORKS -->
<section class="how-section">
  <div class="how-title">How It Works</div>
  <div class="steps-grid">
    <div class="step"><div class="step-num">1</div><div class="step-label">Choose Plan</div><div class="step-desc">Pick Advance or Premium — monthly or annual</div></div>
    <div class="step"><div class="step-num">2</div><div class="step-label">Pay via UPI</div><div class="step-desc">Copy UPI ID, pay from GPay / PhonePe / Paytm</div></div>
    <div class="step"><div class="step-num">3</div><div class="step-label">Send Screenshot</div><div class="step-desc">WhatsApp payment screenshot + Telegram username</div></div>
    <div class="step"><div class="step-num">4</div><div class="step-label">Get Access</div><div class="step-desc">All invite links sent within 1 hour (9AM–6PM IST)</div></div>
  </div>
</section>

<!-- FAQ -->
<section class="faq-section">
  <div class="faq-title">Frequently Asked Questions</div>

  <div class="faq-item">
    <div class="faq-q">Is this SEBI registered investment advice?</div>
    <div class="faq-a">No. AI360Trading is not a SEBI registered investment advisor. All signals and analysis are for educational purposes only. Trading involves risk of loss. Always do your own research.</div>
  </div>

  <div class="faq-item">
    <div class="faq-q">What is the TradingView indicator exactly?</div>
    <div class="faq-a">It is an open-source Pine Script indicator — the same priority scoring formula that powers all AI360 signals. You get the script link to add to your own TradingView account (free account works). A full PDF setup guide is included.</div>
  </div>

  <div class="faq-item">
    <div class="faq-q">What is the Chartink screener?</div>
    <div class="faq-a">A pre-built Chartink screener that filters Nifty200 stocks by breakout stage, volume, FII zone and SMA structure. Premium members also get help setting up Chartink email alerts so you never miss a signal.</div>
  </div>

  <div class="faq-item">
    <div class="faq-q">What is the Nifty200 Google Sheet in Premium?</div>
    <div class="faq-a">View-only access to the live Nifty200 spreadsheet — the same sheet that the AI trading bot uses. Shows real-time CMP, priority scores, sector rank, ATR, FII signal and breakout stage for all 200+ stocks.</div>
  </div>

  <div class="faq-item">
    <div class="faq-q">How do I get access after payment?</div>
    <div class="faq-a">After paying via UPI, click the WhatsApp button and send your payment screenshot with your Telegram username. You will receive all invite links and tool access within 1 hour during market hours (9AM–6PM IST).</div>
  </div>

  <div class="faq-item">
    <div class="faq-q">Can I cancel anytime?</div>
    <div class="faq-a">Monthly plans are not auto-renewed. Simply do not renew after your month ends and access stops automatically. No cancellation process needed.</div>
  </div>

  <div class="faq-item">
    <div class="faq-q">Can I upgrade from Advance to Premium?</div>
    <div class="faq-a">Yes — pay the difference and WhatsApp the screenshot. Upgrade is processed within 1 hour during market hours.</div>
  </div>
</section>

<!-- PAYMENT MODAL -->
<div class="pay-overlay" id="payOverlay">
  <div class="pay-modal">
    <button class="pay-close" onclick="closePay()">✕</button>
    <div class="pay-plan-name" id="modalPlanName">Advance Membership</div>
    <div class="pay-amount" id="modalAmount">₹699/month</div>
    <div class="upi-box">
      <div class="upi-label">Pay via UPI</div>
      <div class="upi-id">9634759528@upi</div>
      <div class="upi-copy" onclick="copyUPI()">📋 Copy UPI ID</div>
    </div>
    <div class="pay-steps">
      <span>1.</span> Copy UPI ID above and open GPay / PhonePe / Paytm<br>
      <span>2.</span> Send exact amount: <strong id="modalAmtInline">₹699</strong><br>
      <span>3.</span> Take screenshot of payment confirmation<br>
      <span>4.</span> Click WhatsApp below — send screenshot + Telegram username
    </div>
    <a href="#" class="pay-wa" id="waLink" target="_blank">📲 Confirm via WhatsApp</a>
    <div class="pay-disclaimer">Access granted within 1 hour. Educational content only — not SEBI advice.</div>
  </div>
</div>

<!-- FOOTER NOTE -->
<div class="mp-footer">
  <strong style="color:var(--text)">AI360Trading</strong><br>
  Educational content only. Not SEBI registered. Trading involves risk of loss.<br>
  <a href="/disclaimer/">Disclaimer</a> · <a href="/policy/">Privacy Policy</a> · <a href="/contact/">Contact</a><br>
  Haridwar, Uttarakhand, India · admin@ai360trading.in
</div>

</div><!-- end .mp -->

<script>
// Billing toggle
function setBilling(type, btn) {
  document.querySelectorAll('.billing-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const isAnnual = type === 'annual';
  document.getElementById('adv-price').innerHTML  = isAnnual ? '₹465 <span>/ month</span>' : '₹699 <span>/ month</span>';
  document.getElementById('prem-price').innerHTML = isAnnual ? '₹999 <span>/ month</span>' : '₹1,499 <span>/ month</span>';
  document.getElementById('adv-annual').classList.toggle('show', isAnnual);
  document.getElementById('prem-annual').classList.toggle('show', isAnnual);
}

// Payment modal
function openPay(plan, monthly, annual) {
  const isAnnual = document.querySelector('.billing-btn.active').textContent.includes('Annual');
  const amt      = isAnnual ? annual : monthly;
  const period   = isAnnual ? '/year' : '/month';
  document.getElementById('modalPlanName').textContent  = plan + ' Membership';
  document.getElementById('modalAmount').textContent    = '₹' + amt + period;
  document.getElementById('modalAmtInline').textContent = '₹' + amt;
  const msg  = encodeURIComponent(`Hi Amit, I've paid ₹${amt} for AI360Trading ${plan} membership. Please activate my access. My Telegram username is: @`);
  document.getElementById('waLink').href = `https://wa.me/919634759528?text=${msg}`;
  document.getElementById('payOverlay').classList.add('open');
}

function closePay() {
  document.getElementById('payOverlay').classList.remove('open');
}

document.getElementById('payOverlay').addEventListener('click', function(e) {
  if (e.target === this) closePay();
});

function copyUPI() {
  navigator.clipboard.writeText('9634759528@upi').then(() => {
    const el = document.querySelector('.upi-copy');
    el.textContent = '✅ Copied!';
    setTimeout(() => el.textContent = '📋 Copy UPI ID', 2000);
  }).catch(() => {
    alert('UPI: 9634759528@upi');
  });
}
</script>
