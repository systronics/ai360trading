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
.shop-hero{background:var(--ink);padding:56px 24px 40px;text-align:center;position:relative;overflow:hidden}
.shop-hero::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(45deg,transparent,transparent 40px,rgba(244,162,97,0.04) 40px,rgba(244,162,97,0.04) 80px)}
.shop-hero h1{font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,3.5rem);color:#fff;position:relative;line-height:1.1}
.shop-hero h1 span{color:var(--gold)}
.shop-hero p{color:rgba(255,255,255,0.65);margin-top:12px;font-size:1rem;position:relative}
.shop-badges{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:20px;position:relative}
.shop-badge{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:rgba(255,255,255,0.85);padding:6px 14px;border-radius:100px;font-size:0.78rem;font-weight:500}
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
@media(max-width:600px){.products-grid{grid-template-columns:1fr 1fr;gap:14px;padding:8px 12px 40px}.filter-bar{padding:16px 12px}.admin-section{padding:0 12px 40px}.form-grid{grid-template-columns:1fr}}
@media(max-width:400px){.products-grid{grid-template-columns:1fr}}
</style>

<div class="shop-wrap">
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
  <div class="admin-section">
    <button class="admin-toggle" onclick="toggleAdmin()">＋ Add New Product (Admin Only)</button>
    <div class="admin-form" id="adminForm">
      <h3>Add New Product</h3>
      <div class="form-grid">
        <div class="form-group"><label class="form-label">Product Name *</label><input class="form-input" id="ap-name" placeholder="e.g. Vintage Painting"></div>
        <div class="form-group"><label class="form-label">Category *</label><select class="form-select" id="ap-category"><option value="art">Art &amp; Collectibles</option><option value="electronics">Electronics</option><option value="books">Books</option><option value="home">Home &amp; Decor</option><option value="other">Other</option></select></div>
        <div class="form-group"><label class="form-label">Selling Price (Rs.) *</label><input class="form-input" id="ap-price" type="number" placeholder="e.g. 2500"></div>
        <div class="form-group"><label class="form-label">Original Price (Rs.)</label><input class="form-input" id="ap-original" type="number" placeholder="e.g. 5000"></div>
        <div class="form-group full"><label class="form-label">Description *</label><textarea class="form-textarea" id="ap-desc" placeholder="Describe the item — size, condition, material..."></textarea></div>
        <div class="form-group full"><label class="form-label">Image Path * (upload to /public/image/ in repo first)</label><input class="form-input" id="ap-img" placeholder="/public/image/your-product.jpg"></div>
        <div class="form-group"><label class="form-label">Condition</label><select class="form-select" id="ap-condition"><option value="used">Used / Vintage</option><option value="new">New / Resale</option><option value="refurbished">Refurbished</option></select></div>
        <div class="form-group"><label class="form-label">Stock</label><input class="form-input" id="ap-stock" type="number" value="1"></div>
      </div>
      <div class="admin-note">After adding, press F12, go to Console tab — copy the JSON shown there and paste into the PRODUCTS array in this file for permanent save.</div>
      <button class="btn-submit-order" style="margin-top:16px" onclick="addProduct()">Add Product</button>
    </div>
  </div>
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
      <div class="form-group"><label class="form-label">Delivery Address *</label><textarea class="form-textarea" id="order-address" placeholder="Full address with PIN code"></textarea></div>
      <div class="form-group"><label class="form-label">Message / Questions</label><textarea class="form-textarea" id="order-message" placeholder="Any questions about this item?"></textarea></div>
      <div class="payment-section">
        <div class="payment-title">Pay via UPI or Bank Transfer</div>
        <div class="upi-box">
          <div style="width:130px;height:130px;margin:0 auto 10px;background:var(--ink);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.7rem;text-align:center;padding:10px;line-height:1.6">Upload your UPI QR image to /public/image/upi-qr.png and replace this block with an img tag</div>
          <div class="upi-id" id="modalUpiId">UPI: yourname@upi</div>
          <div class="upi-note">Scan and pay, then send payment screenshot on WhatsApp</div>
        </div>
        <div class="divider-or">or Bank Transfer</div>
        <div class="bank-box">
          <div class="bank-row"><span class="bank-label">Account Name</span><span class="bank-value">Amit Kumar</span></div>
          <div class="bank-row"><span class="bank-label">Bank Name</span><span class="bank-value">State Bank Of India</span></div>
          <div class="bank-row"><span class="bank-label">Account No</span><span class="bank-value">20231037959</span></div>
          <div class="bank-row"><span class="bank-label">IFSC Code</span><span class="bank-value">SBIN0011415</span></div>
          <div class="bank-row"><span class="bank-label">Account Type</span><span class="bank-value">Savings</span></div>
        </div>
        <div style="font-size:0.75rem;color:var(--muted);margin-top:10px;text-align:center">After payment — share screenshot on WhatsApp for fast confirmation</div>
      </div>
      <button class="btn-submit-order" onclick="submitOrder('email')">Send Order via Email</button>
      <a class="btn-submit-wa" id="waOrderBtn" href="#" onclick="submitOrder('whatsapp')" target="_blank">Order via WhatsApp</a>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
