from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "sparkle-secret-2024"
CORS(app)

JEWELLERY = [
    # Rings
    {"id": 1,  "name": "Rosey Ring",      "category": "Rings",    "emoji": "💍", "art": "ring1",   "price": 1299, "stock": 12, "rating": 4.9, "tag": "Bestseller",  "color": "#ffb3c6", "bg": "#fff0f5", "desc": "Delicate rose-gold band with a tiny blooming flower ✿"},
    {"id": 2,  "name": "Starey Ring",    "category": "Rings",    "emoji": "⭐", "art": "ring2",   "price": 1599, "stock": 8,  "rating": 4.8, "tag": "New",         "color": "#a8d8ff", "bg": "#f0f8ff", "desc": "Dainty silver ring with a sparkling star centrepiece 🌟"},
    {"id": 3,  "name": "Candey Gemstone",    "category": "Rings",    "emoji": "🍬", "art": "ring3",   "price": 999,  "stock": 20, "rating": 4.7, "tag": "",            "color": "#b5ead7", "bg": "#f0fff8", "desc": "Playful multi-colour gemstone ring in pastel tones 🌈"},
    # Necklaces
    {"id": 4,  "name": "Moon & Star wear", "category": "Necklaces","emoji": "🌙", "art": "neck1",  "price": 2199, "stock": 6,  "rating": 5.0, "tag": "Top Rated",   "color": "#ffd6a5", "bg": "#fffdf0", "desc": "Crescent moon with tiny stars on a gold-filled chain ✨"},
    {"id": 5,  "name": "Pearl Dream wear",       "category": "Necklaces","emoji": "🤍", "art": "neck2",  "price": 2799, "stock": 9,  "rating": 4.9, "tag": "Bestseller",  "color": "#e8d5ff", "bg": "#faf5ff", "desc": "Genuine freshwater pearls strung on silk cord 🫧"},
    {"id": 6,  "name": "Rainbow Prism wear",     "category": "Necklaces","emoji": "🌈", "art": "neck3",  "price": 1799, "stock": 14, "rating": 4.6, "tag": "New",         "color": "#ffc8dd", "bg": "#fff5f8", "desc": "Crystal prism pendant that casts rainbow light ☀️"},
    # Earrings
    {"id": 7,  "name": "Sakura Dropsey",      "category": "Earrings", "emoji": "🌸", "art": "ear1",   "price": 899,  "stock": 25, "rating": 4.8, "tag": "",            "color": "#ffb3c6", "bg": "#fff0f5", "desc": "Cherry blossom petal drop earrings in blush enamel 🌸"},
    {"id": 8,  "name": "Cloud Hoopsey",       "category": "Earrings", "emoji": "☁️", "art": "ear2",   "price": 1099, "stock": 18, "rating": 4.7, "tag": "New",         "color": "#c9e4ff", "bg": "#f0f8ff", "desc": "Fluffy cloud-shaped sterling silver hoops 🌤️"},
    {"id": 9,  "name": "Honey Bee Studsey",   "category": "Earrings", "emoji": "🐝", "art": "ear3",   "price": 749,  "stock": 30, "rating": 4.9, "tag": "Bestseller",  "color": "#ffd93d", "bg": "#fffdf0", "desc": "Adorable gold honey-bee stud earrings 🍯"},
    # Bracelets
    {"id": 10, "name": "Daisy Chainsey",       "category": "Bracelets","emoji": "🌼", "art": "brac1",  "price": 1499, "stock": 10, "rating": 4.8, "tag": "",            "color": "#b5ead7", "bg": "#f0fff8", "desc": "Dainty daisy flower charm bracelet in gold 🌻"},
    {"id": 11, "name": "Bubblegum Beadsey",   "category": "Bracelets","emoji": "🫧", "art": "brac2",  "price": 699,  "stock": 35, "rating": 4.6, "tag": "Sale",        "color": "#ffc8dd", "bg": "#fff5f8", "desc": "Stretchy pastel bead bracelet — mix & match fun! 💕"},
    {"id": 12, "name": "Celestial Charmsey",   "category": "Bracelets","emoji": "🪐", "art": "brac3",  "price": 1899, "stock": 5,  "rating": 5.0, "tag": "Top Rated",   "color": "#e8d5ff", "bg": "#faf5ff", "desc": "Planet, moon & star charms on a delicate chain 🌙"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/jewellery")
def api_jewellery():
    category = request.args.get("category", "")
    items = JEWELLERY
    if category and category != "All":
        items = [i for i in items if i["category"] == category]
    return jsonify(items)

@app.route("/api/categories")
def api_categories():
    cats = ["All"] + sorted(set(i["category"] for i in JEWELLERY))
    return jsonify(cats)

@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    items = data.get("items", [])
    total = sum(i["price"] * i["qty"] for i in items)
    order_id = "JW" + __import__("random").randint(100000, 999999).__str__()
    return jsonify({"success": True, "order_id": order_id, "total": total, "message": "Order placed! Sparkles incoming ✨"})

if __name__ == "__main__":
    print("\n💎 GemGarden Jewellery Shop starting up!")
    print("🌸 Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
