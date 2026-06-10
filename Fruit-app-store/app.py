from flask import Flask, render_template_string, request, jsonify, session
from flask_cors import CORS
import json

app = Flask(__name__)
app.secret_key = "fruity-secret-key-2024"
CORS(app)

# Fruit inventory with emoji as cartoon representation
FRUITS = [
    {"id": 1,  "name": "Sweet-Apple",    "emoji": "🍎", "price": 30,  "unit": "kg",  "stock": 50, "color": "#ff6b6b", "bg": "#fff5f5", "desc": "Crispy & sweet!"},
    {"id": 2,  "name": "Banana",     "emoji": "🍌", "price": 20,  "unit": "doz", "stock": 40, "color": "#ffd93d", "bg": "#fffdf0", "desc": "Peel good vibes!"},
    {"id": 3,  "name": "Mangooo",      "emoji": "🥭", "price": 80,  "unit": "kg",  "stock": 30, "color": "#ff9a3c", "bg": "#fff8f0", "desc": "King of fruits!"},
    {"id": 4,  "name": "Grapes",     "emoji": "🍇", "price": 60,  "unit": "kg",  "stock": 25, "color": "#9b59b6", "bg": "#fdf6ff", "desc": "Bunch of joy!"},
    {"id": 5,  "name": "Watermelon", "emoji": "🍉🍇", "price": 25,  "unit": "pc",  "stock": 20, "color": "#2ecc71", "bg": "#f0fff4", "desc": "Summer splash!"},
    {"id": 6,  "name": "Orange",     "emoji": "🍊🍇", "price": 40,  "unit": "kg",  "stock": 35, "color": "#e67e22", "bg": "#fff9f0", "desc": "Vitamin C boost!"},
    {"id": 7,  "name": "Strawberry", "emoji": "🍓🍇", "price": 120, "unit": "box", "stock": 15, "color": "#e84393", "bg": "#fff5fa", "desc": "Berry delicious!"},
    {"id": 8,  "name": "Pineapple",  "emoji": "🍍🍇", "price": 50,  "unit": "pc",  "stock": 18, "color": "#f39c12", "bg": "#fffbf0", "desc": "Tropical party!"},
    {"id": 9,  "name": "Cherry",     "emoji": "🍒🍇", "price": 150, "unit": "box", "stock": 10, "color": "#c0392b", "bg": "#fff5f5", "desc": "Life's a cherry!"},
    {"id": 10, "name": "Kiwi",       "emoji": "🥝🍇", "price": 90,  "unit": "pc",  "stock": 22, "color": "#27ae60", "bg": "#f0fff8", "desc": "Tiny powerhouse!"},
    {"id": 11, "name": "Coconut",    "emoji": "🥥🍇", "price": 35,  "unit": "pc",  "stock": 28, "color": "#8b6914", "bg": "#fefcf3", "desc": "Tropical escape!"},
    {"id": 12, "name": "Lemon",      "emoji": "🍋🍇", "price": 15,  "unit": "pc",  "stock": 60, "color": "#f1c40f", "bg": "#fffef0", "desc": "Squeeze the day!"},
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🍓 FruitLand — Fresh & Fruity!</title>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;600;700;800&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --primary: #ff6b6b;
    --secondary: #ffd93d;
    --accent: #6bcb77;
    --purple: #c77dff;
    --bg: #fff9f0;
    --card-radius: 24px;
    --bounce: cubic-bezier(.68,-0.55,.27,1.55);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Nunito', sans-serif;
    background: var(--bg);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* ── Floating background blobs ── */
  body::before {
    content: '';
    position: fixed; inset: 0; z-index: -1;
    background:
      radial-gradient(circle at 10% 20%, #ffe0e020 0%, transparent 40%),
      radial-gradient(circle at 90% 80%, #c8f7c520 0%, transparent 40%),
      radial-gradient(circle at 80% 10%, #ffd6e020 0%, transparent 35%);
  }

  /* ── Header ── */
  header {
    background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 50%, #ffd93d 100%);
    padding: 0 2rem;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 4px 20px #ff6b6b40;
  }
  .header-inner {
    max-width: 1200px; margin: 0 auto;
    display: flex; align-items: center; justify-content: space-between;
    height: 72px;
  }
  .logo {
    font-family: 'Baloo 2', cursive;
    font-size: 2rem; font-weight: 800;
    color: #fff; text-shadow: 2px 3px 0 #c0392b40;
    letter-spacing: -1px;
    display: flex; align-items: center; gap: .4rem;
  }
  .logo span { animation: wobble 3s ease-in-out infinite; display: inline-block; }
  @keyframes wobble {
    0%,100% { transform: rotate(-5deg); }
    50%      { transform: rotate(5deg); }
  }

  /* ── Cart button ── */
  #cart-btn {
    background: #fff; border: none; cursor: pointer;
    padding: .6rem 1.4rem; border-radius: 50px;
    font-family: 'Baloo 2', cursive; font-size: 1rem; font-weight: 700;
    color: var(--primary); display: flex; align-items: center; gap: .5rem;
    box-shadow: 0 4px 12px #00000020;
    transition: transform .2s var(--bounce), box-shadow .2s;
  }
  #cart-btn:hover { transform: scale(1.08); box-shadow: 0 6px 18px #00000030; }
  #cart-count {
    background: var(--primary); color: #fff;
    border-radius: 50%; width: 24px; height: 24px;
    font-size: .8rem; display: flex; align-items: center; justify-content: center;
    transition: transform .3s var(--bounce);
  }
  #cart-count.bump { transform: scale(1.6); }

  /* ── Hero banner ── */
  .hero {
    text-align: center; padding: 3rem 1rem 2rem;
    max-width: 700px; margin: 0 auto;
  }
  .hero h1 {
    font-family: 'Baloo 2', cursive; font-size: clamp(2.2rem, 6vw, 3.5rem);
    font-weight: 800; line-height: 1.1;
    background: linear-gradient(135deg, #ff6b6b, #ff9a3c, #ffd93d);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero p { color: #888; font-size: 1.1rem; margin-top: .6rem; }
  .fruit-parade {
    font-size: 2.2rem; letter-spacing: .3rem; margin-top: .8rem;
    animation: scroll-fruits 8s linear infinite;
    display: inline-block;
  }
  @keyframes scroll-fruits {
    0%   { transform: translateX(30px);  opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { transform: translateX(-30px); opacity: 0; }
  }

  /* ── Search & filter ── */
  .toolbar {
    max-width: 1200px; margin: 0 auto 1.5rem;
    padding: 0 1.5rem;
    display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;
  }
  .search-wrap {
    flex: 1; min-width: 200px;
    position: relative;
  }
  .search-wrap input {
    width: 100%; padding: .75rem 1rem .75rem 3rem;
    border: 2.5px solid #ffe0b2; border-radius: 50px;
    font-family: 'Nunito', sans-serif; font-size: 1rem;
    background: #fff; outline: none;
    transition: border-color .2s, box-shadow .2s;
  }
  .search-wrap input:focus { border-color: var(--primary); box-shadow: 0 0 0 4px #ff6b6b15; }
  .search-wrap .s-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); font-size: 1.1rem; }

  /* ── Grid ── */
  .grid {
    max-width: 1200px; margin: 0 auto;
    padding: 0 1.5rem 4rem;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1.5rem;
  }

  /* ── Fruit card ── */
  .card {
    background: #fff;
    border-radius: var(--card-radius);
    overflow: hidden;
    box-shadow: 0 4px 16px #0000000d;
    transition: transform .3s var(--bounce), box-shadow .3s;
    position: relative;
    animation: pop-in .4s var(--bounce) backwards;
  }
  @keyframes pop-in {
    from { transform: scale(.7) translateY(20px); opacity: 0; }
    to   { transform: none; opacity: 1; }
  }
  .card:hover { transform: translateY(-8px) rotate(.5deg); box-shadow: 0 16px 40px #0000001a; }

  .card-emoji-wrap {
    height: 130px;
    display: flex; align-items: center; justify-content: center;
    font-size: 5.5rem;
    position: relative; overflow: hidden;
    transition: transform .3s;
  }
  .card:hover .card-emoji-wrap { transform: scale(1.08); }
  .card-emoji-wrap .emoji-shadow {
    position: absolute; bottom: -12px;
    width: 70%; height: 20px;
    background: #00000018;
    border-radius: 50%;
    filter: blur(8px);
  }

  .card-body { padding: 1rem 1.1rem 1.2rem; }
  .card-name {
    font-family: 'Baloo 2', cursive; font-size: 1.25rem; font-weight: 700;
    line-height: 1.2;
  }
  .card-desc { font-size: .82rem; color: #aaa; margin: .15rem 0 .7rem; font-style: italic; }
  .card-footer {
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: .5rem;
  }
  .price {
    font-family: 'Baloo 2', cursive; font-size: 1.3rem; font-weight: 800;
  }
  .unit { font-size: .75rem; color: #bbb; font-weight: 400; }
  .stock { font-size: .75rem; color: #aaa; }
  .stock.low { color: #e74c3c; font-weight: 700; }

  /* ── Qty + Add ── */
  .qty-row { display: flex; align-items: center; gap: .4rem; margin-top: .8rem; }
  .qty-btn {
    width: 30px; height: 30px; border-radius: 50%;
    border: 2px solid currentColor; background: transparent;
    cursor: pointer; font-size: 1.1rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    transition: transform .15s var(--bounce), background .15s;
  }
  .qty-btn:hover { transform: scale(1.2); background: currentColor; color: #fff !important; }
  .qty-val {
    width: 32px; text-align: center;
    font-family: 'Baloo 2', cursive; font-weight: 700; font-size: 1rem;
  }
  .add-btn {
    flex: 1; padding: .5rem; border: none; border-radius: 50px;
    cursor: pointer; font-family: 'Baloo 2', cursive; font-weight: 700;
    font-size: .95rem; color: #fff;
    background: linear-gradient(135deg, var(--c1), var(--c2));
    box-shadow: 0 4px 12px var(--shadow);
    transition: transform .2s var(--bounce), box-shadow .2s;
  }
  .add-btn:hover { transform: scale(1.04) translateY(-2px); box-shadow: 0 6px 20px var(--shadow); }
  .add-btn:active { transform: scale(.96); }

  /* ── Cart Sidebar ── */
  .overlay {
    display: none; position: fixed; inset: 0;
    background: #00000040; z-index: 200;
    backdrop-filter: blur(4px);
  }
  .overlay.open { display: block; animation: fade-in .2s; }
  @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }

  .cart-sidebar {
    position: fixed; top: 0; right: -420px; bottom: 0;
    width: min(420px, 100vw);
    background: #fff; z-index: 201;
    display: flex; flex-direction: column;
    transition: right .35s cubic-bezier(.4,0,.2,1);
    border-radius: 24px 0 0 24px;
    box-shadow: -8px 0 40px #0000001a;
  }
  .cart-sidebar.open { right: 0; }

  .cart-header {
    padding: 1.4rem 1.5rem;
    background: linear-gradient(135deg, #ff6b6b, #ff8e53);
    color: #fff; display: flex; align-items: center; justify-content: space-between;
    border-radius: 24px 0 0 0;
  }
  .cart-header h2 { font-family: 'Baloo 2', cursive; font-size: 1.5rem; font-weight: 800; }
  #close-cart {
    background: #ffffff30; border: none; color: #fff;
    width: 36px; height: 36px; border-radius: 50%;
    font-size: 1.2rem; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background .2s, transform .2s;
  }
  #close-cart:hover { background: #ffffff50; transform: rotate(90deg); }

  .cart-items { flex: 1; overflow-y: auto; padding: 1rem 1.5rem; }
  .cart-empty {
    text-align: center; padding: 3rem 0; color: #ccc;
    font-size: 4rem; line-height: 1;
  }
  .cart-empty p { font-size: 1rem; margin-top: .5rem; }

  .cart-item {
    display: flex; align-items: center; gap: 1rem;
    padding: .75rem 0; border-bottom: 1.5px dashed #f0e0d0;
    animation: pop-in .3s var(--bounce) backwards;
  }
  .ci-emoji { font-size: 2.2rem; flex-shrink: 0; }
  .ci-info { flex: 1; }
  .ci-name { font-family: 'Baloo 2', cursive; font-weight: 700; }
  .ci-price { font-size: .85rem; color: #aaa; }
  .ci-controls { display: flex; align-items: center; gap: .5rem; }
  .ci-qty-btn {
    width: 26px; height: 26px; border-radius: 50%;
    border: 2px solid #ff6b6b; color: #ff6b6b;
    background: #fff; cursor: pointer; font-weight: 700; font-size: .9rem;
    display: flex; align-items: center; justify-content: center;
    transition: transform .15s var(--bounce), background .15s;
  }
  .ci-qty-btn:hover { transform: scale(1.2); background: #ff6b6b; color: #fff; }
  .ci-qty { font-family: 'Baloo 2'; font-weight: 700; width: 20px; text-align: center; }
  .ci-remove { background: none; border: none; color: #ddd; cursor: pointer; font-size: 1rem; transition: color .2s; }
  .ci-remove:hover { color: #e74c3c; }

  .cart-footer {
    padding: 1.2rem 1.5rem;
    border-top: 2px dashed #f0e0d0;
  }
  .total-row {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 1rem;
  }
  .total-label { font-family: 'Baloo 2'; font-size: 1.1rem; color: #888; }
  .total-amount { font-family: 'Baloo 2'; font-size: 1.8rem; font-weight: 800; color: var(--primary); }
  #checkout-btn {
    width: 100%; padding: 1rem; border: none; border-radius: 50px;
    background: linear-gradient(135deg, #ff6b6b, #ff8e53);
    color: #fff; font-family: 'Baloo 2', cursive;
    font-size: 1.2rem; font-weight: 800; cursor: pointer;
    box-shadow: 0 6px 20px #ff6b6b50;
    transition: transform .2s var(--bounce), box-shadow .2s;
  }
  #checkout-btn:hover { transform: scale(1.03) translateY(-2px); box-shadow: 0 10px 28px #ff6b6b60; }

  /* ── Toast ── */
  #toast {
    position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%) translateY(80px);
    background: #2d3436; color: #fff; border-radius: 50px;
    padding: .75rem 2rem; font-family: 'Baloo 2'; font-size: 1rem;
    z-index: 300; transition: transform .4s var(--bounce), opacity .3s;
    opacity: 0; pointer-events: none; white-space: nowrap;
  }
  #toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }

  /* ── Order modal ── */
  .modal-wrap {
    display: none; position: fixed; inset: 0;
    background: #00000050; z-index: 400;
    align-items: center; justify-content: center;
    backdrop-filter: blur(6px);
  }
  .modal-wrap.open { display: flex; animation: fade-in .2s; }
  .modal {
    background: #fff; border-radius: 28px;
    padding: 2.5rem; max-width: 420px; width: 90%;
    text-align: center; animation: pop-in .4s var(--bounce);
    box-shadow: 0 24px 60px #0000002a;
  }
  .modal .big-emoji { font-size: 5rem; }
  .modal h2 { font-family: 'Baloo 2'; font-size: 1.8rem; font-weight: 800; margin: .8rem 0 .4rem; color: #2d3436; }
  .modal p { color: #888; margin-bottom: 1.5rem; }
  .modal-btn {
    padding: .8rem 2.5rem; border: none; border-radius: 50px;
    background: linear-gradient(135deg, #6bcb77, #4ea8de);
    color: #fff; font-family: 'Baloo 2'; font-size: 1.1rem; font-weight: 800;
    cursor: pointer; box-shadow: 0 6px 20px #6bcb7750;
    transition: transform .2s var(--bounce);
  }
  .modal-btn:hover { transform: scale(1.06); }

  /* ── Responsive ── */
  @media (max-width: 480px) {
    .grid { grid-template-columns: repeat(2, 1fr); gap: 1rem; padding: 0 .8rem 3rem; }
    .card-emoji-wrap { height: 100px; font-size: 4rem; }
  }
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="logo"><span>🍓</span> FruitLand</div>
    <button id="cart-btn" onclick="toggleCart()">
      🛒 My Basket
      <span id="cart-count">0</span>
    </button>
  </div>
</header>

<div class="hero">
  <h1>Fresh Fruits,<br>Happy You! 🌈</h1>
  <p>Farm-to-door goodness every single day</p>
  <div class="fruit-parade">🍎🍌🥭🍇🍉🍊🍓🍍🍒🥝🥥🍋</div>
</div>

<div class="toolbar">
  <div class="search-wrap">
    <span class="s-icon">🔍</span>
    <input type="text" id="search" placeholder="Search for your fave fruit…" oninput="filterFruits()">
  </div>
</div>

<div class="grid" id="fruit-grid"></div>

<!-- Cart overlay -->
<div class="overlay" id="overlay" onclick="toggleCart()"></div>
<div class="cart-sidebar" id="cart-sidebar">
  <div class="cart-header">
    <h2>🛒 My Basket</h2>
    <button id="close-cart" onclick="toggleCart()">✕</button>
  </div>
  <div class="cart-items" id="cart-items">
    <div class="cart-empty">🧺<p>Your basket is empty!</p></div>
  </div>
  <div class="cart-footer">
    <div class="total-row">
      <span class="total-label">Total</span>
      <span class="total-amount" id="total">₹0</span>
    </div>
    <button id="checkout-btn" onclick="checkout()">🎉 Checkout Now!</button>
  </div>
</div>

<div id="toast"></div>

<!-- Order success modal -->
<div class="modal-wrap" id="modal">
  <div class="modal">
    <div class="big-emoji">🎉</div>
    <h2>Order Placed!</h2>
    <p>Your fresh fruits are on their way! Expect delivery soon. 🚚💨</p>
    <button class="modal-btn" onclick="closeModal()">Yay, Thanks! 🥳</button>
  </div>
</div>

<script>
const FRUITS = {{ fruits_json | safe }};
let cart = {};
let quantities = {};

FRUITS.forEach(f => { quantities[f.id] = 1; });

function renderGrid(fruits) {
  const grid = document.getElementById('fruit-grid');
  grid.innerHTML = '';
  fruits.forEach((f, idx) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.animationDelay = (idx * 0.06) + 's';
    const stockClass = f.stock <= 10 ? 'low' : '';
    const stockText = f.stock <= 10 ? `⚡ Only ${f.stock} left!` : `✅ ${f.stock} in stock`;

    // Derive gradient from fruit color
    const lighten = f.color + 'cc';
    card.innerHTML = `
      <div class="card-emoji-wrap" style="background:${f.bg}">
        <span style="filter:drop-shadow(2px 4px 6px ${f.color}50)">${f.emoji}</span>
        <div class="emoji-shadow"></div>
      </div>
      <div class="card-body">
        <div class="card-name" style="color:${f.color}">${f.name}</div>
        <div class="card-desc">${f.desc}</div>
        <div class="card-footer">
          <div>
            <span class="price" style="color:${f.color}">₹${f.price}</span>
            <span class="unit">/ ${f.unit}</span>
          </div>
          <div class="stock ${stockClass}">${stockText}</div>
        </div>
        <div class="qty-row">
          <button class="qty-btn" style="color:${f.color};border-color:${f.color}" onclick="changeQty(${f.id},-1)">−</button>
          <span class="qty-val" id="qty-${f.id}">1</span>
          <button class="qty-btn" style="color:${f.color};border-color:${f.color}" onclick="changeQty(${f.id},1)">+</button>
          <button class="add-btn"
            style="--c1:${f.color};--c2:${lighten};--shadow:${f.color}60"
            onclick="addToCart(${f.id})">
            Add 🛒
          </button>
        </div>
      </div>`;
    grid.appendChild(card);
  });
}

function changeQty(id, delta) {
  quantities[id] = Math.max(1, (quantities[id] || 1) + delta);
  const el = document.getElementById('qty-' + id);
  if (el) el.textContent = quantities[id];
}

function addToCart(id) {
  const f = FRUITS.find(x => x.id === id);
  const qty = quantities[id] || 1;
  if (!cart[id]) cart[id] = { ...f, qty: 0 };
  cart[id].qty += qty;
  updateCartUI();
  showToast(`${f.emoji} ${qty}× ${f.name} added!`);
  // Reset qty
  quantities[id] = 1;
  const el = document.getElementById('qty-' + id);
  if (el) el.textContent = 1;
  // Bump count badge
  const cnt = document.getElementById('cart-count');
  cnt.classList.add('bump');
  setTimeout(() => cnt.classList.remove('bump'), 400);
}

function updateCartUI() {
  const items = Object.values(cart).filter(x => x.qty > 0);
  const countEl = document.getElementById('cart-count');
  const itemsEl = document.getElementById('cart-items');
  const totalEl = document.getElementById('total');

  const totalQty = items.reduce((s, i) => s + i.qty, 0);
  const totalAmt = items.reduce((s, i) => s + i.qty * i.price, 0);

  countEl.textContent = totalQty;

  if (items.length === 0) {
    itemsEl.innerHTML = '<div class="cart-empty">🧺<p>Your basket is empty!</p></div>';
  } else {
    itemsEl.innerHTML = items.map(i => `
      <div class="cart-item">
        <span class="ci-emoji">${i.emoji}</span>
        <div class="ci-info">
          <div class="ci-name">${i.name}</div>
          <div class="ci-price">₹${i.price} × ${i.qty} = ₹${i.price * i.qty}</div>
        </div>
        <div class="ci-controls">
          <button class="ci-qty-btn" onclick="adjustCart(${i.id},-1)">−</button>
          <span class="ci-qty">${i.qty}</span>
          <button class="ci-qty-btn" onclick="adjustCart(${i.id},1)">+</button>
          <button class="ci-remove" onclick="removeFromCart(${i.id})" title="Remove">🗑️</button>
        </div>
      </div>`).join('');
  }
  totalEl.textContent = '₹' + totalAmt;
}

function adjustCart(id, delta) {
  if (!cart[id]) return;
  cart[id].qty = Math.max(0, cart[id].qty + delta);
  if (cart[id].qty === 0) delete cart[id];
  updateCartUI();
}

function removeFromCart(id) {
  delete cart[id];
  updateCartUI();
}

function toggleCart() {
  const sidebar = document.getElementById('cart-sidebar');
  const overlay = document.getElementById('overlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2200);
}

function filterFruits() {
  const q = document.getElementById('search').value.toLowerCase();
  const filtered = FRUITS.filter(f => f.name.toLowerCase().includes(q));
  renderGrid(filtered);
}

function checkout() {
  const items = Object.values(cart).filter(x => x.qty > 0);
  if (items.length === 0) { showToast('🧺 Add some fruits first!'); return; }
  toggleCart();
  document.getElementById('modal').classList.add('open');
  cart = {};
  updateCartUI();
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
}

// Init
renderGrid(FRUITS);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, fruits_json=json.dumps(FRUITS))

@app.route("/api/fruits")
def api_fruits():
    return jsonify(FRUITS)

@app.route("/api/cart/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    items = data.get("items", [])
    total = sum(item["price"] * item["qty"] for item in items)
    return jsonify({"success": True, "message": "Order placed!", "total": total, "order_id": "FL" + str(hash(str(items)))[-6:]})

if __name__ == "__main__":
    print("\n🍓 FruitLand is starting up!")
    print("🌐 Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
