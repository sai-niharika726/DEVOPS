from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder="static")

# ── Serve the single-page application ──────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ── Serve any other static assets (images, css, js) if added later ─────────────
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

if __name__ == "__main__":
    print("=" * 50)
    print("  STRAPS & Co. — Bag Store")
    print("  Running at: http://0.0.0.0:5000")
    print("  Local:      http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
