---
layout: default
title: "Contact AI360Trading"
---

<div class="contact-card">
  <div class="contact-header">
    <h1 class="contact-title">Contact Us</h1>
    <p class="contact-subtitle">Institutional-grade support for our trading community.</p>
  </div>

  <form action="https://formspree.io/f/your-id" method="POST" class="contact-form">
    <div class="input-group">
      <label>Full Name</label>
      <input type="text" name="name" placeholder="Enter your name" required>
    </div>

    <div class="input-group">
      <label>Email Address</label>
      <input type="email" name="email" placeholder="email@example.com" required>
    </div>

    <div class="input-group">
      <label>Your Message</label>
      <textarea name="message" rows="5" placeholder="How can we assist you?" required></textarea>
    </div>

    <button type="submit" class="send-btn">SEND MESSAGE</button>
  </form>

  <div class="contact-footer">
    <p>Response time: Usually within 24 hours during market days.</p>
  </div>
</div>

<style>
  /* RESTORING PREVIOUS WORKING STYLES */
  .contact-card {
    max-width: 700px;
    margin: 0 auto;
    background: #ffffff;
    padding: 40px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  }

  .contact-header {
    text-align: center;
    margin-bottom: 35px;
  }

  .contact-title {
    color: #0062ff;
    font-size: 26px;
    font-weight: 900;
    margin-bottom: 10px;
  }

  .contact-subtitle {
    color: #64748b;
    font-size: 15px;
  }

  .contact-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .input-group label {
    font-weight: 800;
    font-size: 13px;
    text-transform: uppercase;
    color: #0f172a;
  }

  .input-group input, .input-group textarea {
    padding: 12px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-family: inherit;
    font-size: 15px;
  }

  .input-group input:focus, .input-group textarea:focus {
    outline: none;
    border-color: #0062ff;
    box-shadow: 0 0 0 3px rgba(0, 98, 255, 0.1);
  }

  .send-btn {
    background: #0062ff;
    color: white;
    border: none;
    padding: 15px;
    border-radius: 8px;
    font-weight: 800;
    cursor: pointer;
    transition: 0.3s;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .send-btn:hover {
    background: #004dc7;
    transform: translateY(-2px);
  }

  .contact-footer {
    margin-top: 30px;
    text-align: center;
    font-size: 13px;
    color: #94a3b8;
    font-style: italic;
  }

  @media (max-width: 600px) {
    .contact-card { padding: 25px 20px; border-radius: 0; border: none; }
  }
</style>
