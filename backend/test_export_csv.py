import os
import sys

# Add backend folder to PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks.export_csv import export_user_reservations
from app import create_app
from models import User

print("Testing CSV export...")
print("=" * 50)

# Get a test user
app = create_app()
with app.app_context():
    # Find first regular user
    user = User.query.filter_by(email="ppathak2002@gmail.com").first()
    
    if not user:
        print("✗ No regular user found in database!")
        print("Please create a user first using /api/auth/register")
        sys.exit(1)
    
    if not user.email:
        print(f"✗ User '{user.username}' has no email set!")
        sys.exit(1)
    
    print(f"Using user: {user.username} (ID: {user.id}, Email: {user.email})")
    print("-" * 50)
    
    # Trigger export
    result = export_user_reservations.delay(user.id, user.email, user.username)
    print(f"Task ID: {result.id}")
    print("Waiting for result...")
    
    try:
        output = result.get(timeout=60)
        print(f"✓ Success: {output}")
        print("\nCheck:")
        print("1. Your email for the export notification")
        print("2. The backend/exports/ directory for the CSV file")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()