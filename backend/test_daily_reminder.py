import os
import sys

# Add backend folder to PYTHONPATH so imports work
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks.daily_reminder import send_daily_reminder

print("Testing daily reminder...")
result = send_daily_reminder.delay()
print(f"Task ID: {result.id}")
print("Waiting for result...")

try:
    output = result.get(timeout=30)
    print(f"✓ Success: {output}")
except Exception as e:
    print(f"✗ Error: {str(e)}")
