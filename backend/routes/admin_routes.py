# admin_routes.py
from flask import Blueprint, request, jsonify
from models import db, ParkingLot, ParkingSpot, Reservation, User
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from sqlalchemy import func
from functools import wraps

admin_bp = Blueprint("admin", __name__)

# Import cache from app
from app import cache

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"msg": "admin only"}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route("/lots", methods=["POST"])
@admin_required
def create_lot():
    """
    Create a new parking lot
    NO CACHE: Write operation
    """
    data = request.get_json() or {}
    name = data.get("name")
    price_per_hour = float(data.get("price_per_hour", 0.0))
    number_of_spots = int(data.get("number_of_spots", 0))
    address = data.get("address")
    pincode = data.get("pincode")

    if not name or number_of_spots <= 0:
        return jsonify({"msg": "name and number_of_spots (>0) required"}), 400

    lot = ParkingLot(
        name=name,
        address=address,
        pincode=pincode,
        price_per_hour=price_per_hour,
        number_of_spots=number_of_spots,
        created_at=datetime.utcnow()
    )

    try:
        db.session.add(lot)
        db.session.flush()

        spots = []
        for i in range(1, number_of_spots + 1):
            spot = ParkingSpot(lot_id=lot.id, spot_number=i, status="A", created_at=datetime.utcnow())
            db.session.add(spot)
            spots.append(spot)
        db.session.commit()
        
        # INVALIDATE CACHE after creating lot
        cache.delete_memoized(list_lots)
        
        return jsonify({
            "msg": "lot created",
            "lot_id": lot.id,
            "spots_created": len(spots)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "error creating lot", "error": str(e)}), 500

