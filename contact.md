---
layout: default
title: "Contact AI360Trading | Support"
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
      <label>Inquiry Type</label>
      <select name="type" required class="contact-select">
        <option value="General">General Inquiry</option>
        <option value="Dashboard">Dashboard Intelligence</option>
        <option value="Technical">Technical Support</option>
      </select>
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
  .contact-card {
    max-width: 700px;
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
  }

  .contact-form {
    display: flex;
    flex-direction: column;
    gap: 22px;
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
  }

  .send-btn:hover {
    background: #004dc7;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 98, 255, 0.2);
  }

  .contact-footer {
    margin-top: 35px;
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
  }
</style>
