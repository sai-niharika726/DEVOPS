from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "mobile": self.mobile,
            "dob": self.dob,
        }


class PassApplication(db.Model):
    __tablename__ = "pass_applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    candidate_name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), nullable=False)  # regular | student | oldage | handicapped

    base_fare = db.Column(db.Integer, nullable=False)
    discount_pct = db.Column(db.Integer, nullable=False)
    payable = db.Column(db.Integer, nullable=False)

    # Only the last 4 digits are stored for reference; the raw Aadhar number is never persisted.
    aadhar_last4 = db.Column(db.String(4), nullable=True)
    aadhar_name = db.Column(db.String(120), nullable=True)

    status = db.Column(db.String(30), default="pending_verification")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_name": self.candidate_name,
            "mobile": self.mobile,
            "age": self.age,
            "category": self.category,
            "base_fare": self.base_fare,
            "discount_pct": self.discount_pct,
            "payable": self.payable,
            "aadhar_last4": self.aadhar_last4,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
        }
