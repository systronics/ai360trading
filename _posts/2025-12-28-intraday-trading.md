---
layout: post
title: "Intraday Trading: Live Algo-Scanner"
date: 2026-01-06T00:25:00+05:30
last_modified_at: 2026-01-06T00:25:00+05:30
image: "https://ai360trading.in/public/image/intraday.webp"
excerpt: "Real-time Intraday, Breakout, and Momentum signals powered by ai360trading Algo."
tags: technical-picks
---

<style>
  /* Intraday High-Speed Terminal UI */
  .intraday-header {
    text-align: center;
    background: #f8faff;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #d1d9e6;
    margin-bottom: 25px;
  }
  
  .live-dot {
    height: 10px;
    width: 10px;
    background-color: #ff4d4d;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 77, 77, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 77, 77, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 77, 77, 0); }
  }

  .terminal-box {
    width: 100%;
    overflow-x: auto;
    border: 1px solid #2c3e50;
    border-radius: 10px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    background: #fff;
    -webkit-overflow-scrolling: touch;
  }

  iframe {
    width: 100%;
    min-width: 1000px; /* Essential for keeping columns aligned on mobile */
    height: 700px;
    border: none;
    display: block;
  }
</style>

<div class="intraday-header">
  <div style="margin-bottom: 10px;">
    <span class="live-dot"></span> 
    <span style="font-size: 12px; font-weight: bold; color: #ff4d4d; letter-spacing: 1px;">ALGO LIVE</span>
  </div>
  <h2 style="margin: 0; color: #2c3e50;">Intraday Momentum Scanner</h2>
  <p style="color: #666; font-size: 14px; margin-top: 5px;">Automatic Breakout & Breakdown signals updated every 5 minutes.</p>
</div>

<div class="terminal-box">
  <iframe 
    src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQ-E98O-wsBDHFmi4L4JHcW2fdTFjisvtJHWE4wj080bz0dUFr_YRHiTCsVLgSQyrr7PvCxPisUMXDf/pubhtml?gid=1473515751&single=true&headers=false&chrome=false&widget=false">
  </iframe>
</div>

<div style="margin-top: 20px; padding: 15px; background: #fff5f5; border-radius: 8px; border: 1px solid #ffebeb;">
  <p style="font-size: 13px; color: #c0392b; margin: 0; text-align: center;">
    <strong>Note:</strong> Data refreshes automatically. For best results, use during live market hours (9:15 AM - 3:30 PM).
  </p>
</div>
