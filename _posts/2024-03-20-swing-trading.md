---
layout:           post
title:            "Live Swing Trading Dashboard | Institutional Buy Signals"
date:             2026-01-05T09:15:00+05:30
last_modified_at: 2026-01-05T23:10:00+05:30
author:           "Amit Kumar"
image:            https://ai360trading.in/public/image/swing.webp
excerpt:          "Track real-time institutional buy signals with automated target and stop-loss tracking for NSE Nifty 200 stocks."
description:      "Automated stock scanner for NSE. View live P/L, entry prices, and exit targets on our trading terminal."
tags:             technical-picks
---

<style>
  /* 1. Global Page Width Upgrade */
  .post-content, .wrapper {
    max-width: 98% !important;
    padding: 0 10px !important;
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
  .btn-tg:hover { transform: translateY(-2px); }

  /* 3. Live Blinking Indicator */
  .live-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 10px;
    color: #2ecc71;
    font-weight: bold;
    font-size: 14px;
  }
  .blink {
    height: 10px;
    width: 10px;
    background-color: #2ecc71;
    border-radius: 50%;
    animation: blink-animation 1.5s infinite;
  }
  @keyframes blink-animation {
    0% { opacity: 1; }
    50% { opacity: 0.3; }
    100% { opacity: 1; }
  }

  /* 4. Terminal Container */
  .terminal-container {
    width: 100%;
    overflow-x: auto;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    background: #fff;
    -webkit-overflow-scrolling: touch;
  }
  iframe {
    width: 100%;
    min-width: 1100px; /* Prevents column squeezing */
    height: 750px;
    border: none;
  }
</style>

<div class="action-buttons">
  <a href="https://t.me/ai360trading" target="_blank" class="btn-tg">📱 Join Telegram Alerts</a>
</div>

<div class="live-status">
  <div class="blink"></div> SYSTEM LIVE: TRACKING NIFTY 200
</div>

<div class="terminal-container">
  <iframe 
    id="live-terminal"
    src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQyI_2dA66bYzzsXZNW9yqSAkml8_TxLA7PK_x6vtl9uqSbUNz-M5FXrYlt4rsP5B7kl6Mrfi5AUpsp/pubhtml?gid=1037713694&amp;single=true&headers=false&chrome=false&widget=false">
  </iframe>
</div>

<script>
  // Cache-Buster Script (Zero Speed Impact)
  window.onload = function() {
    var iframe = document.getElementById('live-terminal');
    var timestamp = new Date().getTime();
    iframe.src += (iframe.src.indexOf('?') > -1 ? "&" : "?") + "cb=" + timestamp;
  };
</script>

