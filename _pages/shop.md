---
layout: default
title: "Shop — Amit's Store"
permalink: /shop/
description: "Buy quality items directly from Amit Kumar. Order via WhatsApp or Email. Pay via UPI."
---

<style>
/* ── FONTS ── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --ink:       #1a1a2e;
  --paper:     #faf8f3;
  --accent:    #e63946;
  --gold:      #f4a261;
  --soft:      #f1ede4;
  --border:    #e0d9cc;
  --muted:     #7a7065;
  --green:     #2a9d5c;
  --shadow:    0 4px 24px rgba(26,26,46,0.10);
  --shadow-lg: 0 12px 48px rgba(26,26,46,0.16);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.shop-wrap {
  background: var(--paper);
  font-family: 'DM Sans', sans-serif;
  color: var(--ink);
  min-height: 100vh;
}

/* ── HERO BANNER ── */
.shop-hero {
  background: var(--ink);
  padding: 56px 24px 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.shop-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 40px,
    rgba(244,162,97,0.04) 40px,
    rgba(244,162,97,0.04) 80px
  );
}
.shop-hero h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2rem, 5vw, 3.5rem);
  color: #fff;
  position: relative;
  line-height: 1.1;
}
.shop-hero h1 span { color: var(--gold); }
.shop-hero p {
  color: rgba(255,255,255,0.65);
  margin-top: 12px;
  font-size: 1rem;
  position: relative;
}
.shop-badges {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 20px;
  position: relative;
}
.shop-badge {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.85);
  padding: 6px 14px;
  border-radius: 100px;
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* ── FILTER BAR ── */
.filter-bar {
  display: flex;
  gap: 8px;
  padding: 20px 24px;
  flex-wrap: wrap;
  max-width: 1100px;
  margin: 0 auto;
  align-items: center;
}
.filter-btn {
  padding: 8px 18px;
  border-radius: 100px;
  border: 1.5px solid var(--border);
  background: #fff;
  color: var(--muted);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-btn:hover, .filter-btn.active {
  background: var(--ink);
  color: #fff;
  border-color: var(--ink);
}
.filter-count {
  background: var(--accent);
  color: #fff;
  border-radius: 100px;
  padding: 1px 7px;
  font-size: 0.72rem;
  margin-left: 4px;
}

/* ── PRODUCT GRID ── */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding: 8px 24px 48px;
  max-width: 1100px;
  margin: 0 auto;
}

/* ── PRODUCT CARD ── */
.product-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: transform 0.25s, box-shadow 0.25s;
  position: relative;
  display: flex;
  flex-direction: column;
}
.product-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
.product-img-wrap {
  position: relative;
  background: var(--soft);
  aspect-ratio: 4/3;
  overflow: hidden;
}
.product-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s;
}
.product-card:hover .product-img-wrap img {
  transform: scale(1.04);
}
.product-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: var(--accent);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 100px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.product-badge.used { background: var(--gold); color: var(--ink); }
.product-badge.new  { background: var(--green); }

.share-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255,255,255,0.92);
  border: none;
  border-radius: 50%;
  width: 34px;
  height: 34px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  transition: transform 0.2s;
}
.share-btn:hover { transform: scale(1.12); }

.product-body {
  padding: 16px 18px 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.product-category {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 6px;
}
.product-name {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.3;
  margin-bottom: 8px;
}
.product-desc {
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.5;
  flex: 1;
  margin-bottom: 12px;
}

/* ── RATING ── */
.rating-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
}
.stars { color: var(--gold); font-size: 0.9rem; letter-spacing: 1px; }
.rating-count { font-size: 0.78rem; color: var(--muted); }
.rating-input { display: none; }
.rating-input.show { display: flex; gap: 4px; }
.star-pick {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--border);
  transition: color 0.15s;
}
.star-pick:hover, .star-pick.lit { color: var(--gold); }

