from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Menu Data ──────────────────────────────────────────────────────────────────
MENU = {
    "espresso": [
        {"id": 1, "name": "Black Ritual",    "desc": "Double ristretto, velvety crema, obsidian depth",         "price": 3.50, "tag": "signature", "emoji": "☕"},
        {"id": 2, "name": "Velvet Macchiato","desc": "Espresso kissed with steamed micro-foam",                 "price": 4.20, "tag": "popular",   "emoji": "🥛"},
        {"id": 3, "name": "Dawn Cortado",    "desc": "Equal parts espresso & warm milk, perfectly balanced",    "price": 4.50, "tag": "new",       "emoji": "🌅"},
        {"id": 4, "name": "Ember Shot",      "desc": "Long espresso with a whisper of smoked caramel",          "price": 4.00, "tag": "seasonal",  "emoji": "🔥"},
    ],
    "cold": [
        {"id": 5, "name": "Midnight Brew",   "desc": "18-hour cold brew, smooth chocolate undertones",          "price": 5.00, "tag": "popular",   "emoji": "🌙"},
        {"id": 6, "name": "Cloud Latte",     "desc": "Cold foam cascade over chilled espresso & oat milk",      "price": 5.50, "tag": "signature", "emoji": "☁️"},
        {"id": 7, "name": "Amber Rush",      "desc": "Nitro cold brew, cascading golden bubbles",               "price": 5.80, "tag": "new",       "emoji": "⚡"},
        {"id": 8, "name": "Mocha Noir",      "desc": "Dark chocolate, espresso, and cold brew harmony",         "price": 5.20, "tag": "popular",   "emoji": "🍫"},
    ],
    "specialty": [
        {"id": 9,  "name": "Rose Reverie",   "desc": "Rosewater, cardamom, espresso & steamed almond milk",     "price": 6.00, "tag": "signature", "emoji": "🌹"},
        {"id": 10, "name": "Saffron Dusk",   "desc": "Turmeric, saffron, honey latte — golden hour in a cup",   "price": 6.50, "tag": "seasonal",  "emoji": "✨"},
        {"id": 11, "name": "Matcha Phantom", "desc": "Ceremonial matcha, oat milk, black sesame swirl",          "price": 6.00, "tag": "new",       "emoji": "🍵"},
        {"id": 12, "name": "Lavender Fog",   "desc": "Earl grey, lavender syrup, steamed oat milk",             "price": 5.80, "tag": "popular",   "emoji": "💜"},
    ],
    "bites": [
        {"id": 13, "name": "Kouign Amann",   "desc": "Caramelised butter pastry, flaky and burnished",          "price": 4.50, "tag": "popular",   "emoji": "🥐"},
        {"id": 14, "name": "Dark Bark",      "desc": "72% chocolate almond bark with sea-salt flakes",          "price": 3.80, "tag": "signature", "emoji": "🍫"},
        {"id": 15, "name": "Fig & Brie",     "desc": "Toasted sourdough, brie, fig jam, candied walnuts",       "price": 8.00, "tag": "new",       "emoji": "🧀"},
        {"id": 16, "name": "Cardamom Roll",  "desc": "Soft brioche, cardamom sugar, vanilla glaze",             "price": 4.20, "tag": "seasonal",  "emoji": "🌀"},
    ],
}

ORDERS = []          # in-memory order log (reset on restart)
ORDER_COUNTER = [0]  # mutable counter


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/menu")
def get_menu():
    return jsonify(MENU)


@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.get_json(force=True)
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    ORDER_COUNTER[0] += 1
    order_id = f"ORD-{ORDER_COUNTER[0]:04d}"
    total = sum(i.get("price", 0) * i.get("qty", 1) for i in items)

    order = {
        "id": order_id,
        "items": items,
        "total": round(total, 2),
        "status": "confirmed",
        "eta": "12–15 min",
    }
    ORDERS.append(order)
    return jsonify(order), 201


@app.route("/api/orders")
def list_orders():
    return jsonify(ORDERS)


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
