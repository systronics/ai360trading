---
layout: page
title: "Intraday Trading: Live Algo-Scanner"
image: "https://ai360trading.in/public/image/intraday.webp"
excerpt: "Real-time Intraday, Breakout, and Momentum signals powered by ai360trading Algo."
permalink: /intraday-live/
tags: technical-picks
---

<style>
  /* 1. Global Page Width Sync - Fixes left-side cutting */
  .post-content, .wrapper {
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 0 15px !important;
  }

  /* 2. Intraday High-Speed Terminal UI */
  .intraday-header {
    text-align: center;
    background: #f8faff;
    padding: 30px;
    border-radius: 12px;
    border: 1px solid #d1d9e6;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  }
  
  .live-dot {
    height: 12px;
    width: 12px;
    background-color: #ff4d4d;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 77, 77, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 77, 77, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 77, 77, 0); }
  }

  /* 3. MOBILE SCROLL FIX - Terminal Box Wrapper */
  .terminal-box {
    width: 100%;
    overflow: hidden; /* Trap the iframe scaling */
    border: 1px solid #2c3e50;
    border-radius: 12px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    background: #fff;
    margin-bottom: 30px;
  }

  .terminal-scroll-container {
    width: 100%;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important; /* Smooth touch swipe for Intraday users */
  }

  iframe {
    width: 100%;
    min-width: 1050px; /* Essential for mobile readability of live columns */
    height: 750px;
    border: none;
    display: block;
  }

  /* Mobile Swipe Hint */
  .scroll-hint {
    display: none;
    text-align: center;
    font-size: 13px;
    color: #ff4d4d;
    font-weight: bold;
    margin-bottom: 10px;
  }

  @media (max-width: 768px) {
    .scroll-hint { display: block; }
  }
</style>

<div class="intraday-header">
  <div style="margin-bottom: 12px; display: flex; align-items: center; justify-content: center;">
    <span class="live-dot"></span> 
    <span style="font-size: 13px; font-weight: bold; color: #ff4d4d; letter-spacing: 1.5px; text-transform: uppercase;">Algo System Live</span>
  </div>
  <h2 style="margin: 0; color: #2c3e50; font-size: 26px;">Intraday Momentum Scanner</h2>
  <p style="color: #4a5568; font-size: 15px; margin-top: 10px;">Automatic Breakout & Breakdown signals updated in real-time for fast scalping.</p>
</div>

<p class="scroll-hint">↔️ SWIPE TO TRACK LIVE SIGNALS</p>

<div class="terminal-box">
  <div class="terminal-scroll-container">
    <iframe 
      id="intraday-terminal"
      src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQ-E98O-wsBDHFmi4L4JHcW2fdTFjisvtJHWE4wj080bz0dUFr_YRHiTCsVLgSQyrr7PvCxPisUMXDf/pubhtml?gid=1473515751&single=true&headers=false&chrome=false&widget=false">
    </iframe>
  </div>
</div>

<div style="padding: 20px; background: #fff5f5; border-radius: 10px; border: 1px solid #ffebeb; text-align: center;">
  <p style="font-size: 14px; color: #c0392b; margin: 0; line-height: 1.6;">
    <strong>High Performance Note:</strong> Data refreshes automatically. For high-speed execution, monitor this terminal during live market hours <strong>(9:15 AM - 3:30 PM IST)</strong>.
  </p>
</div>

<script>
  // Force high-speed refresh for Intraday signals
  window.onload = function() {
    var iframe = document.getElementById('intraday-terminal');
    if (iframe) {
        var currentSrc = iframe.src;
        var timestamp = new Date().getTime();
        // Append unique ID to bypass cache for live signals
        iframe.src = currentSrc + (currentSrc.indexOf('?') > -1 ? "&" : "?") + "cb=" + timestamp;
    }
  };
</script>
