from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from prometheus_flask_exporter import PrometheusMetrics
from config import Config
from models import db
from routes.auth import auth_bp
from routes.doctors import doctors_bp
from routes.appointments import appointments_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    JWTManager(app)

    # Prometheus metrics - automatically exposes /metrics endpoint
    metrics = PrometheusMetrics(app)
    metrics.info("medibook_app_info", "MediBook application info", version="1.0.0")

    app.register_blueprint(auth_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
