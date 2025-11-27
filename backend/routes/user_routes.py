# parking_routes.py

from flask import Blueprint, request, jsonify, send_file, current_app
from models import db, ParkingLot, ParkingSpot, Reservation, User, ExportJob
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import math
import os

user_bp = Blueprint("user", __name__)

def get_cache():
    """Get cache instance from current app"""
    return current_app.extensions['cache']

@user_bp.route("/lots", methods=["GET"])
@jwt_required()
def list_available_lots():
    """
    List lots with available counts. Accessible to logged in users.
    CACHED: 60 seconds - Frequently accessed, changes moderately
    """
    cache = get_cache()
    
    # Create cache key that includes timestamp (rounded to 60 seconds)
    cache_key = f"user_lots_{int(datetime.utcnow().timestamp() // 60)}"
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return jsonify(cached_data), 200
    
    # If not in cache, fetch from database
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
    
    # Store in cache
    cache.get(cache_key, out, timeout=60)
    
    return jsonify(out), 200

@user_bp.route("/book", methods=["POST"])
@jwt_required()
def book_spot():
    """
    Book first available spot in a lot for the current user.
    Request body: {"lot_id": <int>}
    NO CACHE: Write operation that modifies data
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
        
        # INVALIDATE CACHE after booking - clear relevant cache patterns
        cache = get_cache()
        # Clear user lots cache by clearing all possible keys in the last minute
        current_minute = int(datetime.utcnow().timestamp() // 60)
        for i in range(2):  # Clear current and previous minute
            cache.delete(f"user_lots_{current_minute - i}")
            cache.delete(f"admin_lots_{int((current_minute - i) * 60 // 180)}")
        
        # Clear user's reservations cache
        for i in range(2):
            cache.delete(f"my_reservations_{user_id}_{current_minute - i}")
        
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
    NO CACHE: Write operation that modifies data
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
        # get spot available
        res.spot.status = "A"
        db.session.commit()
        
        # INVALIDATE CACHE after leaving
        cache = get_cache()
        current_minute = int(datetime.utcnow().timestamp() // 60)
        for i in range(2):
            cache.delete(f"user_lots_{current_minute - i}")
            cache.delete(f"admin_lots_{int((current_minute - i) * 60 // 180)}")
            cache.delete(f"my_reservations_{user_id}_{current_minute - i}")
        
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
    """
    Get user's reservations
    CACHED: 120 seconds per user - Personal data that changes occasionally
    """
    cache = get_cache()
    user_id = get_jwt_identity()
    
    # Create user-specific cache key with 2-minute buckets
    cache_key = f"my_reservations_{user_id}_{int(datetime.utcnow().timestamp() // 120)}"
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return jsonify(cached_data), 200
    
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
    out = []
    for r in reservations:
        out.append({
            "id": r.id,
            "spot_id": r.spot_id,
            "spot_number": r.spot.spot_number if r.spot else None,
            "lot_id": r.spot.lot_id if r.spot else None,
            "lot_name": r.spot.lot.name if r.spot and r.spot.lot else None,
            "parking_timestamp": r.parking_timestamp.isoformat() if r.parking_timestamp else None,
            "leaving_timestamp": r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
            "parking_cost": r.parking_cost,
            "status": r.status
        })
    
    cache.get(cache_key, out, timeout=120)
    return jsonify(out), 200


# ============= EXPORT ROUTES =============

@user_bp.route("/export/trigger", methods=["POST"])
@jwt_required()
def trigger_export():
    """
    Trigger CSV export job for current user
    NO CACHE: Trigger operation
    """
    from tasks.export_csv import export_user_reservations
    
    user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    if not user.email:
        return jsonify({"msg": "Email not get. Cannot send export notification."}), 400
    
    # Check if user has any pending or processing jobs
    existing_job = ExportJob.query.filter(
        ExportJob.user_id == user_id,
        ExportJob.status.in_(["pending", "processing"])
    ).first()
    
    if existing_job:
        return jsonify({
            "msg": "Export already in progress",
            "job_id": existing_job.id,
            "status": existing_job.status
        }), 409
    
    try:
        job = ExportJob(user_id=user_id, status="pending")
        db.session.add(job)
        db.session.commit()
        
        # Trigger async task
        task = export_user_reservations.delay(user_id, user.email, user.username)
        
        return jsonify({
            "msg": "Export job started",
            "job_id": job.id,
            "task_id": task.id,
            "status": "pending"
        }), 202
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error triggering export", "error": str(e)}), 500


@user_bp.route("/export/status", methods=["GET"])
@jwt_required()
def export_status():
    """
    Get status of user's export jobs
    CACHED: 30 seconds per user
    """
    cache = get_cache()
    user_id = get_jwt_identity()
    
    # Create user-specific cache key
    cache_key = f"export_status_{user_id}_{int(datetime.utcnow().timestamp() // 30)}"
    
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return jsonify(cached_data), 200
    
    jobs = ExportJob.query.filter_by(user_id=user_id).order_by(
        ExportJob.requested_at.desc()
    ).limit(10).all()
    
    out = []
    for job in jobs:
        out.append({
            "id": job.id,
            "status": job.status,
            "requested_at": job.requested_at.isoformat() if job.requested_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "file_available": job.status == "done" and job.file_path is not None
        })
    
    cache.get(cache_key, out, timeout=30)
    
    return jsonify(out), 200


@user_bp.route("/export/download/<int:job_id>", methods=["GET"])
@jwt_required()
def download_export(job_id):
    """
    Download CSV file for completed export job
    NO CACHE: File download
    """
    user_id = get_jwt_identity()
    
    job = ExportJob.query.filter_by(id=job_id, user_id=user_id).first()
    
    if not job:
        return jsonify({"msg": "Export job not found"}), 404
    
    if job.status != "done":
        return jsonify({"msg": "Export not ready yet", "status": job.status}), 400
    
    if not job.file_path or not os.path.exists(job.file_path):
        return jsonify({"msg": "Export file not found"}), 404
    
    try:
        return send_file(
            job.file_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=os.path.basename(job.file_path)
        )
    except Exception as e:
        return jsonify({"msg": "Error downloading file", "error": str(e)}), 500