/* ── PRICE ROW ── */
.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
}
.price {
  font-family: 'Playfair Display', serif;
  font-size: 1.45rem;
  font-weight: 900;
  color: var(--ink);
}
.price-original {
  font-size: 0.85rem;
  color: var(--muted);
  text-decoration: line-through;
}
.price-save {
  font-size: 0.78rem;
  color: var(--green);
  font-weight: 600;
  background: rgba(42,157,92,0.1);
  padding: 3px 8px;
  border-radius: 100px;
}

/* ── ACTION BUTTONS ── */
.action-btns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.btn-whatsapp {
  background: #25d366;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 11px 8px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: background 0.2s, transform 0.15s;
  text-decoration: none;
}
.btn-whatsapp:hover { background: #1ebe5d; transform: scale(1.02); }
.btn-order {
  background: var(--ink);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 11px 8px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: background 0.2s, transform 0.15s;
}
.btn-order:hover { background: #2d2d4e; transform: scale(1.02); }

/* ── COMMENTS ── */
.comments-section {
  border-top: 1px solid var(--border);
  padding: 12px 18px 16px;
}
.comments-toggle {
  background: none;
  border: none;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  color: var(--muted);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  gap: 5px;
}
.comments-toggle:hover { color: var(--ink); }
.comments-list { display: none; margin-top: 10px; }
.comments-list.open { display: block; }
.comment-item {
  background: var(--soft);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 6px;
  font-size: 0.82rem;
}
.comment-author { font-weight: 600; color: var(--ink); }
.comment-text { color: var(--muted); margin-top: 2px; }
.comment-form {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}
.comment-input {
  flex: 1;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  padding: 7px 10px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  outline: none;
  background: #fff;
}
.comment-input:focus { border-color: var(--ink); }
.comment-submit {
  background: var(--ink);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 7px 12px;
  font-size: 0.82rem;
  cursor: pointer;
}

/* ── CHECKOUT MODAL ── */
.modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(26,26,46,0.7);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  padding: 20px;
  backdrop-filter: blur(4px);
}
.modal-overlay.open { display: flex; }
.modal {
  background: #fff;
  border-radius: 20px;
  max-width: 480px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  animation: slideUp 0.3s ease;
}
@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to   { transform: translateY(0);    opacity: 1; }
}
.modal-header {
  padding: 24px 24px 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.modal-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--ink);
}
.modal-close {
  background: var(--soft);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.modal-body { padding: 16px 24px 24px; }

/* Order form */
.form-group { margin-bottom: 14px; }
.form-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 5px;
}
.form-input, .form-textarea, .form-select {
  width: 100%;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  outline: none;
  background: var(--paper);
  color: var(--ink);
  transition: border-color 0.2s;
}
.form-input:focus, .form-textarea:focus, .form-select:focus {
  border-color: var(--ink);
  background: #fff;
}
.form-textarea { resize: vertical; min-height: 70px; }

/* Payment section */
.payment-section {
  background: var(--soft);
  border-radius: 12px;
  padding: 16px;
  margin: 16px 0;
}
.payment-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.upi-box {
  background: #fff;
  border-radius: 10px;
  padding: 14px;
  text-align: center;
  margin-bottom: 12px;
  border: 1.5px solid var(--border);
}
.upi-qr-placeholder {
  width: 120px;
  height: 120px;
  margin: 0 auto 10px;
  background: var(--ink);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.75rem;
  text-align: center;
  padding: 8px;
  line-height: 1.4;
  /* REPLACE with your actual QR image:
     background: url('/public/image/upi-qr.webp') center/cover; */
}
.upi-id {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 4px;
}
.upi-note { font-size: 0.75rem; color: var(--muted); }

.bank-box {
  background: #fff;
  border-radius: 10px;
  padding: 12px 14px;
  border: 1.5px solid var(--border);
  font-size: 0.82rem;
}
.bank-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid var(--border);
}
.bank-row:last-child { border-bottom: none; }
.bank-label { color: var(--muted); }
.bank-value { font-weight: 600; color: var(--ink); }

.divider-or {
  text-align: center;
  color: var(--muted);
  font-size: 0.78rem;
  margin: 10px 0;
  position: relative;
}
.divider-or::before, .divider-or::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 42%;
  height: 1px;
  background: var(--border);
}
.divider-or::before { left: 0; }
.divider-or::after  { right: 0; }

