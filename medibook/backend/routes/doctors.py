from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Doctor, Slot, User
from datetime import date

doctors_bp = Blueprint("doctors", __name__, url_prefix="/api/doctors")


@doctors_bp.route("", methods=["GET"])
def list_doctors():
    speciality = request.args.get("speciality")
    query = Doctor.query
    if speciality:
        query = query.filter_by(speciality=speciality)
    doctors = query.all()
    return jsonify([d.to_dict() for d in doctors]), 200


@doctors_bp.route("/<int:doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify(doctor.to_dict()), 200


@doctors_bp.route("", methods=["POST"])
@jwt_required()
def create_doctor():
    claims = get_jwt()
    if claims.get("role") not in ("doctor", "admin"):
        return jsonify({"error": "only doctors or admins can create profiles"}), 403

    data = request.get_json(force=True)
    user_id = int(get_jwt_identity())

    if Doctor.query.filter_by(user_id=user_id).first():
        return jsonify({"error": "doctor profile already exists"}), 409

    doctor = Doctor(
        user_id=user_id,
        speciality=data.get("speciality", "General"),
        experience_years=data.get("experience_years", 0),
        bio=data.get("bio", ""),
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify(doctor.to_dict()), 201


@doctors_bp.route("/<int:doctor_id>/slots", methods=["GET"])
def get_slots(doctor_id):
    slots = Slot.query.filter_by(doctor_id=doctor_id, is_booked=False).all()
    return jsonify([s.to_dict() for s in slots]), 200


@doctors_bp.route("/<int:doctor_id>/slots", methods=["POST"])
@jwt_required()
def add_slot(doctor_id):
    claims = get_jwt()
    if claims.get("role") not in ("doctor", "admin"):
        return jsonify({"error": "only doctors can add slots"}), 403

    data = request.get_json(force=True)
    slot = Slot(
        doctor_id=doctor_id,
        slot_date=date.fromisoformat(data["slot_date"]),
        slot_time=data["slot_time"],
    )
    db.session.add(slot)
    db.session.commit()
    return jsonify(slot.to_dict()), 201


@doctors_bp.route("/specialities", methods=["GET"])
def specialities():
    specs = db.session.query(Doctor.speciality).distinct().all()
    return jsonify([s[0] for s in specs]), 200


@doctors_bp.route("/stats", methods=["GET"])
def stats():
    from models import Appointment
    total_doctors = Doctor.query.count()
    available = Doctor.query.filter_by(available=True).count()
    total_appointments = Appointment.query.count()
    total_patients = User.query.filter_by(role="patient").count()
    specs = db.session.query(Doctor.speciality).distinct().count()
    return jsonify({
        "total_doctors": total_doctors,
        "available_doctors": available,
        "total_appointments": total_appointments,
        "total_patients": total_patients,
        "specialities": specs,
    }), 200
