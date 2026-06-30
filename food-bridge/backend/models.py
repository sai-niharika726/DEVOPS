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
    role = db.Column(db.String(20), nullable=False)  # 'donor' or 'volunteer'
    org_name = db.Column(db.String(160), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    donations = db.relationship("Donation", backref="donor", lazy=True)
    claims = db.relationship("Claim", backref="volunteer", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "org_name": self.org_name,
        }


class Donation(db.Model):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.String(100), nullable=False)  # e.g. "Serves 25"
    food_type = db.Column(db.String(20), default="veg")   # veg / non_veg / mixed
    pickup_location = db.Column(db.String(200), nullable=False)
    pickup_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="available")  # available, claimed, completed, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    claim = db.relationship("Claim", backref="donation", uselist=False, lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "quantity": self.quantity,
            "food_type": self.food_type,
            "pickup_location": self.pickup_location,
            "pickup_deadline": self.pickup_deadline.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "donor": {
                "id": self.donor.id,
                "name": self.donor.name,
                "org_name": self.donor.org_name,
            } if self.donor else None,
        }


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey("donations.id"), nullable=False, unique=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="claimed")  # claimed, picked_up, completed, cancelled
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "donation_id": self.donation_id,
            "volunteer_id": self.volunteer_id,
            "status": self.status,
            "claimed_at": self.claimed_at.isoformat(),
        }