.btn-submit-order {
  width: 100%;
  background: var(--ink);
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 14px;
  font-family: 'DM Sans', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  margin-top: 4px;
}
.btn-submit-order:hover { background: #2d2d4e; transform: scale(1.01); }

.btn-submit-wa {
  width: 100%;
  background: #25d366;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 14px;
  font-family: 'DM Sans', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-decoration: none;
}
.btn-submit-wa:hover { background: #1ebe5d; }

/* ── ADD PRODUCT (Admin) ── */
.admin-section {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px 60px;
}
.admin-toggle {
  background: none;
  border: 1.5px dashed var(--border);
  border-radius: 12px;
  padding: 14px 20px;
  width: 100%;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 16px;
}
.admin-toggle:hover { border-color: var(--ink); color: var(--ink); }
.admin-form {
  display: none;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}
.admin-form.open { display: block; }
.admin-form h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.2rem;
  margin-bottom: 16px;
  color: var(--ink);
}
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-grid .full { grid-column: 1 / -1; }
.admin-note {
  background: rgba(244,162,97,0.12);
  border-left: 3px solid var(--gold);
  border-radius: 0 8px 8px 0;
  padding: 10px 14px;
  font-size: 0.82rem;
  color: var(--ink);
  margin-top: 12px;
  line-height: 1.5;
}

/* ── TOAST ── */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%) translateY(80px);
  background: var(--ink);
  color: #fff;
  padding: 12px 24px;
  border-radius: 100px;
  font-size: 0.88rem;
  font-weight: 500;
  z-index: 9999;
  transition: transform 0.3s;
  white-space: nowrap;
}
.toast.show { transform: translateX(-50%) translateY(0); }

