import os
from datetime import datetime
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
db = SQLAlchemy()

# --User model--
class User(db.Model):
    __tablename__ = "users"         
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    role = db.Column(db.String(10), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reservations = db.relationship("Reservation", back_populates="user", lazy="dynamic")
    export_jobs = db.relationship("ExportJob", back_populates="user", lazy="dynamic")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# -- Parkinglot Model -- 
class ParkingLot(db.Model):
    __tablename__ = "parking_lots"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(250))
    pincode = db.Column(db.String(20))
    price_per_hour = db.Column(db.Float, nullable=False, default=0.0)
    number_of_spots = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    spots = db.relationship("ParkingSpot", back_populates="lot", cascade="all, delete-orphan", lazy="dynamic")


# -- ParkingSpot Model--
class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), nullable=False, default="A")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lot = db.relationship("ParkingLot", back_populates="spots")
    reservation = db.relationship("Reservation", back_populates="spot", uselist=False)


# -- Reservation Model --
class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spots.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reservations")
    spot = db.relationship("ParkingSpot", back_populates="reservation")

# --ExportJobs Model--
class ExportJob(db.Model):
    __tablename__ = "export_jobs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending/processing/done/failed
    file_path = db.Column(db.String(255), nullable=True)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # relationship back to user (optional)
    user = db.relationship("User", back_populates="export_jobs")