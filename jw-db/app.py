from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "mysql-container"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "root123"),
        database=os.environ.get("DB_NAME", "jewellerydb")
    )

@app.route("/orders", methods=["GET"])
def get_orders():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    return jsonify(orders)

@app.route("/orders", methods=["POST"])
def add_order():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO orders (item, quantity) VALUES (%s, %s)",
                   (data["item"], data["quantity"]))
    db.commit()
    return jsonify({"message": "Order added!"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
