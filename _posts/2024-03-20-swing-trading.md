---
layout:           post
title:            Swing Trading
date:             2025-12-20T13:04:19+05:45
last_modified_at: 2025-12-20T05:20:00+05:45
image:            https://ai360trading.in/public/image/swing.webp
excerpt:          Intraday, Positional, Swing, Breakout, ai360tradingAlgo, SIP
tags:             technical-picks
---

<div id="dashboard-container" style="width: 100%; text-align: center;">
  <p style="font-size: 12px; color: #666;">🕒 Data refreshes every 5 mins. Updates are automatic.</p>
  
  <iframe 
    id="live-sheet"
    src="" 
    style="width: 100%; height: 800px; border: 1px solid #ddd; border-radius: 8px;">
  </iframe>
</div>

<script>
  // This script adds a unique timestamp to the URL every time the page loads.
  // This prevents the browser from showing an "old" version of your sheet.
  window.onload = function() {
    var baseUrl = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQyI_2dA66bYzzsxZNW9yqSAkmi8_TxLA7PK_x6vtI9uqSbUNz-M5FXrYIt4rsP5B7kl6Mrfi5AUpsp/pubhtml?gid=1037713694&single=true&headers=false&chrome=false";
    var timestamp = new Date().getTime();
    document.getElementById('live-sheet').src = baseUrl + "&cachebust=" + timestamp;
  };
</script>
