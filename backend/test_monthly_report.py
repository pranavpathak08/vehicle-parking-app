import os
import sys
from datetime import datetime, timedelta

# Add backend folder to PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks.monthly_report import send_monthly_report
from app import create_app
from models import User, Reservation

print("Testing monthly report...")
print("=" * 60)

# First, check what data we have
app = create_app()
with app.app_context():
    # Calculate previous month
    today = datetime.utcnow()
    first_day_current = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_prev = first_day_current - timedelta(days=1)
    first_day_prev = last_day_prev.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_name = last_day_prev.strftime("%B %Y")
    
    print(f"📅 Report Period: {month_name}")
    print(f"   From: {first_day_prev.date()}")
    print(f"   To: {last_day_prev.date()}")
    print()
    
    # Check users with reservations
    users = User.query.filter_by(role="user").all()
    users_with_data = 0
    
    print(f"👥 Checking {len(users)} users for activity...")
    print()
    
    for user in users:
        reservations = Reservation.query.filter(
            Reservation.user_id == user.id,
            Reservation.parking_timestamp >= first_day_prev,
            Reservation.parking_timestamp < first_day_current
        ).all()
        
        if reservations:
            users_with_data += 1
            total_cost = sum(r.parking_cost or 0 for r in reservations)
            print(f"  ✓ {user.username} - {len(reservations)} reservations, ₹{total_cost:.2f}")
            print(f"    Email: {user.email or 'NOT SET ⚠️'}")
        else:
            print(f"  ✗ {user.username} - No activity in {month_name}")
    
    print()
    print(f"📊 Summary: {users_with_data} user(s) will receive reports")
    
    if users_with_data == 0:
        print()
        print("⚠️  WARNING: No users with activity found!")
        print("   Run 'python create_test_data.py' to create sample data")
        print("=" * 60)
        sys.exit(0)
    
    print()

print("-" * 60)
print("🚀 Triggering monthly report task...")
print()

result = send_monthly_report.delay()
print(f"Task ID: {result.id}")
print("Waiting for result...")
print()

try:
    output = result.get(timeout=60)
    print(f"✅ Success: {output}")
    print()
    print("📧 Check your email inbox for the monthly report!")
    print("=" * 60)
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    print("=" * 60)