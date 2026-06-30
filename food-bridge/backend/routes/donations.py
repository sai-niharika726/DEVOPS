from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Donation, Claim, User

donations_bp = Blueprint("donations", __name__, url_prefix="/api/donations")


def current_user():
    return User.query.get(int(get_jwt_identity()))


@donations_bp.route("", methods=["GET"])
def list_donations():
    status = request.args.get("status", "available")
    query = Donation.query
    if status != "all":
        query = query.filter_by(status=status)
    donations = query.order_by(Donation.pickup_deadline.asc()).all()
    return jsonify([d.to_dict() for d in donations]), 200


@donations_bp.route("/<int:donation_id>", methods=["GET"])
def get_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    return jsonify(donation.to_dict()), 200


@donations_bp.route("", methods=["POST"])
@jwt_required()
def create_donation():
    claims = get_jwt()
    if claims.get("role") != "donor":
        return jsonify({"error": "only donors can post donations"}), 403

    data = request.get_json(force=True)
    required = ["title", "quantity", "pickup_location", "pickup_deadline"]
    if not all(data.get(f) for f in required):
        return jsonify({"error": f"required fields: {', '.join(required)}"}), 400

    try:
        deadline = datetime.fromisoformat(data["pickup_deadline"])
    except ValueError:
        return jsonify({"error": "pickup_deadline must be ISO format"}), 400

    donation = Donation(
        donor_id=int(get_jwt_identity()),
        title=data["title"],
        description=data.get("description", ""),
        quantity=data["quantity"],
        food_type=data.get("food_type", "veg"),
        pickup_location=data["pickup_location"],
        pickup_deadline=deadline,
    )
    db.session.add(donation)
    db.session.commit()
    return jsonify(donation.to_dict()), 201


@donations_bp.route("/<int:donation_id>/claim", methods=["POST"])
@jwt_required()
def claim_donation(donation_id):
    claims = get_jwt()
    if claims.get("role") != "volunteer":
        return jsonify({"error": "only volunteers can claim donations"}), 403

    donation = Donation.query.get_or_404(donation_id)
    if donation.status != "available":
        return jsonify({"error": "donation is no longer available"}), 409

    claim = Claim(donation_id=donation.id, volunteer_id=int(get_jwt_identity()))
    donation.status = "claimed"
    db.session.add(claim)
    db.session.commit()
    return jsonify({"donation": donation.to_dict(), "claim": claim.to_dict()}), 201


@donations_bp.route("/claims/mine", methods=["GET"])
@jwt_required()
def my_claims():
    user_id = int(get_jwt_identity())
    claims = Claim.query.filter_by(volunteer_id=user_id).all()
    result = []
    for c in claims:
        item = c.to_dict()
        item["donation"] = c.donation.to_dict()
        result.append(item)
    return jsonify(result), 200


@donations_bp.route("/claims/<int:claim_id>/status", methods=["PATCH"])
@jwt_required()
def update_claim_status(claim_id):
    user_id = int(get_jwt_identity())
    claim = Claim.query.get_or_404(claim_id)
    if claim.volunteer_id != user_id:
        return jsonify({"error": "not your claim"}), 403

    data = request.get_json(force=True)
    new_status = data.get("status")
    if new_status not in ("picked_up", "completed", "cancelled"):
        return jsonify({"error": "invalid status"}), 400

    claim.status = new_status
    if new_status == "completed":
        claim.donation.status = "completed"
    if new_status == "cancelled":
        claim.donation.status = "available"
        db.session.delete(claim)
        db.session.commit()
        return jsonify({"message": "claim cancelled"}), 200

    db.session.commit()
    return jsonify(claim.to_dict()), 200


@donations_bp.route("/stats", methods=["GET"])
def stats():
    active = Donation.query.filter_by(status="available").count()
    completed = Donation.query.filter_by(status="completed").count()
    donors = User.query.filter_by(role="donor").count()
    volunteers = User.query.filter_by(role="volunteer").count()
    return jsonify({
        "active_listings": active,
        "completed_donations": completed,
        "donors": donors,
        "volunteers": volunteers,
    }), 200
