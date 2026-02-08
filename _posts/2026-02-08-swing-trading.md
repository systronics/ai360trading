---
layout:           post
title:            "Live Swing Trading Dashboard | Institutional Buy Signals"
image:            "https://ai360trading.in/public/image/swing.webp"
excerpt:          "Track real-time institutional buy signals with automated target and stop-loss tracking for NSE Nifty 200 stocks."
description:      "Automated stock scanner for NSE. View live P/L, entry prices, and exit targets on our trading terminal."
tags:             technical-picks
---

<style>
  /* 1. Global Page Width */
  .post-content, .wrapper {
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 0 15px !important;
  }

  /* 2. Professional Button Row */
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

  /* 4. FIXED TERMINAL CONTAINER - Solves Mobile Touch/Scroll */
  .terminal-wrapper {
    position: relative;
    width: 100%;
    overflow: hidden; /* Contains the scroll */
    border-radius: 12px;
    border: 1px solid #e1e8ed;
    background: #fff;
    margin-bottom: 30px;
  }

  .terminal-scroll-container {
    width: 100%;
    overflow-x: auto; /* Enables horizontal scroll */
    -webkit-overflow-scrolling: touch; /* Essential for smooth iOS/Android sliding */
  }

  /* Mobile Scroll Help Text */
  .scroll-hint {
    display: none;
    text-align: center;
    font-size: 12px;
    color: #7f8c8d;
    margin-bottom: 10px;
  }

  @media (max-width: 768px) {
    .scroll-hint { display: block; }
  }

  iframe {
    width: 100%;
    min-width: 1100px; /* Forces the sheet to be wide enough to require scrolling */
    height: 850px;
    border: none;
    display: block;
  }
</style>

<div class="action-buttons">
  <a href="https://t.me/{{ site.telegram.username }}" target="_blank" class="btn-tg">📱 Join Telegram Alerts</a>
</div>

<div class="live-status">
  <div class="blink"></div> ALGO SYSTEM LIVE: TRACKING NIFTY 200
</div>

<p class="scroll-hint">↔️ Swipe left/right to view full table</p>

<div class="terminal-wrapper">
  <div class="terminal-scroll-container">
    <iframe 
      id="live-terminal"
      src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQyI_2dA66bYzzsxZNW9yqSAkmi8_TxLA7PK_x6vtI9uqSbUNz-M5FXrYIt4rsP5B7kl6Mrfi5AUpsp/pubhtml?gid=1037713694&single=true&headers=false&chrome=false&widget=false">
    </iframe>
  </div>
</div>

<script>
  // Automatic Refresh to prevent stale trading data
  window.onload = function() {
    var iframe = document.getElementById('live-terminal');
    if (iframe) {
        var currentSrc = iframe.src;
        var timestamp = new Date().getTime();
        iframe.src = currentSrc + (currentSrc.indexOf('?') > -1 ? "&" : "?") + "cb=" + timestamp;
    }
  };
</script>
