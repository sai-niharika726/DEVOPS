from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    required = ["name", "email", "password", "role"]
    if not all(data.get(f) for f in required):
        return jsonify({"error": "name, email, password and role are required"}), 400

    if data["role"] not in ("donor", "volunteer"):
        return jsonify({"error": "role must be 'donor' or 'volunteer'"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "email already registered"}), 409

    user = User(
        name=data["name"],
        email=data["email"],
        role=data["role"],
        org_name=data.get("org_name"),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid email or password"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )
    return jsonify({"token": token, "user": user.to_dict()}), 200
