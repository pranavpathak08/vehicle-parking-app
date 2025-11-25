import os
import sys
from datetime import datetime, timedelta

# Add backend folder to PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Reservation, ParkingSpot, ParkingLot
import random

app = create_app()

with app.app_context():
    print("Creating test data for monthly report...")
    print("=" * 60)
    
    # Get or create a test user with email
    user = User.query.filter_by(email="ppathak2002@gmail.com").first()
    
    print(f"✓ Using user: {user.username} (ID: {user.id})")
    print(f"  Email: {user.email}")
    print()
    
    # Get available parking spots
    spots = ParkingSpot.query.filter_by(status="A").limit(5).all()
    
    if not spots:
        print("❌ No available parking spots found!")
        print("   Please create a parking lot first using admin endpoints")
        sys.exit(1)
    
    print(f"✓ Found {len(spots)} available parking spots")
    print()
    
    # Calculate previous month date range
    today = datetime.utcnow()
    first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_name = last_day_prev_month.strftime("%B %Y")
    print(f"📅 Creating reservations for: {month_name}")
    print(f"   Date range: {first_day_prev_month.date()} to {last_day_prev_month.date()}")
    print()
    
    # Delete existing test reservations for this user in previous month (if any)
    existing = Reservation.query.filter(
        Reservation.user_id == user.id,
        Reservation.parking_timestamp >= first_day_prev_month,
        Reservation.parking_timestamp < first_day_current_month
    ).all()
    
    if existing:
        print(f"🗑️  Deleting {len(existing)} existing test reservations...")
        for r in existing:
            db.session.delete(r)
        db.session.commit()
    
    # Create 5-10 completed reservations in previous month
    num_reservations = random.randint(5, 10)
    created_count = 0
    
    print(f"📝 Creating {num_reservations} test reservations...")
    print()
    
    for i in range(num_reservations):
        # Random day in previous month
        day = random.randint(1, last_day_prev_month.day)
        hour = random.randint(8, 18)  # Business hours
        minute = random.randint(0, 59)
        
        parking_time = first_day_prev_month.replace(day=day, hour=hour, minute=minute)
        
        # Random parking duration (1-5 hours)
        duration_hours = random.randint(1, 5)
        leaving_time = parking_time + timedelta(hours=duration_hours)
        
        # Pick a random spot
        spot = random.choice(spots)
        
        # Get price from parking lot
        price_per_hour = spot.lot.price_per_hour if spot.lot else 50.0
        parking_cost = duration_hours * price_per_hour
        
        # Create completed reservation
        reservation = Reservation(
            spot_id=spot.id,
            user_id=user.id,
            parking_timestamp=parking_time,
            leaving_timestamp=leaving_time,
            parking_cost=parking_cost,
            status="completed",
            created_at=parking_time
        )
        
        db.session.add(reservation)
        created_count += 1
        
        print(f"  {i+1}. {parking_time.strftime('%d %b, %I:%M %p')} → "
              f"{leaving_time.strftime('%I:%M %p')} "
              f"({duration_hours}h) - Spot #{spot.spot_number} - ₹{parking_cost:.2f}")
    
    # Also create 1 active reservation in previous month (not yet completed)
    day = random.randint(last_day_prev_month.day - 5, last_day_prev_month.day)
    parking_time = first_day_prev_month.replace(day=day, hour=14, minute=0)
    
    active_spot = random.choice(spots)
    active_reservation = Reservation(
        spot_id=active_spot.id,
        user_id=user.id,
        parking_timestamp=parking_time,
        leaving_timestamp=None,
        parking_cost=None,
        status="active",
        created_at=parking_time
    )
    db.session.add(active_reservation)
    created_count += 1
    
    print(f"\n  {created_count}. {parking_time.strftime('%d %b, %I:%M %p')} → "
          f"ACTIVE - Spot #{active_spot.spot_number}")
    
    # Commit all reservations
    db.session.commit()
    
    print()
    print("=" * 60)
    print(f"✅ Successfully created {created_count} test reservations!")
    print()
    
    # Calculate and display statistics
    total_cost = sum(r.parking_cost or 0 for r in Reservation.query.filter(
        Reservation.user_id == user.id,
        Reservation.parking_timestamp >= first_day_prev_month,
        Reservation.parking_timestamp < first_day_current_month
    ).all())
    
    completed = Reservation.query.filter(
        Reservation.user_id == user.id,
        Reservation.status == "completed",
        Reservation.parking_timestamp >= first_day_prev_month,
        Reservation.parking_timestamp < first_day_current_month
    ).count()
    
    active = Reservation.query.filter(
        Reservation.user_id == user.id,
        Reservation.status == "active",
        Reservation.parking_timestamp >= first_day_prev_month,
        Reservation.parking_timestamp < first_day_current_month
    ).count()
    
    print("📊 Test Data Summary:")
    print(f"   User: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Month: {month_name}")
    print(f"   Total Reservations: {created_count}")
    print(f"   Completed: {completed}")
    print(f"   Active: {active}")
    print(f"   Total Spent: ₹{total_cost:.2f}")
    print()
    print("🚀 Now you can test the monthly report:")
    print(f"   python test_monthly_report.py")
    print()
    print(f"📧 Email will be sent to: {user.email}")
    print("=" * 60)