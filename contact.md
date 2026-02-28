---
layout: default
title: "Contact AI360Trading | Support"
---

<div class="contact-card">
  <div class="contact-header">
    <h1 class="contact-title">Contact Us</h1>
    <p class="contact-subtitle">Institutional-grade support for our trading community.</p>
    <div class="contact-info-bar">
      <span>📧 admin@ai360trading.in</span>
      <span>⏱️ Response within 24 hours</span>
      <span>📅 Mon–Fri, Market Days</span>
    </div>
  </div>

  <form action="https://formspree.io/f/your-id" method="POST" class="contact-form">
    <div class="form-row">
      <div class="input-group">
        <label>Full Name</label>
        <input type="text" name="name" placeholder="Enter your full name" required>
      </div>
      <div class="input-group">
        <label>Email Address</label>
        <input type="email" name="email" placeholder="email@example.com" required>
      </div>
    </div>

    <div class="input-group">
      <label>Inquiry Type</label>
      <select name="type" required class="contact-select">
        <option value="" disabled selected>Select inquiry type...</option>
        <option value="General">💬 General Inquiry</option>
        <option value="Dashboard">📊 Dashboard Intelligence</option>
        <option value="Technical">🔧 Technical Support</option>
        <option value="Feedback">⭐ Feedback & Suggestions</option>
        <option value="Partnership">🤝 Partnership & Collaboration</option>
      </select>
    </div>

    <div class="input-group">
      <label>Subject</label>
      <input type="text" name="subject" placeholder="Brief subject of your message" required>
    </div>

    <div class="input-group">
      <label>Your Message</label>
      <textarea name="message" rows="6" placeholder="Please describe your inquiry in detail. The more information you provide, the better we can assist you." required></textarea>
    </div>

    <div class="checkbox-group">
      <input type="checkbox" id="agree" name="agree" required>
      <label for="agree">I have read and agree to the <a href="/policy/">Privacy Policy & Terms</a></label>
    </div>

    <button type="submit" class="send-btn">
      <span class="btn-text">SEND MESSAGE</span>
      <span class="btn-icon">→</span>
    </button>
  </form>

  <div class="contact-channels">
    <h3>Other Ways to Reach Us</h3>
    <div class="channels-grid">
      <div class="channel-item">
        <span class="channel-icon">📧</span>
        <span class="channel-label">Email</span>
        <a href="mailto:admin@ai360trading.in">admin@ai360trading.in</a>
      </div>
      <div class="channel-item">
        <span class="channel-icon">🌐</span>
        <span class="channel-label">Website</span>
        <a href="https://ai360trading.in">ai360trading.in</a>
      </div>
      <div class="channel-item">
        <span class="channel-icon">📍</span>
        <span class="channel-label">Location</span>
        <span>Haridwar, Uttarakhand, India</span>
      </div>
    </div>
  </div>

  <div class="contact-footer">
    <p>⚠️ For financial advice, please consult a SEBI registered advisor. We provide educational content only.</p>
  </div>
</div>

<style>
  .contact-card {
    max-width: 750px;
    margin: 20px auto;
    background: #ffffff;
    padding: 40px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  }

  .contact-header {
    text-align: center;
    margin-bottom: 35px;
  }

  .contact-title {
    color: #0062ff;
    font-size: 30px;
    font-weight: 900;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
  }

  .contact-subtitle {
    color: #64748b;
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 20px;
  }

  .contact-info-bar {
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
    background: #f0f7ff;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 13px;
    color: #0062ff;
    font-weight: 600;
  }

  .contact-form {
    display: flex;
    flex-direction: column;
    gap: 22px;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .input-group label {
    font-weight: 800;
    font-size: 12px;
    text-transform: uppercase;
    color: #475569;
    letter-spacing: 0.5px;
  }

  .input-group input,
  .input-group textarea,
  .contact-select {
    padding: 14px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-family: inherit;
    font-size: 15px;
    background-color: #f8fafc;
    transition: all 0.2s ease;
    color: #1e293b;
  }

  .contact-select {
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 15px center;
    background-size: 16px;
  }

  .input-group input:focus,
  .input-group textarea:focus,
  .contact-select:focus {
    outline: none;
    border-color: #0062ff;
    background-color: #ffffff;
    box-shadow: 0 0 0 4px rgba(0, 98, 255, 0.1);
  }

  .checkbox-group {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: #475569;
  }

  .checkbox-group input[type="checkbox"] {
    width: 16px;
    height: 16px;
    cursor: pointer;
    accent-color: #0062ff;
  }

  .checkbox-group a {
    color: #0062ff;
    text-decoration: none;
    font-weight: 600;
  }

  .checkbox-group a:hover {
    text-decoration: underline;
  }

  .send-btn {
    background: #0062ff;
    color: white;
    border: none;
    padding: 16px;
    border-radius: 8px;
    font-weight: 800;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  .send-btn:hover {
    background: #004dc7;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 98, 255, 0.3);
  }

  .btn-icon {
    font-size: 18px;
    transition: transform 0.2s ease;
  }

  .send-btn:hover .btn-icon {
    transform: translateX(4px);
  }

  .contact-channels {
    margin-top: 40px;
    padding-top: 30px;
    border-top: 1px solid #f1f5f9;
  }

  .contact-channels h3 {
    font-size: 16px;
    font-weight: 800;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 20px;
    text-align: center;
  }

  .channels-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
  }

  .channel-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 20px 15px;
    background: #f8fafc;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    gap: 6px;
  }

  .channel-icon {
    font-size: 24px;
  }

  .channel-label {
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.5px;
  }

  .channel-item a, .channel-item span:last-child {
    font-size: 13px;
    color: #0062ff;
    text-decoration: none;
    font-weight: 600;
    word-break: break-all;
  }

  .channel-item a:hover {
    text-decoration: underline;
  }

  .contact-footer {
    margin-top: 30px;
    text-align: center;
    font-size: 13px;
    color: #94a3b8;
    font-style: italic;
    border-top: 1px solid #f1f5f9;
    padding-top: 20px;
  }

  @media (max-width: 600px) {
    .contact-card {
      padding: 30px 20px;
      margin: 0;
      border-radius: 0;
      border: none;
    }
    .contact-title { font-size: 26px; }
    .form-row { grid-template-columns: 1fr; }
    .channels-grid { grid-template-columns: 1fr; }
    .contact-info-bar { gap: 10px; font-size: 12px; }
  }
</style>
