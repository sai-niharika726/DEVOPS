from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # patient | doctor | admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}


class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    speciality = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text, nullable=True)
    available = db.Column(db.Boolean, default=True)

    user = db.relationship("User", backref="doctor_profile")
    slots = db.relationship("Slot", backref="doctor", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.user.name,
            "speciality": self.speciality,
            "experience_years": self.experience_years,
            "bio": self.bio,
            "available": self.available,
        }


class Slot(db.Model):
    __tablename__ = "slots"
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    slot_date = db.Column(db.Date, nullable=False)
    slot_time = db.Column(db.String(10), nullable=False)  # e.g. "09:00"
    is_booked = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "slot_date": self.slot_date.isoformat(),
            "slot_time": self.slot_time,
            "is_booked": self.is_booked,
        }


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("slots.id"), nullable=False, unique=True)
    reason = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), default="booked")  # booked | completed | cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor = db.relationship("Doctor", foreign_keys=[doctor_id])
    slot = db.relationship("Slot")

    def to_dict(self):
        return {
            "id": self.id,
            "patient": self.patient.name,
            "doctor": self.doctor.user.name,
            "speciality": self.doctor.speciality,
            "slot_date": self.slot.slot_date.isoformat(),
            "slot_time": self.slot.slot_time,
            "reason": self.reason,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
