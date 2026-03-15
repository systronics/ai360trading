---
layout: default
title: "Membership — AI360Trading"
permalink: /membership/
description: "Join AI360Trading Membership — Telegram signals, YouTube private videos, live sessions and TradingView scanner. All trading services in one place."
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Mulish:wght@300;400;500;600;700&display=swap');

:root {
  --bg:       #05080f;
  --surface:  #0b0f1a;
  --card:     #0f1520;
  --border:   #1c2535;
  --gold:     #fbbf24;
  --green:    #10b981;
  --red:      #ef4444;
  --blue:     #3b82f6;
  --purple:   #8b5cf6;
  --orange:   #f97316;
  --text:     #e2e8f0;
  --muted:    #64748b;
  --shadow:   0 8px 32px rgba(0,0,0,0.4);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
.mp { background: var(--bg); font-family: 'Mulish', sans-serif; color: var(--text); min-height: 100vh; overflow-x: hidden; }

/* ── NAV ── */
.mp-nav { background: rgba(11,15,26,0.95); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); padding: 10px 24px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 200; }
.mp-nav-home { display: flex; align-items: center; gap: 6px; text-decoration: none; color: var(--text); font-size: 0.82rem; font-weight: 700; padding: 6px 14px; border-radius: 8px; background: var(--card); border: 1px solid var(--border); transition: all 0.2s; }
.mp-nav-home:hover { border-color: var(--gold); color: var(--gold); }
.mp-nav-links { display: flex; gap: 4px; }
.mp-nav-link { text-decoration: none; color: var(--muted); font-size: 0.75rem; font-weight: 700; padding: 5px 10px; border-radius: 6px; transition: all 0.2s; text-transform: uppercase; letter-spacing: 0.04em; }
.mp-nav-link:hover { color: var(--text); background: var(--card); }
@media(max-width:480px) { .mp-nav-links { display: none; } }

/* ── HERO ── */
.mp-hero { padding: 64px 24px 48px; text-align: center; position: relative; overflow: hidden; }
.mp-hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 60% 40% at 50% 0%, rgba(251,191,36,0.07) 0%, transparent 70%); pointer-events: none; }
.mp-hero::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); }

