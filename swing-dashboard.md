---
layout: page
title: "Live Swing Trading Dashboard | Institutional Buy Signals"
image: "https://ai360trading.in/public/image/swing.webp"
excerpt: "Track real-time institutional buy signals with automated target and stop-loss tracking for NSE Nifty 200 stocks."
permalink: /swing-dashboard/
---

<style>
  /* 1. Global Page Width Fix */
  .post-content, .wrapper {
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 0 15px !important;
  }

  /* 2. Professional Button UI */
  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin: 20px 0;
    flex-wrap: wrap;
  }
  .btn-tg {
    background-color: #0088cc;
    color: white !important;
    padding: 12px 25px;
    border-radius: 50px;
    text-decoration: none !important;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0,136,204,0.3);
    transition: 0.3s;
  }

  /* 3. Live Blinking Indicator */
  .live-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 20px 0;
    color: #2ecc71;
    font-weight: bold;
    font-size: 16px;
  }
  .blink {
    height: 12px;
    width: 12px;
    background-color: #2ecc71;
    border-radius: 50%;
    animation: blink-animation 1.5s infinite;
  }
  @keyframes blink-animation {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
    100% { opacity: 1; transform: scale(1); }
  }

  /* 4. TERMINAL CONTAINER FIX */
  .terminal-wrapper {
    position: relative;
    width: 100%;
    border-radius: 12px;
    border: 1px solid #e1e8ed;
    background: #fff;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    overflow: visible;
  }
  .terminal-scroll-container {
    width: 100%;
    overflow-x: auto !important;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch !important;
    touch-action: pan-x;
    border-radius: 12px;
  }
  iframe {
    width: 100%;
    min-width: 1050px;
    height: 850px;
    border: none;
    display: block;
  }

  /* 5. Mobile Swipe Hint */
  .scroll-hint {
    display: none;
    text-align: center;
    font-size: 13px;
    color: #34495e;
    margin-bottom: 12px;
    padding: 10px;
    background: #f8f9fa;
    border: 1px dashed #cbd5e0;
    border-radius: 6px;
  }

  /* 6. SEO Content Section */
  .dashboard-intro {
    background: #f8fafc;
    border-left: 4px solid #0062ff;
    border-radius: 0 8px 8px 0;
    padding: 20px 25px;
    margin: 25px 0;
    font-size: 16px;
    color: #1e293b;
    line-height: 1.8;
  }

  .dashboard-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin: 30px 0;
  }
  .feature-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }
  .feature-card h3 {
    font-size: 15px !important;
    font-weight: 800;
    color: #0062ff;
    margin: 0 0 8px 0;
  }
  .feature-card p {
    font-size: 14px;
    color: #4a5568;
    margin: 0;
    line-height: 1.6;
  }

  /* 7. Internal Links */
  .internal-nav {
    margin: 30px 0;
    padding: 20px;
    background: #f0f4f8;
    border-radius: 10px;
  }
  .internal-nav p {
    font-weight: 800;
    font-size: 14px;
    color: #0f172a;
    margin: 0 0 12px 0;
  }
  .internal-nav-links {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  .nav-link {
    background: #ffffff;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 700;
    color: #0062ff !important;
    text-decoration: none;
    border: 1px solid #e2e8f0;
    transition: 0.2s;
  }
  .nav-link:hover {
    background: #0062ff;
    color: white !important;
    border-color: #0062ff;
  }

  /* 8. Disclaimer */
  .dashboard-disclaimer {
    margin-top: 30px;
    padding: 15px 20px;
    background: #fff5f5;
    border: 1px solid #fed7d7;
    border-radius: 8px;
    font-size: 13px;
    color: #744210;
    line-height: 1.7;
  }

  @media (max-width: 768px) {
    .scroll-hint { display: block; }
    iframe { height: 700px; }
    .dashboard-features { grid-template-columns: 1fr; }
  }
</style>

<!-- INTRO TEXT: Matches H1 for SEO -->
<div class="dashboard-intro">
  <strong>Live Swing Trading Dashboard</strong> tracks institutional buy signals across NSE Nifty 200 stocks in real time. Our algo system identifies high-probability swing trading setups using price action logic, volume analysis, and institutional order flow. Each signal comes with a defined entry zone, target price, and stop-loss level — so you always know your risk before entering a trade.
</div>

<div class="action-buttons">
  <a href="https://t.me/{{ site.telegram_username }}" 
     target="_blank" 
     class="btn-tg">
     📣 JOIN TELEGRAM FOR ALERTS
  </a>
</div>

<div class="live-status">
  <div class="blink"></div> ALGO SYSTEM LIVE: TRACKING NIFTY 200
</div>

<p class="scroll-hint">↔️ <b>Expert View:</b> Swipe left/right to view full terminal data</p>

<div class="terminal-wrapper">
  <div class="terminal-scroll-container">
    <iframe 
      id="live-terminal"
      src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQyI_2dA66bYzzsxZNW9yqSAkmi8_TxLA7PK_x6vtI9uqSbUNz-M5FXrYIt4rsP5B7kl6Mrfi5AUpsp/pubhtml?gid=1037713694&single=true&headers=false&chrome=false&widget=false">
    </iframe>
  </div>
</div>

<!-- FEATURE CARDS: Adds word count + matches H1 keywords -->
<div class="dashboard-features">
  <div class="feature-card">
    <h3>📊 Institutional Buy Signals</h3>
    <p>Each swing trade signal is derived from institutional order flow patterns and high-volume price action setups on NSE-listed Nifty 200 stocks.</p>
  </div>
  <div class="feature-card">
    <h3>🎯 Entry, Target & Stop-Loss</h3>
    <p>Every signal includes a precise entry zone, profit target, and stop-loss level. Risk is always defined before you enter a trade.</p>
  </div>
  <div class="feature-card">
    <h3>⚡ Real-Time Updates</h3>
    <p>The dashboard refreshes automatically to reflect the latest market data. Signals are updated daily before market open and after close.</p>
  </div>
  <div class="feature-card">
    <h3>📈 Swing Trading Focus</h3>
    <p>Setups are designed for 3 to 15 day holding periods — ideal for traders who cannot monitor intraday moves but want consistent swing trading results.</p>
  </div>
</div>

<!-- INTERNAL LINKS -->
<div class="internal-nav">
  <p>EXPLORE MORE:</p>
  <div class="internal-nav-links">
    <a href="/analysis/" class="nav-link">📊 Market Analysis</a>
    <a href="/positional-picks/" class="nav-link">🎯 Positional Picks</a>
    <a href="/earn-money/" class="nav-link">💰 Earn Money</a>
    <a href="/about/" class="nav-link">ℹ️ About</a>
    <a href="/disclaimer/" class="nav-link">📋 Disclaimer</a>
    <a href="/policy/" class="nav-link">🔒 Privacy Policy</a>
  </div>
</div>

<!-- DISCLAIMER -->
<div class="dashboard-disclaimer">
  ⚠️ <strong>Risk Disclaimer:</strong> Swing trading signals on this dashboard are for educational and informational purposes only. They do not constitute financial advice. Markets are inherently unpredictable — always use proper position sizing and never risk more than you can afford to lose. Read our full <a href="/disclaimer/">Legal Disclaimer</a> before acting on any signal.
</div>

<script>
  window.onload = function() {
    var iframe = document.getElementById('live-terminal');
    if (iframe) {
        var currentSrc = iframe.src;
        var timestamp = new Date().getTime();
        iframe.src = currentSrc + (currentSrc.indexOf('?') > -1 ? "&" : "?") + "cb=" + timestamp;
    }
  };
</script>
