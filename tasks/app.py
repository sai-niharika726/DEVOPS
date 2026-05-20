from flask import Flask
import os

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "v1")

@app.route('/')
def home():
    return f"""
    <html>
        <head>
            <title>Company App-1</title>
        </head>
        <body style="font-family:Arial; text-align:center; margin-top:100px;">
            <h1>Flask Application Running Successfully</h1>
            <h2>Application Version: {VERSION}</h2>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {
        "status": "UP",
        "version": VERSION
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