@admin_bp.route("/lots", methods=["GET"])
@admin_required
@cache.cached(timeout=180, key_prefix='admin_lots')  # Cache for 3 minutes
def list_lots():
    """
    List all parking lots with availability
    CACHED: 180 seconds - Admin dashboard data
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
            "number_of_spots": total,
            "occupied": occupied,
            "available": available,
            "address": l.address,
            "pincode": l.pincode,
            "created_at": l.created_at.isoformat()
        })
    return jsonify(out), 200


@admin_bp.route("/lots/<int:lot_id>/spots", methods=["GET"])
@admin_required
@cache.memoize(timeout=60)  # Cache for 60 seconds per lot
def list_spots_for_lot(lot_id):
    """
    List all spots in a parking lot
    CACHED: 60 seconds per lot - Spot status changes moderately
    """
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"msg": "lot not found"}), 404

    spots = lot.spots.order_by(ParkingSpot.spot_number).all()
    out = []

    for s in spots:
        spot_info = {
            "id": s.id,
            "spot_number": s.spot_number,
            "status": s.status,
            "created_at": s.created_at.isoformat()
        }

        # include current reservation info if occupied
        if s.status == "O" and s.reservation:
            r = s.reservation
            spot_info["reservation"] = {
                "reservation_id": r.id,
                "user_id": r.user_id,
                "parking_timestamp": r.parking_timestamp.isoformat() if r.parking_timestamp else None,
                "status": r.status
            }
        out.append(spot_info)
    return jsonify({"lot": {"id": lot.id, "name":lot.name}, "spots":out}), 200


@admin_bp.route("/lots/<int:lot_id>", methods=["PUT"])
@admin_required
def update_lot(lot_id):
    """
    Update parking lot details
    NO CACHE: Write operation
    """
    data = request.get_json() or {}
    lot = ParkingLot.query.get(lot_id)

    if not lot:
        return jsonify({"msg": "lot not found"}), 404

    name = data.get("name")
    price = data.get("price_per_hour")
    address = data.get("address")
    pincode = data.get("pincode")
    new_count = data.get("number_of_spots")

    try:
        if name:
            lot.name = name
        if price is not None:
            lot.price_per_hour = float(price)
        if address is not None:
            lot.address = address
        if pincode is not None:
            lot.pincode = pincode

        if new_count is not None:
            new_count = int(new_count)
            if new_count < 0:
                return jsonify({"msg": "number_of_spots must be >= 0"}), 400

            current_count = lot.number_of_spots
            if new_count == current_count:
                pass
            elif new_count > current_count:
                start = 0
                last_spot = lot.spots.order_by(ParkingSpot.spot_number.desc()).first()
                if last_spot:
                    start = last_spot.spot_number

                spots_to_add = new_count - current_count
                for i in range(1, spots_to_add + 1):
                    sn = start + i
                    spot = ParkingSpot(lot_id=lot.id, spot_number=sn, status="A", created_at=datetime.utcnow())
                    db.session.add(spot)    
                lot.number_of_spots = new_count
            else:
                remove_count = current_count - new_count
                spots_to_remove = lot.spots.filter_by().order_by(ParkingSpot.spot_number.desc()).limit(remove_count).all()

                for s in spots_to_remove:
                    if s.status != "A":
                        return jsonify({"msg": "cannot decrease number_of_spots: some spots to remove are occupied"}), 400
                
                for s in spots_to_remove:
                    db.session.delete(s)
                lot.number_of_spots = new_count

        db.session.commit()
        
        # INVALIDATE CACHE after updating lot
        cache.delete_memoized(list_lots)
        cache.delete_memoized(list_spots_for_lot, lot_id)
        
        return jsonify({"msg": "lot updated", "lot_id": lot.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "error updating lot", "error": str(e)}), 500


@admin_bp.route("/lots/<int:lot_id>", methods=["DELETE"])
@admin_required
def delete_lot(lot_id):
    """
    Delete a parking lot
    NO CACHE: Write operation
    """
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"msg": "lot not found"}), 404

    occupied_spots = lot.spots.filter_by(status="O").count()
    active_reservations = Reservation.query.join(ParkingSpot, Reservation.spot_id == ParkingSpot.id).filter(ParkingSpot.lot_id == lot_id, Reservation.status=="active").count()

    if occupied_spots > 0 or active_reservations > 0:
        return jsonify({"msg": "cannot delete lot while spots are occupied or active reservations exist"}), 400

    try:
        db.session.delete(lot)
        db.session.commit()
        
        # INVALIDATE CACHE after deleting lot
        cache.delete_memoized(list_lots)
        cache.delete_memoized(list_spots_for_lot, lot_id)
        
        return jsonify({"msg": "lot deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "error deleting lot", "error":str(e)}), 500


# ============= DASHBOARD/ANALYTICS ROUTES (Heavily Cached) =============

@admin_bp.route("/dashboard/stats", methods=["GET"])
@admin_required
@cache.cached(timeout=300, key_prefix='admin_dashboard_stats')  # Cache for 5 minutes
def dashboard_stats():
    """
    Get dashboard statistics
    CACHED: 300 seconds - Expensive aggregation queries
    """
    try:
        # Total parking lots
        total_lots = ParkingLot.query.count()
        
        # Total spots
        total_spots = db.session.query(func.sum(ParkingLot.number_of_spots)).scalar() or 0
        
        # Occupied spots
        occupied_spots = ParkingSpot.query.filter_by(status="O").count()
        
        # Available spots
        available_spots = total_spots - occupied_spots
        
        # Active reservations
        active_reservations = Reservation.query.filter_by(status="active").count()
        
        # Total users
        total_users = User.query.filter_by(role="user").count()
        
        # Today's revenue
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.leaving_timestamp >= today_start,
            Reservation.status == "completed"
        ).scalar() or 0
        
        # This month's revenue
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.leaving_timestamp >= month_start,
            Reservation.status == "completed"
        ).scalar() or 0
        
        return jsonify({
            "total_lots": total_lots,
            "total_spots": int(total_spots),
            "occupied_spots": occupied_spots,
            "available_spots": available_spots,
            "occupancy_rate": round((occupied_spots / total_spots * 100) if total_spots > 0 else 0, 2),
            "active_reservations": active_reservations,
            "total_users": total_users,
            "today_revenue": round(today_revenue, 2),
            "month_revenue": round(month_revenue, 2)
        }), 200
        
    except Exception as e:
        return jsonify({"msg": "error fetching stats", "error": str(e)}), 500