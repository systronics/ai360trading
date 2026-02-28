---
layout: page
title: "Positional Trading - Long Term Value Picks"
image: "https://ai360trading.in/public/image/swing.webp"
excerpt: "Institutional grade long-term picks focusing on bottom-out setups and undervalued SIP opportunities."
permalink: /positional-picks/
---

<style>
  /* 1. Global Page Width Sync - Ensures center alignment */
  .post-content, .wrapper {
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 0 15px !important;
  }

  /* 2. Professional Dashboard UI */
  .trading-status {
    text-align: center;
    margin-bottom: 30px;
    padding: 25px;
    background: #f0f7ff;
    border-radius: 12px;
    border: 1px solid #d1d9e6;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  }

  .info-tag {
    display: inline-block;
    padding: 6px 16px;
    background: #0088cc;
    color: white !important;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 12px;
    letter-spacing: 0.5px;
  }

  /* 3. MOBILE SCROLL FIX - Optimized for Human Manual Touch */
  .terminal-box {
    position: relative;
    width: 100%;
    /* Removed overflow:hidden to prevent mobile scroll locking */
    border: 1px solid #e1e8ed;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    background: #fff;
    margin-bottom: 30px;
  }

  /* This container handles the actual touch swipe */
  .terminal-scroll-container {
    width: 100%;
    overflow-x: auto !important;
    overflow-y: hidden;
    /* Smooth swipe for mobile */
    -webkit-overflow-scrolling: touch !important;
    /* Prioritize horizontal swipe to prevent page wiggle */
    touch-action: pan-x; 
    border-radius: 12px;
  }

  iframe {
    width: 100%;
    min-width: 1100px; /* Maintains professional spacing for many columns */
    height: 800px;
    border: none;
    display: block;
  }

  /* 4. Expert View Hint - Hand-crafted feel */
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
    font-weight: 500;
  }

  @media (max-width: 768px) {
    .scroll-hint { display: block; }
    iframe { height: 700px; } /* Slightly shorter for better mobile fit */
  }
</style>

<div class="trading-status">
  <span class="info-tag">STRATEGY: BOTTOM-OUT SCREENER</span>
  <h2 style="margin: 5px 0; color: #2c3e50; font-size: 26px;">Institutional Positional Picks</h2>
  <p style="font-size: 15px; color: #4a5568; margin-top: 10px;">Focusing on Undervalued Stocks for 3-12 Month Investment Horizon</p>
</div>

<p class="scroll-hint">↔️ <b>Expert View:</b> Swipe left/right to view full research table</p>

<div class="terminal-box">
  <div class="terminal-scroll-container">
    <iframe 
      id="positional-terminal"
      src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRxCmYGRepK_DgUk-KMeudF4PoQ9B89msVkMeZmImFb-2QaXobqjOthwdMDlvxpHtu3S9UtyXo9SrOR/pubhtml?gid=1640788813&single=true&headers=false&chrome=false&widget=false">
    </iframe>
  </div>
</div>

<div style="margin-top: 30px; padding: 20px; background: #fffdf0; border-left: 5px solid #f1c40f; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
  <p style="font-size: 14px; color: #4a5568; margin: 0; line-height: 1.6;">
    <strong>Investment Note:</strong> Positional trades are updated weekly based on fundamental shifts and institutional delivery volumes. These picks are hand-vetted for long-term wealth creation rather than speculative scalps.
  </p>
  <p style="font-size: 12px; color: #7f8c8d; margin-top: 10px; font-weight: 600;">
    🕒 <strong>Market Monitoring Active:</strong> {{ "now" | date: "%d-%b-%Y %H:%M" }} IST
  </p>
</div>

<script>
  // Automatic Refresh to prevent stale trading data
  window.onload = function() {
    var iframe = document.getElementById('positional-terminal');
    if (iframe) {
        var currentSrc = iframe.src;
        var timestamp = new Date().getTime();
        // Force fresh load with a cache-buster timestamp
        iframe.src = currentSrc + (currentSrc.indexOf('?') > -1 ? "&" : "?") + "cb=" + timestamp;
    }
  };
</script>
