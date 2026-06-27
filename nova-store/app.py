from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "127.0.0.1"),
    "port":     os.environ.get("DB_PORT", "5432"),
    "database": os.environ.get("DB_NAME", "novastore"),
    "user":     os.environ.get("DB_USER", "nova"),
    "password": os.environ.get("DB_PASSWORD", "nova123"),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price NUMERIC(10,2),
            category TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT 10
        );
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_name TEXT,
            customer_email TEXT,
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER,
            total NUMERIC(10,2),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    cur.execute("SELECT COUNT(*) FROM products;")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO products (name, description, price, category, image_url, stock) VALUES (%s,%s,%s,%s,%s,%s)",
            [
                ("MacBook Pro M3",    "Apple MacBook Pro with M3 chip, 16GB RAM, 512GB SSD",          1999.99, "Laptops",    "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400", 15),
                ("Sony WH-1000XM5",   "Industry-leading noise cancelling wireless headphones",           349.99, "Audio",      "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", 30),
                ("iPhone 15 Pro",     "Apple iPhone 15 Pro with titanium design and A17 Pro chip",     1199.99, "Phones",     "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400", 20),
                ("Samsung 4K OLED TV","55-inch 4K OLED Smart TV with HDR10+",                          1299.99, "TVs",        "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=400",  8),
                ("iPad Air M2",       "Apple iPad Air with M2 chip, 10.9-inch Liquid Retina display",   749.99, "Tablets",    "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400", 25),
                ("DJI Mini 4 Pro",    "Compact drone with 4K/60fps camera and 34-min flight time",      759.99, "Cameras",    "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=400", 12),
                ("LG UltraWide 34\"", "34-inch curved UltraWide QHD IPS display for professionals",    799.99, "Monitors",   "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400", 18),
                ("Keychron K2 Pro",   "Wireless mechanical keyboard with RGB backlight",                119.99, "Accessories","https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400", 50),
            ]
        )
    conn.commit()
    cur.close()
    conn.close()

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/products")
def get_products():
    category = request.args.get("category")
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if category and category != "All":
        cur.execute("SELECT * FROM products WHERE category=%s ORDER BY id", (category,))
    else:
        cur.execute("SELECT * FROM products ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(rows)

@app.route("/api/products/<int:pid>")
def get_product(pid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM products WHERE id=%s", (pid,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return jsonify(dict(row)) if row else (jsonify({"error": "Not found"}), 404)

@app.route("/api/categories")
def get_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
    cats = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(["All"] + cats)

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT price, stock FROM products WHERE id=%s", (data["product_id"],))
    p = cur.fetchone()
    if not p:
        return jsonify({"error": "Product not found"}), 404
    if p["stock"] < data["quantity"]:
        return jsonify({"error": "Insufficient stock"}), 400
    total = float(p["price"]) * int(data["quantity"])
    cur.execute(
        "INSERT INTO orders (customer_name,customer_email,product_id,quantity,total) VALUES (%s,%s,%s,%s,%s) RETURNING id",
        (data["customer_name"], data["customer_email"], data["product_id"], data["quantity"], total)
    )
    oid = cur.fetchone()["id"]
    cur.execute("UPDATE products SET stock=stock-%s WHERE id=%s", (data["quantity"], data["product_id"]))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"order_id": oid, "total": total, "message": "Order placed!"}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
