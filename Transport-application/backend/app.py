import os
import re
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

from extensions import db, bcrypt
from models import User, PassApplication

BASE_FARE = 1000

DISCOUNT_RULES = {
    "regular": 0,
    "student": 20,      # age 10-20
    "oldage": 40,        # age 50+
    "handicapped": 50,   # no age restriction
}

MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
AADHAR_RE = re.compile(r"^\d{12}$")


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@db:5432/transit_pass"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "change-me-in-prod")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)

    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    CORS(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def validate_category_age(category, age):
    if category == "student" and not (10 <= age <= 20):
        return "Student category requires age between 10 and 20."
    if category == "oldage" and age < 50:
        return "Old age category requires age 50 or above."
    if category not in DISCOUNT_RULES:
        return "Invalid category."
    return None


def register_routes(app):

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/signup")
    def signup():
        data = request.get_json(force=True) or {}
        full_name = (data.get("full_name") or "").strip()
        mobile = (data.get("mobile") or "").strip()
        password = data.get("password") or ""
        dob = data.get("dob")  # optional, "YYYY-MM-DD"

        if not full_name or len(full_name) < 2:
            return jsonify(error="Enter a valid full name."), 400
        if not MOBILE_RE.match(mobile):
            return jsonify(error="Enter a valid 10-digit mobile number."), 400
        if len(password) < 6:
            return jsonify(error="Password must be at least 6 characters."), 400
        if User.query.filter_by(mobile=mobile).first():
            return jsonify(error="An account with this mobile number already exists."), 409

        user = User(
            full_name=full_name,
            mobile=mobile,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            dob=dob,
        )
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=str(user.id))
        return jsonify(token=token, user=user.to_dict()), 201

    @app.post("/api/login")
    def login():
        data = request.get_json(force=True) or {}
        mobile = (data.get("mobile") or "").strip()
        password = data.get("password") or ""

        user = User.query.filter_by(mobile=mobile).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify(error="Invalid mobile number or password."), 401

        token = create_access_token(identity=str(user.id))
        return jsonify(token=token, user=user.to_dict()), 200

    @app.get("/api/me")
    @jwt_required()
    def me():
        user = User.query.get(int(get_jwt_identity()))
        if not user:
            return jsonify(error="User not found."), 404
        return jsonify(user=user.to_dict())

    @app.post("/api/pass/quote")
    @jwt_required()
    def quote():
        """Calculate fare and discount for a given age/category, server-side."""
        data = request.get_json(force=True) or {}
        category = data.get("category", "regular")
        age = data.get("age")

        if not isinstance(age, int) or age <= 0:
            return jsonify(error="Enter a valid age."), 400

        err = validate_category_age(category, age)
        if err:
            return jsonify(error=err), 400

        discount_pct = DISCOUNT_RULES[category]
        payable = round(BASE_FARE * (1 - discount_pct / 100))
        return jsonify(
            base_fare=BASE_FARE,
            discount_pct=discount_pct,
            payable=payable,
        )

    @app.post("/api/pass/apply")
    @jwt_required()
    def apply_pass():
        data = request.get_json(force=True) or {}
        candidate_name = (data.get("candidate_name") or "").strip()
        mobile = (data.get("mobile") or "").strip()
        age = data.get("age")
        category = data.get("category", "regular")

        if not candidate_name or len(candidate_name) < 2:
            return jsonify(error="Enter a valid candidate name."), 400
        if not MOBILE_RE.match(mobile):
            return jsonify(error="Enter a valid 10-digit mobile number."), 400
        if not isinstance(age, int) or age <= 0:
            return jsonify(error="Enter a valid age."), 400

        err = validate_category_age(category, age)
        if err:
            return jsonify(error=err), 400

        discount_pct = DISCOUNT_RULES[category]
        payable = round(BASE_FARE * (1 - discount_pct / 100))

        application = PassApplication(
            user_id=int(get_jwt_identity()),
            candidate_name=candidate_name,
            mobile=mobile,
            age=age,
            category=category,
            base_fare=BASE_FARE,
            discount_pct=discount_pct,
            payable=payable,
            status="pending_verification",
        )
        db.session.add(application)
        db.session.commit()

        return jsonify(application=application.to_dict()), 201

    @app.post("/api/pass/<int:application_id>/confirm")
    @jwt_required()
    def confirm_pass(application_id):
        data = request.get_json(force=True) or {}
        aadhar_number = (data.get("aadhar_number") or "").strip()
        aadhar_name = (data.get("aadhar_name") or "").strip()

        application = PassApplication.query.filter_by(
            id=application_id, user_id=int(get_jwt_identity())
        ).first()
        if not application:
            return jsonify(error="Application not found."), 404
        if not AADHAR_RE.match(aadhar_number):
            return jsonify(error="Enter a valid 12-digit Aadhar number."), 400
        if not aadhar_name or len(aadhar_name) < 2:
            return jsonify(error="Enter the name as it appears on the Aadhar card."), 400

        # Store only a masked reference; never persist the raw Aadhar number.
        application.aadhar_last4 = aadhar_number[-4:]
        application.aadhar_name = aadhar_name
        application.status = "confirmed"
        application.confirmed_at = datetime.utcnow()
        db.session.commit()

        return jsonify(application=application.to_dict())

    @app.get("/api/pass/my")
    @jwt_required()
    def my_passes():
        applications = PassApplication.query.filter_by(
            user_id=int(get_jwt_identity())
        ).order_by(PassApplication.id.desc()).all()
        return jsonify(applications=[a.to_dict() for a in applications])


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
