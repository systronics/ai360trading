---
layout: default
title: "Shop — Amit's Store"
permalink: /shop/
description: "Buy unique items from Amit Kumar, Haridwar. Order via WhatsApp or Email. Pay via UPI. Traditional art, collectibles and more."
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--ink:#1a1a2e;--paper:#faf8f3;--accent:#e63946;--gold:#f4a261;--soft:#f1ede4;--border:#e0d9cc;--muted:#7a7065;--green:#2a9d5c;--shadow:0 4px 24px rgba(26,26,46,0.10);--shadow-lg:0 12px 48px rgba(26,26,46,0.16)}
*{box-sizing:border-box;margin:0;padding:0}
.shop-wrap{background:var(--paper);font-family:'DM Sans',sans-serif;color:var(--ink);min-height:100vh}
.shop-hero{background:var(--ink);padding:32px 20px 28px;text-align:center;position:relative;overflow:hidden}
.shop-hero::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(45deg,transparent,transparent 40px,rgba(244,162,97,0.04) 40px,rgba(244,162,97,0.04) 80px)}
.shop-hero h1{font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,3.5rem);color:#fff;position:relative;line-height:1.1}
.shop-hero h1 span{color:var(--gold)}
.shop-hero p{color:rgba(255,255,255,0.65);margin-top:12px;font-size:1rem;position:relative}
.shop-badges{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-top:14px;position:relative}
.shop-badge{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:rgba(255,255,255,0.85);padding:5px 11px;border-radius:100px;font-size:0.72rem;font-weight:500}
.filter-bar{display:flex;gap:8px;padding:20px 24px;flex-wrap:wrap;max-width:1100px;margin:0 auto}
.filter-btn{padding:8px 18px;border-radius:100px;border:1.5px solid var(--border);background:#fff;color:var(--muted);font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:500;cursor:pointer;transition:all 0.2s}
.filter-btn:hover,.filter-btn.active{background:var(--ink);color:#fff;border-color:var(--ink)}
.filter-count{background:var(--accent);color:#fff;border-radius:100px;padding:1px 7px;font-size:0.72rem;margin-left:4px}
.products-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:24px;padding:8px 24px 48px;max-width:1100px;margin:0 auto}
.product-card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:var(--shadow);transition:transform 0.25s,box-shadow 0.25s;position:relative;display:flex;flex-direction:column}
.product-card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg)}
.product-img-wrap{position:relative;background:var(--soft);aspect-ratio:3/4;overflow:hidden}
.product-img-wrap img{width:100%;height:100%;object-fit:cover;transition:transform 0.4s;display:none}
.product-img-wrap img.active{display:block}
.product-card:hover .product-img-wrap img.active{transform:scale(1.03)}
.img-dots{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:5px;z-index:2}
.img-dot{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,0.5);border:none;cursor:pointer;transition:background 0.2s;padding:0}
.img-dot.active{background:#fff}
.img-prev,.img-next{position:absolute;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.85);border:none;border-radius:50%;width:30px;height:30px;cursor:pointer;font-size:0.9rem;display:flex;align-items:center;justify-content:center;z-index:2;opacity:0;transition:opacity 0.2s}
.product-img-wrap:hover .img-prev,.product-img-wrap:hover .img-next{opacity:1}
.img-prev{left:8px}.img-next{right:8px}
.product-badge{position:absolute;top:12px;left:12px;background:var(--accent);color:#fff;font-size:0.72rem;font-weight:600;padding:4px 10px;border-radius:100px;letter-spacing:0.04em;text-transform:uppercase;z-index:2}
.product-badge.used{background:var(--gold);color:var(--ink)}.product-badge.new{background:var(--green)}
.share-btn{position:absolute;top:12px;right:12px;background:rgba(255,255,255,0.92);border:none;border-radius:50%;width:34px;height:34px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.12);transition:transform 0.2s;z-index:2}
.share-btn:hover{transform:scale(1.12)}
.sold-out-overlay{position:absolute;inset:0;background:rgba(26,26,46,0.6);display:flex;align-items:center;justify-content:center;z-index:3}
.sold-out-label{background:var(--accent);color:#fff;font-weight:700;font-size:1.1rem;padding:8px 24px;border-radius:100px}
.product-body{padding:16px 18px 12px;flex:1;display:flex;flex-direction:column}
.product-category{font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.product-name{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--ink);line-height:1.3;margin-bottom:8px}
.product-desc{font-size:0.85rem;color:var(--muted);line-height:1.5;flex:1;margin-bottom:12px}
.rating-row{display:flex;align-items:center;gap:6px;margin-bottom:12px}
.stars{font-size:0.9rem;letter-spacing:1px}
.rating-count{font-size:0.78rem;color:var(--muted)}
.rating-input{display:none;gap:4px}.rating-input.show{display:flex}
.star-pick{background:none;border:none;font-size:1.2rem;cursor:pointer;color:var(--border);transition:color 0.15s}
.star-pick:hover,.star-pick.lit{color:var(--gold)}
.price-row{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:14px}
.price{font-family:'Playfair Display',serif;font-size:1.45rem;font-weight:900;color:var(--ink)}
.price-original{font-size:0.85rem;color:var(--muted);text-decoration:line-through}
.price-save{font-size:0.78rem;color:var(--green);font-weight:600;background:rgba(42,157,92,0.1);padding:3px 8px;border-radius:100px}
.action-btns{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.btn-whatsapp{background:#25d366;color:#fff;border:none;border-radius:10px;padding:11px 8px;font-family:'DM Sans',sans-serif;font-size:0.82rem;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:5px;transition:background 0.2s;text-decoration:none}
.btn-whatsapp:hover{background:#1ebe5d}
.btn-order{background:var(--ink);color:#fff;border:none;border-radius:10px;padding:11px 8px;font-family:'DM Sans',sans-serif;font-size:0.82rem;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:5px;transition:background 0.2s}
.btn-order:hover{background:#2d2d4e}
.comments-section{border-top:1px solid var(--border);padding:12px 18px 16px}
.comments-toggle{background:none;border:none;font-family:'DM Sans',sans-serif;font-size:0.82rem;color:var(--muted);cursor:pointer;padding:0;display:flex;align-items:center;gap:5px}
.comments-toggle:hover{color:var(--ink)}
.comments-list{display:none;margin-top:10px}.comments-list.open{display:block}
.comment-item{background:var(--soft);border-radius:8px;padding:8px 12px;margin-bottom:6px;font-size:0.82rem}
.comment-author{font-weight:600;color:var(--ink)}.comment-text{color:var(--muted);margin-top:2px}
.comment-form{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.comment-input{flex:1;min-width:80px;border:1.5px solid var(--border);border-radius:8px;padding:7px 10px;font-family:'DM Sans',sans-serif;font-size:0.82rem;outline:none;background:#fff}
.comment-input:focus{border-color:var(--ink)}
.comment-submit{background:var(--ink);color:#fff;border:none;border-radius:8px;padding:7px 12px;font-size:0.82rem;cursor:pointer}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(26,26,46,0.7);z-index:1000;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px)}
.modal-overlay.open{display:flex}
.modal{background:#fff;border-radius:20px;max-width:480px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:var(--shadow-lg);animation:slideUp 0.3s ease}
@keyframes slideUp{from{transform:translateY(30px);opacity:0}to{transform:translateY(0);opacity:1}}
.modal-header{padding:24px 24px 0;display:flex;justify-content:space-between;align-items:flex-start}
.modal-title{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:var(--ink)}
.modal-close{background:var(--soft);border:none;border-radius:50%;width:32px;height:32px;font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.modal-body{padding:16px 24px 24px}
.form-group{margin-bottom:14px}
.form-label{display:block;font-size:0.82rem;font-weight:600;color:var(--ink);margin-bottom:5px}
.form-input,.form-textarea,.form-select{width:100%;border:1.5px solid var(--border);border-radius:10px;padding:10px 12px;font-family:'DM Sans',sans-serif;font-size:0.9rem;outline:none;background:var(--paper);color:var(--ink);transition:border-color 0.2s}
.form-input:focus,.form-textarea:focus{border-color:var(--ink);background:#fff}
.form-textarea{resize:vertical;min-height:70px}
.payment-section{background:var(--soft);border-radius:12px;padding:16px;margin:16px 0}
.payment-title{font-size:0.85rem;font-weight:700;color:var(--ink);margin-bottom:12px}
.upi-box{background:#fff;border-radius:10px;padding:14px;text-align:center;margin-bottom:12px;border:1.5px solid var(--border)}
.upi-id{font-size:0.9rem;font-weight:700;color:var(--ink);margin-bottom:3px}
.upi-note{font-size:0.75rem;color:var(--muted)}
.bank-box{background:#fff;border-radius:10px;padding:12px 14px;border:1.5px solid var(--border);font-size:0.82rem}
.bank-row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border)}
.bank-row:last-child{border-bottom:none}
.bank-label{color:var(--muted)}.bank-value{font-weight:600;color:var(--ink)}
.divider-or{text-align:center;color:var(--muted);font-size:0.78rem;margin:10px 0;position:relative}
.divider-or::before,.divider-or::after{content:'';position:absolute;top:50%;width:42%;height:1px;background:var(--border)}
.divider-or::before{left:0}.divider-or::after{right:0}
.btn-submit-order{width:100%;background:var(--ink);color:#fff;border:none;border-radius:12px;padding:14px;font-family:'DM Sans',sans-serif;font-size:1rem;font-weight:600;cursor:pointer;transition:background 0.2s;margin-top:4px}
.btn-submit-order:hover{background:#2d2d4e}
.btn-submit-wa{width:100%;background:#25d366;color:#fff;border:none;border-radius:12px;padding:14px;font-family:'DM Sans',sans-serif;font-size:1rem;font-weight:600;cursor:pointer;transition:background 0.2s;margin-top:8px;display:flex;align-items:center;justify-content:center;gap:8px;text-decoration:none}
.btn-submit-wa:hover{background:#1ebe5d}
.admin-section{max-width:1100px;margin:0 auto;padding:0 24px 60px}
.admin-toggle{background:none;border:1.5px dashed var(--border);border-radius:12px;padding:14px 20px;width:100%;font-family:'DM Sans',sans-serif;font-size:0.9rem;color:var(--muted);cursor:pointer;transition:all 0.2s;margin-bottom:16px}
.admin-toggle:hover{border-color:var(--ink);color:var(--ink)}
.admin-form{display:none;background:#fff;border-radius:16px;padding:24px;box-shadow:var(--shadow);margin-bottom:16px}
.admin-form.open{display:block}
.admin-form h3{font-family:'Playfair Display',serif;font-size:1.2rem;margin-bottom:16px;color:var(--ink)}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.form-grid .full{grid-column:1/-1}
.admin-note{background:rgba(244,162,97,0.12);border-left:3px solid var(--gold);border-radius:0 8px 8px 0;padding:10px 14px;font-size:0.82rem;color:var(--ink);margin-top:12px;line-height:1.5}
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--ink);color:#fff;padding:12px 24px;border-radius:100px;font-size:0.88rem;font-weight:500;z-index:9999;transition:transform 0.3s;white-space:nowrap}
.toast.show{transform:translateX(-50%) translateY(0)}
/* Hide site main header on shop page only — exact class from default.html */
.header-container { display: none !important; }
/* Remove content-wrapper padding that would create gap above shop hero */
.content-wrapper { padding-top: 0 !important; margin-top: 0 !important; }
body { padding-top: 0 !important; margin-top: 0 !important; }
.shop-hero { margin-top: 0; }
.shop-topnav{background:#fff;border-bottom:1px solid var(--border);padding:9px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:6px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(26,26,46,0.06)}
.shop-topnav-left{display:flex;align-items:center;gap:6px}
.btn-home{display:flex;align-items:center;gap:5px;text-decoration:none;color:var(--ink);font-size:0.82rem;font-weight:700;padding:6px 12px;border-radius:8px;background:var(--soft);border:1.5px solid var(--border);transition:all 0.2s;white-space:nowrap}
.btn-home:hover{background:var(--ink);color:#fff;border-color:var(--ink)}
.topnav-links{display:flex;align-items:center;gap:2px}
.topnav-link{text-decoration:none;color:var(--muted);font-size:0.75rem;font-weight:600;padding:5px 8px;border-radius:6px;transition:all 0.2s;text-transform:uppercase;letter-spacing:0.03em;white-space:nowrap}
.topnav-link:hover{color:var(--ink);background:var(--soft)}
.topnav-brand{font-family:"Playfair Display",serif;font-size:0.88rem;font-weight:700;color:var(--muted)}
@media(max-width:480px){.topnav-links{display:none}.shop-topnav{padding:8px 14px}}
@media(max-width:600px){.products-grid{grid-template-columns:1fr 1fr;gap:14px;padding:8px 12px 40px}.filter-bar{padding:16px 12px}.admin-section{padding:0 12px 40px}.form-grid{grid-template-columns:1fr}}
@media(max-width:400px){.products-grid{grid-template-columns:1fr}}
</style>

<div class="shop-wrap">

  <!-- BACK NAV — sticky top bar with home + links -->
  <div class="shop-topnav">
    <div class="shop-topnav-left">
      <a href="/" class="btn-home">&#8592; Home</a>
      <span class="topnav-brand" style="margin-left:8px">AI360Trading</span>
    </div>
    <div class="topnav-links">
      <a href="/about/" class="topnav-link">About</a>
      <a href="/contact/" class="topnav-link">Contact</a>
      <a href="/disclaimer/" class="topnav-link">Disclaimer</a>
      <a href="/policy/" class="topnav-link">Policy</a>
    </div>
  </div>

  <div class="shop-hero">
    <h1>Amit's <span>Shop</span></h1>
    <p>Unique items from Haridwar — direct from seller, no middlemen</p>
    <div class="shop-badges">
      <span class="shop-badge">✅ 100% Genuine</span>
      <span class="shop-badge">📦 Ships from Haridwar</span>
      <span class="shop-badge">💳 UPI / Bank Transfer</span>
      <span class="shop-badge">💬 Order on WhatsApp</span>
      <span class="shop-badge">🚫 No GST on Used Items</span>
    </div>
  </div>
  <div class="filter-bar">
    <button class="filter-btn active" onclick="filterProducts('all',this)">All <span class="filter-count" id="count-all">0</span></button>
    <button class="filter-btn" onclick="filterProducts('art',this)">Art &amp; Collectibles</button>
    <button class="filter-btn" onclick="filterProducts('electronics',this)">Electronics</button>
    <button class="filter-btn" onclick="filterProducts('books',this)">Books</button>
    <button class="filter-btn" onclick="filterProducts('home',this)">Home &amp; Decor</button>
    <button class="filter-btn" onclick="filterProducts('other',this)">Other</button>
  </div>
  <div class="products-grid" id="productsGrid"></div>

</div>

<div class="modal-overlay" id="orderModal">
  <div class="modal">
    <div class="modal-header">
      <div><div class="modal-title" id="modalProductName">Order</div><div style="font-size:0.85rem;color:var(--muted);margin-top:4px" id="modalProductPrice"></div></div>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-group"><label class="form-label">Your Name *</label><input class="form-input" id="order-name" placeholder="Full name"></div>
      <div class="form-group"><label class="form-label">Phone / WhatsApp *</label><input class="form-input" id="order-phone" placeholder="+91 XXXXXXXXXX" type="tel"></div>
      <div class="form-group"><label class="form-label">Email</label><input class="form-input" id="order-email" placeholder="you@email.com" type="email"></div>
      <div class="form-group"><label class="form-label">Street Address *</label><input class="form-input" id="order-street" placeholder="House No, Street, Area / Colony"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="form-group"><label class="form-label">City *</label><input class="form-input" id="order-city" placeholder="e.g. Haridwar"></div>
        <div class="form-group"><label class="form-label">PIN Code *</label><input class="form-input" id="order-pin" placeholder="e.g. 249401" type="number" maxlength="6"></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="form-group"><label class="form-label">State *</label><select class="form-select" id="order-state">
          <option value="">Select State</option>
          <option>Andhra Pradesh</option><option>Arunachal Pradesh</option><option>Assam</option>
          <option>Bihar</option><option>Chhattisgarh</option><option>Goa</option><option>Gujarat</option>
          <option>Haryana</option><option>Himachal Pradesh</option><option>Jharkhand</option>
          <option>Karnataka</option><option>Kerala</option><option>Madhya Pradesh</option>
          <option>Maharashtra</option><option>Manipur</option><option>Meghalaya</option>
          <option>Mizoram</option><option>Nagaland</option><option>Odisha</option><option>Punjab</option>
          <option>Rajasthan</option><option>Sikkim</option><option>Tamil Nadu</option>
          <option>Telangana</option><option>Tripura</option><option selected>Uttarakhand</option>
          <option>Uttar Pradesh</option><option>West Bengal</option>
          <option>Delhi</option><option>Jammu and Kashmir</option><option>Ladakh</option>
          <option>Chandigarh</option><option>Puducherry</option>
        </select></div>
        <div class="form-group"><label class="form-label">Landmark</label><input class="form-input" id="order-landmark" placeholder="Near school, temple..."></div>
      </div>
      <div class="form-group"><label class="form-label">Message / Questions</label><textarea class="form-textarea" id="order-message" placeholder="Any questions about this item?"></textarea></div>
      <div style="background:var(--soft);border-radius:14px;padding:18px;margin:16px 0">
        <!-- Step indicator -->
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px">
          <div style="background:var(--ink);color:#fff;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;flex-shrink:0">2</div>
          <div style="font-size:0.85rem;font-weight:700;color:var(--ink)">Pay via UPI</div>
        </div>

        <!-- UPI App buttons -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:12px">
          <a href="#" onclick="return triggerUpiPay(event,'gpay')" style="display:flex;flex-direction:column;align-items:center;gap:4px;background:#fff;border:1.5px solid var(--border);border-radius:10px;padding:10px 6px;text-decoration:none;transition:all 0.2s" onmouseover="this.style.borderColor='var(--ink)'" onmouseout="this.style.borderColor='var(--border)'">
            <span style="font-size:1.4rem">🟢</span>
            <span style="font-size:0.72rem;font-weight:700;color:var(--ink)">GPay</span>
          </a>
          <a href="#" onclick="return triggerUpiPay(event,'phonepe')" style="display:flex;flex-direction:column;align-items:center;gap:4px;background:#fff;border:1.5px solid var(--border);border-radius:10px;padding:10px 6px;text-decoration:none;transition:all 0.2s" onmouseover="this.style.borderColor='var(--ink)'" onmouseout="this.style.borderColor='var(--border)'">
            <span style="font-size:1.4rem">🟣</span>
            <span style="font-size:0.72rem;font-weight:700;color:var(--ink)">PhonePe</span>
          </a>
          <a href="#" onclick="return triggerUpiPay(event,'paytm')" style="display:flex;flex-direction:column;align-items:center;gap:4px;background:#fff;border:1.5px solid var(--border);border-radius:10px;padding:10px 6px;text-decoration:none;transition:all 0.2s" onmouseover="this.style.borderColor='var(--ink)'" onmouseout="this.style.borderColor='var(--border)'">
            <span style="font-size:1.4rem">🔵</span>
            <span style="font-size:0.72rem;font-weight:700;color:var(--ink)">Paytm</span>
          </a>
        </div>

        <!-- Amount display -->
        <div id="payAmountBox" style="background:#fff;border-radius:10px;padding:10px 14px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;border:1.5px solid var(--border)">
          <span style="font-size:0.82rem;color:var(--muted)">Amount to pay</span>
          <span id="payAmountDisplay" style="font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:900;color:var(--ink)">Rs.20</span>
        </div>

        <!-- UPI ID copy -->
        <div style="background:#fff;border-radius:10px;padding:10px 14px;border:1.5px solid var(--border)">
          <div style="font-size:0.72rem;color:var(--muted);margin-bottom:4px">UPI ID (to pay manually)</div>
          <div style="display:flex;align-items:center;justify-content:space-between;gap:8px">
            <div id="modalUpiId" style="font-size:0.95rem;font-weight:700;color:var(--ink);letter-spacing:0.02em">9634759528@upi</div>
            <button onclick="copyUpi()" style="background:var(--soft);border:1.5px solid var(--border);border-radius:8px;padding:5px 12px;font-size:0.78rem;font-weight:600;cursor:pointer;color:var(--ink);white-space:nowrap;flex-shrink:0">📋 Copy</button>
          </div>
        </div>

        <div style="font-size:0.72rem;color:var(--muted);margin-top:10px;text-align:center;line-height:1.5">
          After paying — send payment screenshot on WhatsApp to confirm your order
        </div>
      </div>

      <button class="btn-submit-order" onclick="submitOrder('email')">📧 Send Order via Email</button>
      <a class="btn-submit-wa" id="waOrderBtn" href="#" onclick="submitOrder('whatsapp')" target="_blank">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        Confirm Order via WhatsApp
      </a>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const CONFIG = {
  whatsapp:   "919634759528",
  email:      "admin@ai360trading.in",
  upiId:      "9634759528@upi",
  sellerName: "Amit Kumar",
  city:       "Haridwar, Uttarakhand"
};

// UPI DEEP LINK — opens GPay/PhonePe/Paytm with amount pre-filled
function triggerUpiPay(e, app) {
  e.preventDefault();
  if (!currentProduct) return false;
  const upiUrl = "upi://pay?pa="+CONFIG.upiId+"&pn="+encodeURIComponent(CONFIG.sellerName)+"&am="+currentProduct.price+"&cu=INR&tn="+encodeURIComponent("Order: "+currentProduct.name);
  window.location.href = upiUrl;
  setTimeout(()=>{ showToast("If app did not open — copy UPI ID: "+CONFIG.upiId); }, 2000);
  return false;
}
function copyUpi() {
  navigator.clipboard.writeText(CONFIG.upiId)
    .then(() => showToast("UPI ID copied: " + CONFIG.upiId))
    .catch(() => showToast("UPI ID: " + CONFIG.upiId));
}

// YOUR PRODUCTS — painting1.jpg, painting2.jpg, painting3.jpg go in /public/image/
const PRODUCTS = [
  {
    id: 1,
    name: "Traditional Indian Beaded Art — Lady with Golden Deer",
    category: "art",
    condition: "used",
    price: 20,
    original: 100,
    stock: 1,
    desc: "Rare vintage Indian folk art. Hand-embroidered with golden zari thread, studded with decorative beads and stones. Lady with golden deer motif in classic red and gold on dark background. Approx 24x36 inch. Perfect for home, office or gifting. Ships from Haridwar.",
    imgs: ["/public/image/painting1.jpg","/public/image/painting2.jpg","/public/image/painting3.jpg"],
    ratings: [],
    comments: []
  }
];

let currentFilter="all",currentProduct=null;
let localProducts=JSON.parse(localStorage.getItem("shop_products")||"[]");
let allProducts=[...PRODUCTS,...localProducts];
let localComments=JSON.parse(localStorage.getItem("shop_comments")||"{}");
let localRatings=JSON.parse(localStorage.getItem("shop_ratings")||"{}");
let imgIndexes={};

function getAllProducts(){
  const soldItems=JSON.parse(localStorage.getItem("shop_sold")||"{}");
  return allProducts.map(p=>({
    ...p,
    stock:Math.max(0,(p.stock||1)-(soldItems[String(p.id)]||0)),
    comments:[...(p.comments||[]),...(localComments[String(p.id)]||[])],
    ratings:[...(p.ratings||[]),...(localRatings[String(p.id)]||[])],
  }));
}
function avgRating(r){return r.length?r.reduce((a,b)=>a+b,0)/r.length:0;}
function starsHTML(avg){return[1,2,3,4,5].map(i=>`<span style="color:${i<=Math.round(avg)?"var(--gold)":"var(--border)"}">★</span>`).join("");}

function renderProducts(){
  const grid=document.getElementById("productsGrid");
  const all=getAllProducts();
  const list=currentFilter==="all"?all:all.filter(p=>p.category===currentFilter);
  document.getElementById("count-all").textContent=all.length;
  if(!list.length){grid.innerHTML=`<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--muted)">No products in this category yet.</div>`;return;}
  grid.innerHTML=list.map(p=>{
    const imgs=p.imgs||[p.img];
    const idx=imgIndexes[p.id]||0;
    const avg=avgRating(p.ratings);
    const saved=p.original?Math.round((1-p.price/p.original)*100):0;
    const cLabel={used:"Vintage",new:"New",refurbished:"Refurbished"}[p.condition]||p.condition;
    const cClass=p.condition==="new"?"new":p.condition==="refurbished"?"":"used";
    const waMsg=encodeURIComponent(`Hi Amit, I am interested in: ${p.name} (Rs.${p.price.toLocaleString("en-IN")}). Please share details.`);
    const soldOut=p.stock<1;
    return`<div class="product-card" data-id="${p.id}">
      <div class="product-img-wrap">
        ${imgs.map((src,i)=>`<img src="${src}" alt="${p.name} photo ${i+1}" loading="lazy" class="${i===idx?"active":""}" onerror="this.src='https://via.placeholder.com/400x530?text=Photo+${i+1}'">`).join("")}
        ${imgs.length>1?`<button class="img-prev" onclick="changeImg(${p.id},-1,event)">&#8249;</button><button class="img-next" onclick="changeImg(${p.id},1,event)">&#8250;</button><div class="img-dots">${imgs.map((_,i)=>`<button class="img-dot ${i===idx?"active":""}" onclick="setImg(${p.id},${i},event)"></button>`).join("")}</div>`:""}
        <span class="product-badge ${cClass}">${cLabel}</span>
        <button class="share-btn" onclick="shareProduct(${p.id},event)" title="Share">&#8679;</button>
        ${soldOut?`<div class="sold-out-overlay"><span class="sold-out-label">SOLD OUT</span></div>`:""}
      </div>
      <div class="product-body">
        <div class="product-category">${p.category}</div>
        <div class="product-name">${p.name}</div>
        <div class="product-desc">${p.desc}</div>
        <div class="rating-row">
          <span class="stars">${starsHTML(avg)}</span>
          <span class="rating-count">${avg?avg.toFixed(1)+" / 5":"No ratings yet"} (${p.ratings.length})</span>
          <button onclick="toggleRating(${p.id})" style="background:none;border:none;font-size:0.75rem;color:var(--muted);cursor:pointer;margin-left:4px">Rate</button>
        </div>
        <div class="rating-input" id="rate-${p.id}">${[1,2,3,4,5].map(n=>`<button class="star-pick" onclick="submitRating(${p.id},${n})">${n}&#9733;</button>`).join("")}</div>
        <div class="price-row">
          <div><div class="price">Rs.${p.price.toLocaleString("en-IN")}</div>${p.original?`<div class="price-original">Rs.${p.original.toLocaleString("en-IN")}</div>`:""}</div>
          ${saved?`<span class="price-save">Save ${saved}%</span>`:""}
        </div>
        <div class="action-btns">
          <a class="btn-whatsapp" href="https://wa.me/${CONFIG.whatsapp}?text=${waMsg}" target="_blank">WhatsApp</a>
          <button class="btn-order" onclick="openOrder(${p.id})" ${soldOut?'disabled style="opacity:0.5;cursor:not-allowed"':""}>Order Now</button>
        </div>
      </div>
      <div class="comments-section">
        <button class="comments-toggle" onclick="toggleComments(${p.id})">Comments (${p.comments.length})</button>
        <div class="comments-list" id="comments-${p.id}">
          ${p.comments.length?p.comments.map(c=>`<div class="comment-item"><div class="comment-author">${c.author}</div><div class="comment-text">${c.text}</div></div>`).join(""):`<div style="font-size:0.8rem;color:var(--muted);padding:4px 0">No comments yet — be first!</div>`}
          <div class="comment-form">
            <input class="comment-input" id="ci-name-${p.id}" placeholder="Name" style="max-width:90px">
            <input class="comment-input" id="ci-text-${p.id}" placeholder="Write a comment..." style="flex:2">
            <button class="comment-submit" onclick="addComment(${p.id})">Post</button>
          </div>
        </div>
      </div>
    </div>`;
  }).join("");
}

function changeImg(id,dir,e){e.stopPropagation();const p=getAllProducts().find(x=>x.id===id);const imgs=p.imgs||[p.img];imgIndexes[id]=((imgIndexes[id]||0)+dir+imgs.length)%imgs.length;renderProducts();}
function setImg(id,idx,e){e.stopPropagation();imgIndexes[id]=idx;renderProducts();}
function filterProducts(cat,btn){currentFilter=cat;document.querySelectorAll(".filter-btn").forEach(b=>b.classList.remove("active"));btn.classList.add("active");renderProducts();}
function toggleComments(id){document.getElementById(`comments-${id}`).classList.toggle("open");}
function toggleRating(id){document.getElementById(`rate-${id}`).classList.toggle("show");}
function submitRating(productId,stars){const r=JSON.parse(localStorage.getItem("shop_ratings")||"{}");const id=String(productId);if(!r[id])r[id]=[];r[id].push(stars);localStorage.setItem("shop_ratings",JSON.stringify(r));localRatings=r;showToast(`Thanks for your ${stars} star rating!`);renderProducts();}
function addComment(productId){const name=document.getElementById(`ci-name-${productId}`).value.trim();const text=document.getElementById(`ci-text-${productId}`).value.trim();if(!name||!text){showToast("Please enter name and comment");return;}const c=JSON.parse(localStorage.getItem("shop_comments")||"{}");const id=String(productId);if(!c[id])c[id]=[];c[id].push({author:name,text});localStorage.setItem("shop_comments",JSON.stringify(c));localComments=c;document.getElementById(`ci-name-${productId}`).value="";document.getElementById(`ci-text-${productId}`).value="";showToast("Comment posted!");renderProducts();setTimeout(()=>{const el=document.getElementById(`comments-${productId}`);if(el)el.classList.add("open");},100);}
function shareProduct(productId,e){if(e)e.stopPropagation();const p=getAllProducts().find(x=>x.id===productId);const url=`${window.location.origin}/shop/`;const txt=`Check this out: ${p.name} for Rs.${p.price.toLocaleString("en-IN")} — ${CONFIG.city}. ${url}`;if(navigator.share){navigator.share({title:p.name,text:txt,url});}else{navigator.clipboard.writeText(txt).then(()=>showToast("Link copied!"));}}
function openOrder(productId){
  currentProduct=getAllProducts().find(p=>p.id===productId);
  if(!currentProduct||currentProduct.stock<1){showToast("Sorry, this item is sold out!");return;}
  document.getElementById("modalProductName").textContent=currentProduct.name;
  document.getElementById("modalProductPrice").textContent="Rs."+currentProduct.price.toLocaleString("en-IN")+" — Fill details then pay";
  const amtEl=document.getElementById("payAmountDisplay");
  if(amtEl) amtEl.textContent="Rs."+currentProduct.price.toLocaleString("en-IN");
  document.getElementById("modalUpiId").textContent=CONFIG.upiId;
  ["order-name","order-phone","order-email","order-street","order-city","order-pin","order-state","order-landmark","order-message"].forEach(id=>{const el=document.getElementById(id);if(el)el.value="";});
  document.getElementById("orderModal").classList.add("open");
  document.body.style.overflow="hidden";
}
function closeModal(){document.getElementById("orderModal").classList.remove("open");document.body.style.overflow="";}
document.getElementById("orderModal").addEventListener("click",function(e){if(e.target===this)closeModal();});
function submitOrder(method){
  const name=document.getElementById("order-name").value.trim();
  const phone=document.getElementById("order-phone").value.trim();
  const street=document.getElementById("order-street").value.trim();
  const city=document.getElementById("order-city").value.trim();
  const pin=document.getElementById("order-pin").value.trim();
  const state=document.getElementById("order-state").value;
  if(!name||!phone||!street||!city||!pin||!state){showToast("Please fill Name, Phone and Address");return;}
  // AUTO REDUCE STOCK
  const soldItems=JSON.parse(localStorage.getItem("shop_sold")||"{}");
  const pid=String(currentProduct.id);
  soldItems[pid]=(soldItems[pid]||0)+1;
  localStorage.setItem("shop_sold",JSON.stringify(soldItems));
  allProducts=allProducts.map(p=>{if(p.id===currentProduct.id)return{...p,stock:Math.max(0,(p.stock||1)-1)};return p;});
  const msg="New Order - Amit Shop\n\nItem: "+currentProduct.name+"\nPrice: Rs."+currentProduct.price.toLocaleString("en-IN")+"\nName: "+name+"\nPhone: "+phone+"\nEmail: "+(document.getElementById("order-email").value||"Not provided")+"\nAddress: "+document.getElementById("order-street").value+", "+document.getElementById("order-city").value+", "+document.getElementById("order-state").value+" - "+document.getElementById("order-pin").value+(document.getElementById("order-landmark").value?" (Near: "+document.getElementById("order-landmark").value+")":"")+"\nNotes: "+(document.getElementById("order-message").value||"None")+"\n\nPayment: UPI "+CONFIG.upiId+"\nWill send payment screenshot after paying.";
  if(method==="whatsapp"){window.open("https://wa.me/"+CONFIG.whatsapp+"?text="+encodeURIComponent(msg),"_blank");showToast("Order sent! Complete UPI payment to confirm.");}
  else{window.location.href="mailto:"+CONFIG.email+"?subject="+encodeURIComponent("Order: "+currentProduct.name)+"&body="+encodeURIComponent(msg);showToast("Opening email...");}
  closeModal();
  renderProducts();
}
function toggleAdmin(){document.getElementById("adminForm").classList.toggle("open");}
function addProduct(){const name=document.getElementById("ap-name").value.trim();const price=parseInt(document.getElementById("ap-price").value);const desc=document.getElementById("ap-desc").value.trim();const img=document.getElementById("ap-img").value.trim();if(!name||!price||!desc||!img){showToast("Fill all required fields");return;}const p={id:Date.now(),name,category:document.getElementById("ap-category").value,condition:document.getElementById("ap-condition").value,price,original:parseInt(document.getElementById("ap-original").value)||0,stock:parseInt(document.getElementById("ap-stock").value)||1,desc,imgs:[img],ratings:[],comments:[]};const saved=JSON.parse(localStorage.getItem("shop_products")||"[]");saved.push(p);localStorage.setItem("shop_products",JSON.stringify(saved));localProducts=saved;allProducts=[...PRODUCTS,...localProducts];console.log("Copy this into PRODUCTS array:\n",JSON.stringify(p,null,2));showToast(`${name} added! Press F12 to copy permanent code.`);renderProducts();document.getElementById("adminForm").classList.remove("open");}
function showToast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),3000);}
renderProducts();

// Hide exact site header — .header-container from default.html
(function(){
  const h = document.querySelector('.header-container');
  if(h) h.style.display = 'none';
  // Also remove top margin/padding from content-wrapper
  const w = document.querySelector('.content-wrapper');
  if(w){ w.style.paddingTop = '0'; w.style.marginTop = '0'; }
})();
</script>
