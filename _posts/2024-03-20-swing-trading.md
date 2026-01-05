---
layout:           post
title:            Swing Trading
date:             2025-12-20T13:04:19+05:45
last_modified_at: 2025-12-20T05:20:00+05:45
image:            https://ai360trading.in/public/image/swing.webp
excerpt:          Intraday, Positional, Swing, Breakout, ai360tradingAlgo, SIP
tags:             technical-picks
---

<style>
  .post-content, .wrapper {
    max-width: 98% !important;
    padding: 0 10px !important;
  }
  .dashboard-wrapper {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
  }
  .iframe-container {
    width: 100%;
    overflow-x: auto; /* Enables swiping on mobile */
    -webkit-overflow-scrolling: touch;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    background: #fff;
  }
  iframe {
    width: 100%;
    min-width: 1100px; /* Ensures all 14 columns are visible without squeezing */
    height: 750px;
    border: none;
    display: block;
  }
  .sync-note {
    font-size: 13px;
    color: #555;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 5px;
  }
</style>

<div class="dashboard-wrapper">
  <div class="sync-note">
    <span>🕒</span> Data refreshes every 5 mins. Updates are automatic.
  </div>

  <div class="iframe-container">
    <iframe 
      id="live-trading-sheet"
      src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQyI_2dA66bYzzsxZNW9yqSAkmi8_TxLA7PK_x6vtI9uqSbUNz-M5FXrYIt4rsP5B7kl6Mrfi5AUpsp/pubhtml?gid=1037713694&single=true&headers=false&chrome=false&widget=false">
    </iframe>
  </div>
</div>

<script>
  /**
   * CACHE-BUSTER SCRIPT
   * This ensures that every time a subscriber visits your site, 
   * they see the newest data instead of a cached version.
   */
  window.onload = function() {
    var iframe = document.getElementById('live-trading-sheet');
    var timestamp = new Date().getTime();
    // Appends a unique ID to the URL to force a fresh load
    if (iframe.src.indexOf('?') > -1) {
      iframe.src += "&cb=" + timestamp;
    } else {
      iframe.src += "?cb=" + timestamp;
    }
  };
</script>