/* ── RESPONSIVE ── */
@media (max-width: 600px) {
  .products-grid { grid-template-columns: 1fr 1fr; gap: 14px; padding: 8px 12px 40px; }
  .filter-bar { padding: 16px 12px; }
  .admin-section { padding: 0 12px 40px; }
  .form-grid { grid-template-columns: 1fr; }
  .action-btns { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 400px) {
  .products-grid { grid-template-columns: 1fr; }
}
</style>

<div class="shop-wrap">

  <!-- HERO -->
  <div class="shop-hero">
    <h1>Amit's <span>Shop</span></h1>
    <p>Quality items — direct from Haridwar. No middlemen. No hidden fees.</p>
    <div class="shop-badges">
      <span class="shop-badge">✅ 100% Genuine</span>
      <span class="shop-badge">📦 Direct from Seller</span>
      <span class="shop-badge">💳 UPI / Bank Transfer</span>
      <span class="shop-badge">💬 Order on WhatsApp</span>
      <span class="shop-badge">🚫 No GST on Used Items</span>
    </div>
  </div>

  <!-- FILTER BAR -->
  <div class="filter-bar">
    <button class="filter-btn active" onclick="filterProducts('all', this)">All <span class="filter-count" id="count-all">0</span></button>
    <button class="filter-btn" onclick="filterProducts('electronics', this)">Electronics</button>
    <button class="filter-btn" onclick="filterProducts('books', this)">Books</button>
    <button class="filter-btn" onclick="filterProducts('home', this)">Home & Kitchen</button>
    <button class="filter-btn" onclick="filterProducts('clothing', this)">Clothing</button>
    <button class="filter-btn" onclick="filterProducts('other', this)">Other</button>
  </div>

  <!-- PRODUCTS GRID -->
  <div class="products-grid" id="productsGrid"></div>

  <!-- ADD PRODUCT (Admin) -->
  <div class="admin-section">
    <button class="admin-toggle" onclick="toggleAdmin()">＋ Add New Product (Admin Only)</button>
    <div class="admin-form" id="adminForm">
      <h3>Add New Product</h3>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Product Name *</label>
          <input class="form-input" id="ap-name" placeholder="e.g. Samsung Galaxy S21">
        </div>
        <div class="form-group">
          <label class="form-label">Category *</label>
          <select class="form-select" id="ap-category">
            <option value="electronics">Electronics</option>
            <option value="books">Books</option>
            <option value="home">Home & Kitchen</option>
            <option value="clothing">Clothing</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Selling Price (₹) *</label>
          <input class="form-input" id="ap-price" type="number" placeholder="e.g. 8500">
        </div>
        <div class="form-group">
          <label class="form-label">Original Price (₹)</label>
          <input class="form-input" id="ap-original" type="number" placeholder="e.g. 12000">
        </div>
        <div class="form-group full">
          <label class="form-label">Description *</label>
          <textarea class="form-textarea" id="ap-desc" placeholder="Describe condition, features, age..."></textarea>
        </div>
        <div class="form-group full">
          <label class="form-label">Image URL *</label>
          <input class="form-input" id="ap-img" placeholder="https://... or /public/image/product.jpg">
        </div>
        <div class="form-group">
          <label class="form-label">Condition</label>
          <select class="form-select" id="ap-condition">
            <option value="used">Used / Second Hand</option>
            <option value="new">New / Resale</option>
            <option value="refurbished">Refurbished</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Stock</label>
          <input class="form-input" id="ap-stock" type="number" placeholder="1" value="1">
        </div>
      </div>
      <div class="admin-note">
        💡 After adding, copy the generated product data and paste it into the <code>PRODUCTS</code> array in this file's script section — then commit to GitHub. Your product goes live automatically.
      </div>
      <button class="btn-submit-order" style="margin-top:16px" onclick="addProduct()">Add Product to Store</button>
    </div>
  </div>

</div>

<!-- ORDER MODAL -->
<div class="modal-overlay" id="orderModal">
  <div class="modal">
    <div class="modal-header">
      <div>
        <div class="modal-title" id="modalProductName">Order Product</div>
        <div style="font-size:0.85rem;color:var(--muted);margin-top:4px" id="modalProductPrice"></div>
      </div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">

      <div class="form-group">
        <label class="form-label">Your Name *</label>
        <input class="form-input" id="order-name" placeholder="Full name">
      </div>
      <div class="form-group">
        <label class="form-label">Phone / WhatsApp *</label>
        <input class="form-input" id="order-phone" placeholder="+91 9XXXXXXXXX" type="tel">
      </div>
      <div class="form-group">
        <label class="form-label">Email</label>
        <input class="form-input" id="order-email" placeholder="you@email.com" type="email">
      </div>
      <div class="form-group">
        <label class="form-label">Delivery Address *</label>
        <textarea class="form-textarea" id="order-address" placeholder="Full address with PIN code"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Message / Questions</label>
        <textarea class="form-textarea" id="order-message" placeholder="Any specific questions about the product?"></textarea>
      </div>

      <!-- PAYMENT -->
      <div class="payment-section">
        <div class="payment-title">💳 Payment Details</div>
        <div class="upi-box">
          <div class="upi-qr-placeholder">
            📱 Your UPI QR Code Here<br><small>Replace with actual QR image</small>
          </div>
          <div class="upi-id">UPI ID: amitk@upi</div>
          <div class="upi-note">Scan QR or pay to UPI ID above</div>
        </div>
        <div class="divider-or">or Bank Transfer</div>
        <div class="bank-box">
          <div class="bank-row"><span class="bank-label">Name</span><span class="bank-value">Amit Kumar</span></div>
          <div class="bank-row"><span class="bank-label">Bank</span><span class="bank-value">SBI / Your Bank</span></div>
          <div class="bank-row"><span class="bank-label">Account No</span><span class="bank-value">XXXXXXXXXXXX</span></div>
          <div class="bank-row"><span class="bank-label">IFSC</span><span class="bank-value">SBIN0XXXXXX</span></div>
        </div>
        <div style="font-size:0.78rem;color:var(--muted);margin-top:10px;text-align:center">
          After payment, share screenshot on WhatsApp for fast confirmation
        </div>
      </div>

      <button class="btn-submit-order" onclick="submitOrder('email')">📧 Send Order via Email</button>
      <a class="btn-submit-wa" id="waOrderBtn" href="#" onclick="submitOrder('whatsapp')" target="_blank">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        Order via WhatsApp
      </a>

    </div>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<script>
// ══════════════════════════════════════════════════════
// PRODUCTS DATA — Add your products here
// ══════════════════════════════════════════════════════
const PRODUCTS = [
  {
    id: 1,
    name: "Sample Electronics Item",
    category: "electronics",
    condition: "used",
    price: 4500,
    original: 8000,
    desc: "Good condition, fully working. Minor scratches on body. All accessories included.",
    img: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=300&fit=crop",
    stock: 1,
    ratings: [5, 4, 5],
    comments: [{ author: "Rahul", text: "Great product, fast response from seller!" }]
  },
  {
    id: 2,
    name: "Trading & Finance Books Set",
    category: "books",
    condition: "used",
    price: 800,
    original: 2200,
    desc: "Set of 5 trading books including Market Wizards, Reminiscences of a Stock Operator. Good condition.",
    img: "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400&h=300&fit=crop",
    stock: 1,
    ratings: [5],
    comments: []
  },
  {
    id: 3,
    name: "Home Decor Item",
    category: "home",
    condition: "new",
    price: 1200,
    original: 1800,
    desc: "Brand new, never used. Bought but didn't need. Original packaging.",
    img: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=300&fit=crop",
    stock: 2,
    ratings: [],
    comments: []
  }
];

// ══════════════════════════════════════════════════════
// CONFIG — Update these with your real details
// ══════════════════════════════════════════════════════
const CONFIG = {
  whatsapp: "919634759528",   // Your WhatsApp number with country code, no +
  email:    "admin@ai360trading.in",
  upiId:    "9634759528@upi",      // Your real UPI ID
  sellerName: "Amit Kumar",
  city: "Haridwar"
};

// ══════════════════════════════════════════════════════
// STATE
// ══════════════════════════════════════════════════════
let currentFilter = 'all';
let currentProduct = null;
let localProducts  = JSON.parse(localStorage.getItem('shop_products') || '[]');
let allProducts    = [...PRODUCTS, ...localProducts];
let localComments  = JSON.parse(localStorage.getItem('shop_comments') || '{}');
let localRatings   = JSON.parse(localStorage.getItem('shop_ratings')  || '{}');

function getAllProducts() {
  return allProducts.map(p => {
    const id = String(p.id);
    return {
      ...p,
      comments: [...(p.comments || []), ...(localComments[id] || [])],
      ratings:  [...(p.ratings  || []), ...(localRatings[id]  || [])],
    };
  });
}

// ══════════════════════════════════════════════════════
// RENDER
// ══════════════════════════════════════════════════════
function avgRating(ratings) {
  if (!ratings.length) return 0;
  return ratings.reduce((a,b) => a+b, 0) / ratings.length;
}
function starsHTML(avg) {
  const full = Math.round(avg);
  return ['★','★','★','★','★'].map((s,i) =>
    `<span style="color:${i < full ? 'var(--gold)' : 'var(--border)'}">${s}</span>`
  ).join('');
}

function renderProducts() {
  const grid = document.getElementById('productsGrid');
  const products = getAllProducts();
  const filtered = currentFilter === 'all' ? products : products.filter(p => p.category === currentFilter);

  document.getElementById('count-all').textContent = products.length;

  if (!filtered.length) {
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px 0;color:var(--muted)">No products in this category yet.</div>`;
    return;
  }

  grid.innerHTML = filtered.map(p => {
    const avg   = avgRating(p.ratings);
    const saved = p.original ? Math.round((1 - p.price/p.original)*100) : 0;
    const condLabel = p.condition === 'new' ? 'New' : p.condition === 'refurbished' ? 'Refurbished' : 'Used';
    const condClass = p.condition === 'new' ? 'new' : p.condition === 'refurbished' ? '' : 'used';
    const waMsg = encodeURIComponent(`Hi Amit, I'm interested in: ${p.name} (₹${p.price.toLocaleString('en-IN')})`);

    return `
    <div class="product-card" data-category="${p.category}" data-id="${p.id}">
      <div class="product-img-wrap">
        <img src="${p.img}" alt="${p.name}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">
        <span class="product-badge ${condClass}">${condLabel}</span>
        <button class="share-btn" onclick="shareProduct(${p.id})" title="Share">⬆</button>
      </div>
      <div class="product-body">
        <div class="product-category">${p.category}</div>
        <div class="product-name">${p.name}</div>
        <div class="product-desc">${p.desc}</div>

        <div class="rating-row">
          <span class="stars">${starsHTML(avg)}</span>
          <span class="rating-count">${avg ? avg.toFixed(1) : 'No ratings'} (${p.ratings.length})</span>
          <button onclick="toggleRating(${p.id})" style="background:none;border:none;font-size:0.75rem;color:var(--muted);cursor:pointer;margin-left:4px">Rate</button>
        </div>
        <div class="rating-input" id="rate-${p.id}">
          ${[1,2,3,4,5].map(n => `<button class="star-pick" onclick="submitRating(${p.id},${n})" title="${n} star">★</button>`).join('')}
        </div>

        <div class="price-row">
          <div>
            <div class="price">₹${p.price.toLocaleString('en-IN')}</div>
            ${p.original ? `<div class="price-original">₹${p.original.toLocaleString('en-IN')}</div>` : ''}
          </div>
          ${saved ? `<span class="price-save">Save ${saved}%</span>` : ''}
        </div>

        <div class="action-btns">
          <a class="btn-whatsapp" href="https://wa.me/${CONFIG.whatsapp}?text=${waMsg}" target="_blank">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            WhatsApp
          </a>
          <button class="btn-order" onclick="openOrder(${p.id})">
            🛒 Order Now
          </button>
        </div>
      </div>

      <div class="comments-section">
        <button class="comments-toggle" onclick="toggleComments(${p.id})">
          💬 ${p.comments.length} comment${p.comments.length !== 1 ? 's' : ''}
        </button>
        <div class="comments-list" id="comments-${p.id}">
          ${p.comments.map(c => `
            <div class="comment-item">
              <div class="comment-author">${c.author}</div>
              <div class="comment-text">${c.text}</div>
            </div>
          `).join('') || '<div style="font-size:0.8rem;color:var(--muted);padding:4px 0">No comments yet. Be first!</div>'}
          <div class="comment-form">
            <input class="comment-input" id="ci-name-${p.id}" placeholder="Your name">
            <input class="comment-input" id="ci-text-${p.id}" placeholder="Your comment" style="flex:2">
            <button class="comment-submit" onclick="addComment(${p.id})">Post</button>
          </div>
        </div>
      </div>
    </div>`;
  }).join('');
}

// ══════════════════════════════════════════════════════
// INTERACTIONS
// ══════════════════════════════════════════════════════
function filterProducts(cat, btn) {
  currentFilter = cat;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderProducts();
}

function toggleComments(id) {
  const el = document.getElementById(`comments-${id}`);
  el.classList.toggle('open');
}

function toggleRating(id) {
  const el = document.getElementById(`rate-${id}`);
  el.classList.toggle('show');
}

function submitRating(productId, stars) {
  const ratings = JSON.parse(localStorage.getItem('shop_ratings') || '{}');
  const id = String(productId);
  if (!ratings[id]) ratings[id] = [];
  ratings[id].push(stars);
  localStorage.setItem('shop_ratings', JSON.stringify(ratings));
  localRatings = ratings;
  showToast(`Thanks for your ${stars}★ rating!`);
  renderProducts();
}

function addComment(productId) {
  const nameEl = document.getElementById(`ci-name-${productId}`);
  const textEl = document.getElementById(`ci-text-${productId}`);
  const name = nameEl.value.trim();
  const text = textEl.value.trim();
  if (!name || !text) { showToast('Please enter name and comment'); return; }
  const comments = JSON.parse(localStorage.getItem('shop_comments') || '{}');
  const id = String(productId);
  if (!comments[id]) comments[id] = [];
  comments[id].push({ author: name, text });
  localStorage.setItem('shop_comments', JSON.stringify(comments));
  localComments = comments;
  nameEl.value = '';
  textEl.value = '';
  showToast('Comment added!');
  renderProducts();
  setTimeout(() => {
    const el = document.getElementById(`comments-${productId}`);
    if (el) el.classList.add('open');
  }, 100);
}

function shareProduct(productId) {
  const p = getAllProducts().find(x => x.id === productId);
  const url = `${window.location.origin}/shop/#product-${productId}`;
  const text = `Check out: ${p.name} for ₹${p.price.toLocaleString('en-IN')} on Amit's Shop — ${url}`;
  if (navigator.share) {
    navigator.share({ title: p.name, text, url });
  } else {
    navigator.clipboard.writeText(text).then(() => showToast('Link copied to clipboard!'));
  }
}

// ══════════════════════════════════════════════════════
// ORDER MODAL
// ══════════════════════════════════════════════════════
function openOrder(productId) {
  currentProduct = getAllProducts().find(p => p.id === productId);
  document.getElementById('modalProductName').textContent = currentProduct.name;
  document.getElementById('modalProductPrice').textContent = `₹${currentProduct.price.toLocaleString('en-IN')}`;
  document.getElementById('orderModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  document.getElementById('orderModal').classList.remove('open');
  document.body.style.overflow = '';
}
document.getElementById('orderModal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

function submitOrder(method) {
  const name    = document.getElementById('order-name').value.trim();
  const phone   = document.getElementById('order-phone').value.trim();
  const address = document.getElementById('order-address').value.trim();
  if (!name || !phone || !address) { showToast('Please fill Name, Phone and Address'); return; }

  const msg = `🛒 *New Order — AI360Trading Shop*

*Product:* ${currentProduct.name}
*Price:* ₹${currentProduct.price.toLocaleString('en-IN')}
*Name:* ${name}
*Phone:* ${phone}
*Email:* ${document.getElementById('order-email').value || 'Not provided'}
*Address:* ${address}
*Message:* ${document.getElementById('order-message').value || 'None'}

_Payment: UPI/Bank transfer. Screenshot to confirm._`;

  if (method === 'whatsapp') {
    const waUrl = `https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(msg)}`;
    window.open(waUrl, '_blank');
    showToast('Opening WhatsApp...');
  } else {
    const subject = encodeURIComponent(`Order: ${currentProduct.name}`);
    const body    = encodeURIComponent(msg);
    window.location.href = `mailto:${CONFIG.email}?subject=${subject}&body=${body}`;
    showToast('Opening email client...');
  }
  closeModal();
}

// ══════════════════════════════════════════════════════
// ADD PRODUCT (Admin)
// ══════════════════════════════════════════════════════
function toggleAdmin() {
  document.getElementById('adminForm').classList.toggle('open');
}

function addProduct() {
  const name  = document.getElementById('ap-name').value.trim();
  const price = parseInt(document.getElementById('ap-price').value);
  const desc  = document.getElementById('ap-desc').value.trim();
  const img   = document.getElementById('ap-img').value.trim();
  if (!name || !price || !desc || !img) { showToast('Please fill all required fields'); return; }

  const newProduct = {
    id: Date.now(),
    name,
    category:  document.getElementById('ap-category').value,
    condition: document.getElementById('ap-condition').value,
    price,
    original:  parseInt(document.getElementById('ap-original').value) || 0,
    desc,
    img,
    stock:    parseInt(document.getElementById('ap-stock').value) || 1,
    ratings:  [],
    comments: []
  };

  const saved = JSON.parse(localStorage.getItem('shop_products') || '[]');
  saved.push(newProduct);
  localStorage.setItem('shop_products', JSON.stringify(saved));
  localProducts = saved;
  allProducts = [...PRODUCTS, ...localProducts];

  // Show copy-paste data for permanent addition
  console.log('Add this to PRODUCTS array:\n', JSON.stringify(newProduct, null, 2));
  showToast(`✅ "${name}" added! Check console for permanent code.`);
  renderProducts();
  document.getElementById('adminForm').classList.remove('open');
}

// ══════════════════════════════════════════════════════
// TOAST
// ══════════════════════════════════════════════════════
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

// INIT
renderProducts();
</script>
