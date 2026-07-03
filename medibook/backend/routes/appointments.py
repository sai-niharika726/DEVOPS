from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Appointment, Slot, Doctor

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")


@appointments_bp.route("", methods=["POST"])
@jwt_required()
def book():
    claims = get_jwt()
    if claims.get("role") != "patient":
        return jsonify({"error": "only patients can book appointments"}), 403

    data = request.get_json(force=True)
    slot = Slot.query.get_or_404(data["slot_id"])

    if slot.is_booked:
        return jsonify({"error": "slot already booked"}), 409

    appointment = Appointment(
        patient_id=int(get_jwt_identity()),
        doctor_id=slot.doctor_id,
        slot_id=slot.id,
        reason=data.get("reason", ""),
    )
    slot.is_booked = True
    db.session.add(appointment)
    db.session.commit()
    return jsonify(appointment.to_dict()), 201


@appointments_bp.route("/mine", methods=["GET"])
@jwt_required()
def my_appointments():
    patient_id = int(get_jwt_identity())
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    return jsonify([a.to_dict() for a in appointments]), 200


@appointments_bp.route("/doctor", methods=["GET"])
@jwt_required()
def doctor_appointments():
    claims = get_jwt()
    if claims.get("role") not in ("doctor", "admin"):
        return jsonify({"error": "only doctors can view their appointments"}), 403

    user_id = int(get_jwt_identity())
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if not doctor:
        return jsonify({"error": "doctor profile not found"}), 404

    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    return jsonify([a.to_dict() for a in appointments]), 200


@appointments_bp.route("/<int:appointment_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel(appointment_id):
    patient_id = int(get_jwt_identity())
    appt = Appointment.query.get_or_404(appointment_id)
    if appt.patient_id != patient_id:
        return jsonify({"error": "not your appointment"}), 403

    appt.status = "cancelled"
    appt.slot.is_booked = False
    db.session.commit()
    return jsonify(appt.to_dict()), 200


@appointments_bp.route("/<int:appointment_id>/complete", methods=["PATCH"])
@jwt_required()
def complete(appointment_id):
    claims = get_jwt()
    if claims.get("role") not in ("doctor", "admin"):
        return jsonify({"error": "only doctors can mark complete"}), 403

    appt = Appointment.query.get_or_404(appointment_id)
    appt.status = "completed"
    db.session.commit()
    return jsonify(appt.to_dict()), 200
