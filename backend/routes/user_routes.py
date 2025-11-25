# parking_routes.py

from flask import Blueprint, request, jsonify
from models import db, ParkingLot, ParkingSpot, Reservation
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import math

user_bp = Blueprint("user", __name__)

@user_bp.route("/lots", methods=["GET"])
@jwt_required()
def list_available_lots():
    """
    List lots with available counts. Accessible to logged in users.
    """
    lots = ParkingLot.query.order_by(ParkingLot.created_at.desc()).all()
    out = []
                    
    for l in lots:
        total = l.number_of_spots
        occupied = l.spots.filter_by(status="O").count()
        available = total - occupied
        out.append({
            "id": l.id,
            "name": l.name,
            "price_per_hour": l.price_per_hour,
            "available_spots": available,
            "total_spots": total,
            "address": l.address,
            "pincode": l.pincode
        })
    return jsonify(out), 200

@user_bp.route("/book", methods=["POST"])
@jwt_required()
def book_spot():
    """
    Book first available spot in a lot for the current user.
    Request body: {"lot_id": <int>}
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    lot_id = data.get("lot_id")
    if not lot_id:
        return jsonify({"msg": "lot_id required"}), 400

    # Check if user already has an active reservation
    existing = Reservation.query.filter_by(user_id=user_id, status="active").first()
    if existing:
        return jsonify({"msg": "You already have an active reservation", "reservation_id": existing.id}), 409

    #Atomic attempt to allocate a spot.
    #We'll use a session transaction and re-check before commit (optimistic approach).

    try:
        with db.session.begin_nested():
            # find first available spot in the requested lot
            spot = ParkingSpot.query.filter_by(lot_id=lot_id, status="A").order_by(ParkingSpot.spot_number).with_for_update().first()

            if not spot:
                return jsonify({"msg": "no available spot in this lot"}), 409


            # Marking spot occupied and creating reservation
            spot.status = "O"
            reservation = Reservation(
                spot_id=spot.id,
                user_id=user_id,
                parking_timestamp=datetime.utcnow(),
                status="active",
                created_at=datetime.utcnow()
            )
            db.session.add(reservation)
        # commit transaction
        db.session.commit()
        return jsonify({
            "msg": "Parking spot booked successfully",
            "lot_id": lot_id,
            "reservation_id": reservation.id,
            "spot_id": spot.id,
            "spot_number": spot.spot_number
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error while booking", "error": str(e)}), 500

@user_bp.route("/leave", methods=["POST"])
@jwt_required()
def leave_spot():
    """
    Release an active reservation
    Request body: {"reservation_id": <int>}
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    reservation_id = data.get("reservation_id")

    if not reservation_id:
        return jsonify({"msg": "reservation_id required"}), 400

    res = Reservation.query.filter_by(id=reservation_id, user_id=user_id, status="active").first()
    if not res:
        return jsonify({"msg": "active reservation not found"}), 404

    try:
        res.leaving_timestamp = datetime.utcnow()
        duration = res.leaving_timestamp - res.parking_timestamp
        minutes = duration.total_seconds() / 60.0
        hours = math.ceil(minutes / 60.0) if minutes > 0 else 0
        price_per_hour = res.spot.lot.price_per_hour if res.spot and res.spot.lot else 0.0
        res.parking_cost = hours * price_per_hour
        res.status = "completed"
        # set spot available
        res.spot.status = "A"
        db.session.commit()
        return jsonify({
            "msg": "released",
            "parking_cost": res.parking_cost,
            "duration_minutes": minutes
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "error releasing reservation", "error": str(e)}), 500


@user_bp.route("/my_reservations", methods=["GET"])
@jwt_required()
def my_reservations():
    user_id = get_jwt_identity()
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
    out = []
    for r in reservations:
        out.append({
            "id": r.id,
            "spot_id": r.spot_id,
            "spot_number": r.spot.spot_number if r.spot else None,
            "lot_id": r.spot.lot_id if r.spot else None,
            "parking_timestamp": r.parking_timestamp.isoformat() if r.parking_timestamp else None,
            "leaving_timestamp": r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
            "parking_cost": r.parking_cost,
            "status": r.status
        })
    return jsonify(out), 200