.mp-eyebrow { display: inline-flex; align-items: center; gap: 8px; background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.2); color: var(--gold); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; padding: 7px 16px; border-radius: 100px; margin-bottom: 24px; }
.live-dot { width: 7px; height: 7px; background: var(--green); border-radius: 50%; animation: blink 1.4s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.mp-hero h1 { font-family: 'Syne', sans-serif; font-size: clamp(2.4rem, 7vw, 5rem); line-height: 1; color: #fff; letter-spacing: -0.02em; margin-bottom: 16px; }
.mp-hero h1 em { font-style: normal; color: var(--gold); }
.mp-hero p { font-size: clamp(0.9rem, 2vw, 1.05rem); color: var(--muted); max-width: 500px; margin: 0 auto 32px; line-height: 1.7; }

/* Billing toggle */
.billing-toggle { display: inline-flex; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 4px; gap: 4px; margin-bottom: 48px; }
.billing-btn { padding: 8px 20px; border-radius: 9px; border: none; font-family: 'Mulish', sans-serif; font-size: 0.85rem; font-weight: 700; cursor: pointer; transition: all 0.2s; color: var(--muted); background: transparent; }
.billing-btn.active { background: var(--gold); color: #000; }
.billing-save { font-size: 0.65rem; background: var(--green); color: #fff; padding: 2px 6px; border-radius: 100px; margin-left: 4px; }

/* ── SERVICE CARDS ── */
.services-section { max-width: 1100px; margin: 0 auto; padding: 0 20px 60px; }
.services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }

.svc-card { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 28px 24px; position: relative; transition: transform 0.25s, border-color 0.25s; display: flex; flex-direction: column; overflow: hidden; }
.svc-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 20px 20px 0 0; }
.svc-card.tg::before   { background: linear-gradient(90deg, #0088cc, #229ed9); }
.svc-card.yt::before   { background: linear-gradient(90deg, #ff0000, #ff6b6b); }
.svc-card.live::before { background: linear-gradient(90deg, #ef4444, #f97316); }
.svc-card.tv::before   { background: linear-gradient(90deg, #2962ff, #1565c0); }
.svc-card:hover { transform: translateY(-4px); border-color: var(--gold); }

.svc-icon { font-size: 2.2rem; margin-bottom: 14px; }
.svc-platform { font-size: 0.68rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.svc-card.tg   .svc-platform { color: #229ed9; }
.svc-card.yt   .svc-platform { color: #ff6b6b; }
.svc-card.live .svc-platform { color: var(--orange); }
.svc-card.tv   .svc-platform { color: #5c9eff; }

.svc-name { font-family: 'Syne', sans-serif; font-size: 1.2rem; color: #fff; margin-bottom: 8px; }
.svc-desc { font-size: 0.8rem; color: var(--muted); line-height: 1.6; flex: 1; margin-bottom: 16px; }

.svc-features { list-style: none; margin-bottom: 20px; display: flex; flex-direction: column; gap: 6px; }
.svc-features li { display: flex; align-items: flex-start; gap: 7px; font-size: 0.78rem; color: var(--text); line-height: 1.4; }
.svc-features li::before { content: '✓'; color: var(--green); font-weight: 800; flex-shrink: 0; }

.svc-price { margin-bottom: 16px; }
.svc-amount { font-family: 'Syne', sans-serif; font-size: 2rem; color: var(--gold); line-height: 1; }
.svc-period { font-size: 0.75rem; color: var(--muted); margin-top: 2px; }
.svc-annual  { font-size: 0.72rem; color: var(--green); margin-top: 3px; }

.btn-svc { width: 100%; padding: 12px; border-radius: 10px; border: 1.5px solid var(--border); background: transparent; color: var(--gold); font-family: 'Mulish', sans-serif; font-size: 0.85rem; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-svc:hover { background: var(--gold); color: #000; border-color: var(--gold); }

/* ── COMBO CARD ── */
.combo-wrap { background: linear-gradient(135deg, #0f1520, #141c2e); border: 1px solid rgba(251,191,36,0.4); border-radius: 24px; padding: 36px 32px; position: relative; overflow: hidden; margin-bottom: 40px; }
.combo-wrap::before { content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(251,191,36,0.05) 0%, transparent 70%); pointer-events: none; }
.combo-badge { display: inline-flex; align-items: center; gap: 6px; background: var(--gold); color: #000; font-size: 0.72rem; font-weight: 800; padding: 5px 14px; border-radius: 100px; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 20px; }
.combo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; align-items: center; }
@media(max-width:640px) { .combo-grid { grid-template-columns: 1fr; } }

.combo-left h2 { font-family: 'Syne', sans-serif; font-size: clamp(1.6rem, 4vw, 2.4rem); color: #fff; line-height: 1.1; margin-bottom: 12px; }
.combo-left h2 span { color: var(--gold); }
.combo-left p { font-size: 0.85rem; color: var(--muted); line-height: 1.6; margin-bottom: 20px; }
.combo-includes { display: flex; flex-wrap: wrap; gap: 8px; }
.combo-tag { display: flex; align-items: center; gap: 5px; background: rgba(255,255,255,0.05); border: 1px solid var(--border); border-radius: 8px; padding: 5px 10px; font-size: 0.75rem; color: var(--text); font-weight: 600; }

.combo-right { text-align: center; }
.combo-price-box { background: var(--bg); border-radius: 16px; padding: 24px; border: 1px solid var(--border); margin-bottom: 16px; }
.combo-original { font-size: 0.82rem; color: var(--muted); text-decoration: line-through; margin-bottom: 4px; }
.combo-amount { font-family: 'Syne', sans-serif; font-size: 3.5rem; color: var(--gold); line-height: 1; }
.combo-period { font-size: 0.82rem; color: var(--muted); margin-top: 4px; }
.combo-saving { display: inline-block; background: rgba(16,185,129,0.15); color: var(--green); border: 1px solid rgba(16,185,129,0.3); font-size: 0.75rem; font-weight: 700; padding: 4px 12px; border-radius: 100px; margin-top: 8px; }
.btn-combo { width: 100%; background: var(--gold); color: #000; border: none; border-radius: 12px; padding: 16px; font-family: 'Mulish', sans-serif; font-size: 1rem; font-weight: 800; cursor: pointer; transition: all 0.2s; letter-spacing: 0.01em; }
.btn-combo:hover { background: #fcd34d; transform: scale(1.02); }

/* ── HOW IT WORKS ── */
.how-section { max-width: 860px; margin: 0 auto 60px; padding: 0 20px; }
.section-label { font-family: 'Syne', sans-serif; font-size: clamp(1.4rem, 4vw, 2rem); color: #fff; text-align: center; margin-bottom: 8px; }
.section-sub { text-align: center; color: var(--muted); font-size: 0.85rem; margin-bottom: 32px; }
.steps-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
@media(max-width:600px) { .steps-row { grid-template-columns: 1fr 1fr; } }
.step-box { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px 16px; text-align: center; }
.step-n { font-family: 'Syne', sans-serif; font-size: 2.5rem; color: var(--gold); opacity: 0.25; line-height: 1; }
.step-t { font-size: 0.85rem; font-weight: 700; color: #fff; margin: 6px 0 4px; }
.step-d { font-size: 0.75rem; color: var(--muted); line-height: 1.5; }

/* ── FAQ ── */
.faq-section { max-width: 680px; margin: 0 auto 60px; padding: 0 20px; }
.faq-item { border-bottom: 1px solid var(--border); }
.faq-q { width: 100%; background: none; border: none; color: var(--text); font-family: 'Mulish', sans-serif; font-size: 0.88rem; font-weight: 700; padding: 16px 0; text-align: left; cursor: pointer; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.faq-q:hover { color: var(--gold); }
.faq-icon { color: var(--gold); font-size: 1.1rem; flex-shrink: 0; transition: transform 0.2s; }
.faq-a { display: none; font-size: 0.82rem; color: var(--muted); line-height: 1.7; padding-bottom: 14px; }
.faq-item.open .faq-a { display: block; }
.faq-item.open .faq-icon { transform: rotate(45deg); }

/* ── MODAL ── */
.modal-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.88); z-index: 1000; align-items: center; justify-content: center; padding: 16px; backdrop-filter: blur(8px); }
.modal-overlay.open { display: flex; }
.modal { background: var(--card); border: 1px solid var(--border); border-radius: 20px; max-width: 440px; width: 100%; max-height: 92vh; overflow-y: auto; animation: up 0.28s ease; }
@keyframes up { from{transform:translateY(20px);opacity:0} to{transform:translateY(0);opacity:1} }
.modal-head { padding: 22px 22px 0; display: flex; justify-content: space-between; align-items: flex-start; }
.modal-svc-name { font-family: 'Syne', sans-serif; font-size: 1.2rem; color: var(--gold); }
.modal-svc-price { font-size: 0.78rem; color: var(--muted); margin-top: 2px; }
.modal-x { background: var(--surface); border: 1px solid var(--border); border-radius: 50%; width: 28px; height: 28px; color: var(--muted); cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.modal-body { padding: 16px 22px 22px; }

.form-group { margin-bottom: 12px; }
.form-label { display: block; font-size: 0.72rem; font-weight: 700; color: var(--muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.form-input { width: 100%; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; font-family: 'Mulish', sans-serif; font-size: 0.88rem; color: var(--text); outline: none; transition: border-color 0.2s; }
.form-input:focus { border-color: var(--gold); }

.pay-box { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 16px; margin: 14px 0; }
.pay-amount-row { display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; margin-bottom: 12px; border-bottom: 1px solid var(--border); }
.pay-label { font-size: 0.75rem; color: var(--muted); }
.pay-amount { font-family: 'Syne', sans-serif; font-size: 1.6rem; color: var(--gold); }
.upi-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.upi-val { font-size: 0.92rem; font-weight: 700; color: var(--text); }
.btn-copy { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 6px 12px; font-size: 0.75rem; font-weight: 700; color: var(--gold); cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-copy:hover { background: var(--gold); color: #000; border-color: var(--gold); }
.pay-steps { margin-top: 12px; display: flex; flex-direction: column; gap: 6px; }
.pay-step { display: flex; align-items: center; gap: 8px; font-size: 0.75rem; color: var(--muted); }
.pay-step-n { background: var(--card); border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 0.62rem; font-weight: 800; color: var(--gold); flex-shrink: 0; }

.btn-wa { width: 100%; background: #25d366; color: #fff; border: none; border-radius: 12px; padding: 14px; font-family: 'Mulish', sans-serif; font-size: 0.95rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 4px; transition: background 0.2s; text-decoration: none; }
.btn-wa:hover { background: #1ebe5d; }
.btn-email { width: 100%; background: transparent; color: var(--text); border: 1px solid var(--border); border-radius: 12px; padding: 12px; font-family: 'Mulish', sans-serif; font-size: 0.85rem; font-weight: 700; cursor: pointer; margin-top: 8px; transition: all 0.2s; }
.btn-email:hover { border-color: var(--gold); color: var(--gold); }

/* ── TOAST ── */
.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(80px); background: var(--gold); color: #000; padding: 10px 22px; border-radius: 100px; font-size: 0.82rem; font-weight: 800; z-index: 9999; transition: transform 0.3s; white-space: nowrap; }
.toast.show { transform: translateX(-50%) translateY(0); }
</style>

<div class="mp">

  <!-- NAV -->
  <div class="mp-nav">
    <a href="/" class="mp-nav-home">← Home</a>
    <div class="mp-nav-links">
      <a href="/shop/" class="mp-nav-link">Shop</a>
      <a href="/about/" class="mp-nav-link">About</a>
      <a href="/contact/" class="mp-nav-link">Contact</a>
    </div>
  </div>

  <!-- HERO -->
  <div class="mp-hero">
    <div class="mp-eyebrow"><span class="live-dot"></span> All Services Live</div>
    <h1>AI360<br><em>Membership</em></h1>
    <p>One place for all AI360Trading services — signals, videos, live sessions and scanner access. Pick what you need or get everything at once.</p>

    <div class="billing-toggle">
      <button class="billing-btn active" id="btnM" onclick="setBilling('monthly')">Monthly</button>
      <button class="billing-btn" id="btnA" onclick="setBilling('annual')">Annual <span class="billing-save">Save 33%</span></button>
    </div>
  </div>

  <!-- SERVICES -->
  <div class="services-section">

    <div class="services-grid">

      <!-- TELEGRAM -->
      <div class="svc-card tg">
        <div class="svc-icon">📱</div>
        <div class="svc-platform">Telegram</div>
        <div class="svc-name">Signal Channel</div>
        <div class="svc-desc">Private Telegram channel with live trading signals — swing, positional and options alerts as they happen.</div>
        <ul class="svc-features">
          <li>Swing trade signals daily</li>
          <li>Positional calls weekly</li>
          <li>Options alerts when triggered</li>
          <li>Entry, target, stop loss levels</li>
          <li>Market regime alerts</li>
          <li>Weekly performance report</li>
        </ul>
        <div class="svc-price">
          <div class="svc-amount" id="tg-price">₹499</div>
          <div class="svc-period" id="tg-period">per month</div>
          <div class="svc-annual" id="tg-annual">or ₹3,999/year</div>
        </div>
        <button class="btn-svc" onclick="openModal('Telegram Signal Channel', 499, 3999, 'tg')">Subscribe Now</button>
      </div>

      <!-- YOUTUBE PRIVATE -->
      <div class="svc-card yt">
        <div class="svc-icon">📺</div>
        <div class="svc-platform">YouTube</div>
        <div class="svc-name">Private Videos</div>
        <div class="svc-desc">Access to private YouTube videos — market analysis, trade walkthroughs, tutorials and strategy breakdowns.</div>
        <ul class="svc-features">
          <li>Private analysis videos</li>
          <li>Trade setup walkthroughs</li>
          <li>Strategy tutorials</li>
          <li>Chart reading lessons</li>
          <li>Post-trade reviews</li>
          <li>New videos every week</li>
        </ul>
        <div class="svc-price">
          <div class="svc-amount" id="yt-price">₹299</div>
          <div class="svc-period" id="yt-period">per month</div>
          <div class="svc-annual" id="yt-annual">or ₹2,499/year</div>
        </div>
        <button class="btn-svc" onclick="openModal('YouTube Private Videos', 299, 2499, 'yt')">Subscribe Now</button>
      </div>

      <!-- YOUTUBE LIVE -->
      <div class="svc-card live">
        <div class="svc-icon">🔴</div>
        <div class="svc-platform">YouTube Live</div>
        <div class="svc-name">Live Sessions</div>
        <div class="svc-desc">Private live trading sessions — watch Amit trade in real time, ask questions, learn the decision-making process live.</div>
        <ul class="svc-features">
          <li>Live trading sessions</li>
          <li>Real-time market commentary</li>
          <li>Live Q&amp;A with Amit</li>
          <li>Pre-market live analysis</li>
          <li>Recorded replays available</li>
          <li>Priority access to sessions</li>
        </ul>
        <div class="svc-price">
          <div class="svc-amount" id="live-price">₹699</div>
          <div class="svc-period" id="live-period">per month</div>
          <div class="svc-annual" id="live-annual">or ₹5,999/year</div>
        </div>
        <button class="btn-svc" onclick="openModal('YouTube Live Sessions', 699, 5999, 'live')">Subscribe Now</button>
      </div>

      <!-- TRADINGVIEW -->
      <div class="svc-card tv">
        <div class="svc-icon">📊</div>
        <div class="svc-platform">TradingView</div>
        <div class="svc-name">Scanner Access</div>
        <div class="svc-desc">Access to the AI360 Nifty200 TradingView scanner — the same tool that powers all trade signals. Full setup guide included.</div>
        <ul class="svc-features">
          <li>Nifty200 scanner access</li>
          <li>Priority score formula</li>
          <li>Sector trend filter</li>
          <li>RS vs Nifty indicator</li>
          <li>Full setup guide PDF</li>
          <li>Lifetime updates</li>
        </ul>
        <div class="svc-price">
          <div class="svc-amount" id="tv-price">₹399</div>
          <div class="svc-period" id="tv-period">per month</div>
          <div class="svc-annual" id="tv-annual">or ₹2,999/year</div>
        </div>
        <button class="btn-svc" onclick="openModal('TradingView Scanner Access', 399, 2999, 'tv')">Subscribe Now</button>
      </div>

    </div>

    <!-- ALL-IN-ONE COMBO -->
    <div class="combo-wrap">
      <div class="combo-badge">👑 Best Value — All-in-One</div>
      <div class="combo-grid">
        <div class="combo-left">
          <h2>Everything in<br><span>One Membership</span></h2>
          <p>Get all 4 services together at one price. Save 47% vs buying individually. Everything Amit uses — signals, videos, live sessions and scanner.</p>
          <div class="combo-includes">
            <div class="combo-tag">📱 Telegram</div>
            <div class="combo-tag">📺 YouTube Private</div>
            <div class="combo-tag">🔴 YouTube Live</div>
            <div class="combo-tag">📊 TradingView Scanner</div>
          </div>
        </div>
        <div class="combo-right">
          <div class="combo-price-box">
            <div class="combo-original" id="combo-original">Individual total: ₹1,896/mo</div>
            <div class="combo-amount" id="combo-price">₹999</div>
            <div class="combo-period" id="combo-period">per month</div>
            <div class="combo-saving" id="combo-saving">You save ₹897/month — 47% off</div>
          </div>
          <button class="btn-combo" onclick="openModal('All-in-One Membership', 999, 7999, 'combo')">
            Join All-in-One Now →
          </button>
          <div style="font-size:0.72rem;color:var(--muted);margin-top:10px">Access within 1 hour of payment confirmation</div>
        </div>
      </div>
    </div>

  </div>

  <!-- HOW IT WORKS -->
  <div class="how-section">
    <div class="section-label">How It Works</div>
    <p class="section-sub">Simple 4-step process — takes less than 5 minutes</p>
    <div class="steps-row">
      <div class="step-box"><div class="step-n">01</div><div class="step-t">Choose Service</div><div class="step-d">Pick the plan that fits your trading style and budget</div></div>
      <div class="step-box"><div class="step-n">02</div><div class="step-t">Pay via UPI</div><div class="step-d">Copy UPI ID and pay from any UPI app in 30 seconds</div></div>
      <div class="step-box"><div class="step-n">03</div><div class="step-t">Send Screenshot</div><div class="step-d">Click WhatsApp button and send payment screenshot</div></div>
      <div class="step-box"><div class="step-n">04</div><div class="step-t">Get Access</div><div class="step-d">Receive invite links within 1 hour during market hours</div></div>
    </div>
  </div>

  <!-- FAQ -->
  <div class="faq-section">
    <div class="section-label" style="margin-bottom:24px">FAQ</div>
    <div class="faq-item">
      <button class="faq-q" onclick="toggleFaq(this)">Is this SEBI registered investment advice? <span class="faq-icon">+</span></button>
      <div class="faq-a">No. All content is for educational purposes only. AI360Trading is not a SEBI registered investment advisor. Past performance does not guarantee future results. Trade at your own risk.</div>
    </div>
    <div class="faq-item">
      <button class="faq-q" onclick="toggleFaq(this)">How do I get access after payment? <span class="faq-icon">+</span></button>
      <div class="faq-a">After paying via UPI, click the WhatsApp button and send your payment screenshot along with your Telegram username and YouTube email. You will receive all invite links within 1 hour during market hours (9AM–6PM IST).</div>
    </div>
    <div class="faq-item">
      <button class="faq-q" onclick="toggleFaq(this)">Can I subscribe to only one service? <span class="faq-icon">+</span></button>
      <div class="faq-a">Yes — each service can be subscribed individually. You are not required to take the combo. Start with what interests you most and upgrade anytime.</div>
    </div>
    <div class="faq-item">
      <button class="faq-q" onclick="toggleFaq(this)">How does the annual plan work? <span class="faq-icon">+</span></button>
      <div class="faq-a">Annual plans are paid once upfront and give you 12 months of access. You save 33% compared to paying monthly. Access does not auto-renew — you will be reminded before expiry.</div>
    </div>
    <div class="faq-item">
      <button class="faq-q" onclick="toggleFaq(this)">What is the TradingView scanner exactly? <span class="faq-icon">+</span></button>
      <div class="faq-a">It is the same Nifty200 screening tool that powers all AI360 signals — priority score, sector trend, RS vs Nifty and more. You get access to the Pine Script indicator plus a complete PDF setup guide to use it on your own TradingView account.</div>
    </div>
    <div class="faq-item">
      <button class="faq-q" onclick="toggleFaq(this)">Can I cancel anytime? <span class="faq-icon">+</span></button>
      <div class="faq-a">Monthly plans are not auto-renewed. Simply do not renew after your month ends and access will stop automatically. No cancellation needed.</div>
    </div>
  </div>

</div>

<!-- MODAL -->
<div class="modal-overlay" id="modal">
  <div class="modal">
    <div class="modal-head">
      <div>
        <div class="modal-svc-name" id="m-name">Service</div>
        <div class="modal-svc-price" id="m-price-label">₹499/month</div>
      </div>
      <button class="modal-x" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label class="form-label">Your Name *</label>
        <input class="form-input" id="m-name-in" placeholder="Full name">
      </div>
      <div class="form-group">
        <label class="form-label">WhatsApp Number *</label>
        <input class="form-input" id="m-phone" placeholder="+91 XXXXXXXXXX" type="tel">
      </div>
      <div class="form-group">
        <label class="form-label">Telegram Username *</label>
        <input class="form-input" id="m-tg" placeholder="@yourusername">
      </div>
      <div class="form-group">
        <label class="form-label">YouTube Email (for YouTube services)</label>
        <input class="form-input" id="m-yt" placeholder="you@gmail.com" type="email">
      </div>
      <div class="form-group">
        <label class="form-label">TradingView Username (for scanner)</label>
        <input class="form-input" id="m-tv" placeholder="your TradingView username">
      </div>

      <div class="pay-box">
        <div class="pay-amount-row">
          <span class="pay-label">Amount to pay</span>
          <span class="pay-amount" id="m-amount">₹499</span>
        </div>
        <div style="font-size:0.68rem;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.05em">Pay to UPI ID</div>
        <div class="upi-row">
          <span class="upi-val">9634759528@upi</span>
          <button class="btn-copy" onclick="copyUpi()">📋 Copy</button>
        </div>
        <div class="pay-steps">
          <div class="pay-step"><span class="pay-step-n">1</span>Copy UPI ID and open GPay / PhonePe / Paytm</div>
          <div class="pay-step"><span class="pay-step-n">2</span>Send <strong id="m-pay-step-amt" style="color:var(--gold)">₹499</strong> to UPI ID</div>
          <div class="pay-step"><span class="pay-step-n">3</span>Take screenshot of payment confirmation</div>
          <div class="pay-step"><span class="pay-step-n">4</span>Click WhatsApp below — send screenshot</div>
        </div>
      </div>

      <a class="btn-wa" href="#" id="m-wa-btn" onclick="confirmOrder(event)" target="_blank">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        Confirm via WhatsApp
      </a>
      <button class="btn-email" onclick="confirmOrder('email')">Confirm via Email instead</button>
      <div style="font-size:0.68rem;color:var(--muted);text-align:center;margin-top:12px;line-height:1.5">Access granted within 1 hour. Educational content only — not SEBI registered advice.</div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const CONFIG = {
  whatsapp: "919634759528",
  email:    "admin@ai360trading.in",
  upiId:    "9634759528@upi"
};

// Pricing data
const PRICES = {
  tg:    { monthly: 499,  annual: 3999  },
  yt:    { monthly: 299,  annual: 2499  },
  live:  { monthly: 699,  annual: 5999  },
  tv:    { monthly: 399,  annual: 2999  },
  combo: { monthly: 999,  annual: 7999  },
};

let billing = 'monthly';
let currentPlan = { name: '', price: 0, type: '' };

function setBilling(type) {
  billing = type;
  document.getElementById('btnM').classList.toggle('active', type === 'monthly');
  document.getElementById('btnA').classList.toggle('active', type === 'annual');

  // Update individual card prices
  const keys = ['tg', 'yt', 'live', 'tv'];
  const periods = { tg: 'Telegram', yt: 'YouTube Private', live: 'YouTube Live', tv: 'TradingView Scanner' };
  const annuals = { tg: '₹3,999/year', yt: '₹2,499/year', live: '₹5,999/year', tv: '₹2,999/year' };

  keys.forEach(k => {
    const p = PRICES[k];
    const amt = type === 'monthly' ? p.monthly : p.annual;
    document.getElementById(k+'-price').textContent  = '₹' + amt.toLocaleString('en-IN');
    document.getElementById(k+'-period').textContent = type === 'monthly' ? 'per month' : 'per year';
    document.getElementById(k+'-annual').textContent = type === 'monthly'
      ? 'or ₹' + p.annual.toLocaleString('en-IN') + '/year'
      : 'Save 33% vs monthly billing';
  });

  // Update combo
  if (type === 'monthly') {
    document.getElementById('combo-original').textContent = 'Individual total: ₹1,896/mo';
    document.getElementById('combo-price').textContent    = '₹999';
    document.getElementById('combo-period').textContent   = 'per month';
    document.getElementById('combo-saving').textContent   = 'You save ₹897/month — 47% off';
  } else {
    document.getElementById('combo-original').textContent = 'Individual total: ₹15,496/yr';
    document.getElementById('combo-price').textContent    = '₹7,999';
    document.getElementById('combo-period').textContent   = 'per year';
    document.getElementById('combo-saving').textContent   = 'You save ₹7,497/year — 48% off';
  }
}

function openModal(name, monthly, annual, type) {
  const price = billing === 'monthly' ? monthly : annual;
  currentPlan = { name, price, type };

  document.getElementById('m-name').textContent       = name;
  document.getElementById('m-price-label').textContent = '₹' + price.toLocaleString('en-IN') + (billing === 'monthly' ? '/month' : '/year');
  document.getElementById('m-amount').textContent      = '₹' + price.toLocaleString('en-IN');
  document.getElementById('m-pay-step-amt').textContent = '₹' + price.toLocaleString('en-IN');

  // Clear form
  ['m-name-in','m-phone','m-tg','m-yt','m-tv'].forEach(id => {
    const el = document.getElementById(id); if(el) el.value = '';
  });

  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
  document.body.style.overflow = '';
}
document.getElementById('modal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

function copyUpi() {
  navigator.clipboard.writeText(CONFIG.upiId)
    .then(() => showToast('UPI ID copied: ' + CONFIG.upiId))
    .catch(() => showToast('UPI ID: ' + CONFIG.upiId));
}

function confirmOrder(e) {
  if (e && e.preventDefault) e.preventDefault();
  const name  = document.getElementById('m-name-in').value.trim();
  const phone = document.getElementById('m-phone').value.trim();
  const tg    = document.getElementById('m-tg').value.trim();
  if (!name)  { showToast('Please enter your Name');             highlight('m-name-in'); return false; }
  if (!phone) { showToast('Please enter your WhatsApp number');  highlight('m-phone');   return false; }
  if (!tg)    { showToast('Please enter your Telegram username');highlight('m-tg');      return false; }

  const yt = document.getElementById('m-yt').value.trim();
  const tv = document.getElementById('m-tv').value.trim();

  const msg =
    "New Membership Request — AI360Trading\n\n" +
    "Service: " + currentPlan.name + "\n" +
    "Amount: Rs." + currentPlan.price.toLocaleString('en-IN') + " (" + billing + ")\n" +
    "Name: " + name + "\n" +
    "WhatsApp: " + phone + "\n" +
    "Telegram: " + tg + "\n" +
    (yt ? "YouTube Email: " + yt + "\n" : "") +
    (tv ? "TradingView: " + tv + "\n" : "") +
    "\nPayment of Rs." + currentPlan.price.toLocaleString('en-IN') +
    " sent to UPI: " + CONFIG.upiId +
    "\nPayment screenshot attached below.";

  if (e === 'email') {
    window.location.href = 'mailto:' + CONFIG.email +
      '?subject=' + encodeURIComponent('Membership: ' + currentPlan.name) +
      '&body=' + encodeURIComponent(msg);
    showToast('Opening email...');
  } else {
    window.open('https://wa.me/' + CONFIG.whatsapp + '?text=' + encodeURIComponent(msg), '_blank');
    showToast('Opening WhatsApp...');
  }
  closeModal();
  return false;
}

function highlight(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.borderColor = 'var(--gold)';
  el.focus();
  setTimeout(() => { el.style.borderColor = ''; }, 3000);
}

function toggleFaq(btn) {
  btn.parentElement.classList.toggle('open');
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}
</script>