// UPDATE THESE WITH YOUR REAL DETAILS
const CONFIG = {
  whatsapp:   "919634759528",
  email:      "admin@ai360trading.in",
  upiId:      "9634759528@upi",
  sellerName: "Amit Kumar",
  city:       "Haridwar, Uttarakhand"
};

// YOUR PRODUCTS — painting1.jpg, painting2.jpg, painting3.jpg go in /public/image/
const PRODUCTS = [
  {
    id: 1,
    name: "Traditional Indian Beaded Art — Lady with Golden Deer",
    category: "art",
    condition: "used",
    price: 10,
    original: 150,
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

function getAllProducts(){return allProducts.map(p=>({...p,comments:[...(p.comments||[]),...(localComments[String(p.id)]||[])],ratings:[...(p.ratings||[]),...(localRatings[String(p.id)]||[])]}));}
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
function openOrder(productId){currentProduct=getAllProducts().find(p=>p.id===productId);document.getElementById("modalProductName").textContent=currentProduct.name;document.getElementById("modalProductPrice").textContent=`Rs.${currentProduct.price.toLocaleString("en-IN")} — Pay via UPI or Bank`;document.getElementById("modalUpiId").textContent=`UPI: ${CONFIG.upiId}`;document.getElementById("orderModal").classList.add("open");document.body.style.overflow="hidden";}
function closeModal(){document.getElementById("orderModal").classList.remove("open");document.body.style.overflow="";}
document.getElementById("orderModal").addEventListener("click",function(e){if(e.target===this)closeModal();});
function submitOrder(method){const name=document.getElementById("order-name").value.trim();const phone=document.getElementById("order-phone").value.trim();const address=document.getElementById("order-address").value.trim();if(!name||!phone||!address){showToast("Please fill Name, Phone and Address");return;}const msg=`New Order - Amit's Shop\n\nItem: ${currentProduct.name}\nPrice: Rs.${currentProduct.price.toLocaleString("en-IN")}\nName: ${name}\nPhone: ${phone}\nEmail: ${document.getElementById("order-email").value||"Not provided"}\nAddress: ${address}\nNotes: ${document.getElementById("order-message").value||"None"}\n\nPayment via UPI (${CONFIG.upiId}) or Bank Transfer. Will send screenshot.`;if(method==="whatsapp"){window.open(`https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(msg)}`,"_blank");showToast("Opening WhatsApp...");}else{window.location.href=`mailto:${CONFIG.email}?subject=${encodeURIComponent("Order: "+currentProduct.name)}&body=${encodeURIComponent(msg)}`;showToast("Opening email...");}closeModal();}
function toggleAdmin(){document.getElementById("adminForm").classList.toggle("open");}
function addProduct(){const name=document.getElementById("ap-name").value.trim();const price=parseInt(document.getElementById("ap-price").value);const desc=document.getElementById("ap-desc").value.trim();const img=document.getElementById("ap-img").value.trim();if(!name||!price||!desc||!img){showToast("Fill all required fields");return;}const p={id:Date.now(),name,category:document.getElementById("ap-category").value,condition:document.getElementById("ap-condition").value,price,original:parseInt(document.getElementById("ap-original").value)||0,stock:parseInt(document.getElementById("ap-stock").value)||1,desc,imgs:[img],ratings:[],comments:[]};const saved=JSON.parse(localStorage.getItem("shop_products")||"[]");saved.push(p);localStorage.setItem("shop_products",JSON.stringify(saved));localProducts=saved;allProducts=[...PRODUCTS,...localProducts];console.log("Copy this into PRODUCTS array:\n",JSON.stringify(p,null,2));showToast(`${name} added! Press F12 to copy permanent code.`);renderProducts();document.getElementById("adminForm").classList.remove("open");}
function showToast(msg){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),3000);}
renderProducts();
</script>
