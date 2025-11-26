import os
import sys
from celery import Celery
from dotenv import load_dotenv
from celery.schedules import crontab

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "vehicle_parking_app",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    beat_schedule={
        # Daily reminder at 6 PM
        "daily-reminder-task": {
            "task": "tasks.daily_reminder.send_daily_reminder",
            "schedule": crontab(hour=18, minute=0),
            "args": ()
        },
        # Monthly report on 1st of every month at 9 AM
        # IMPORTANT: Task name must match the folder name (monthly_reminder, not monthly_report)
        "monthly-report-task": {
            "task": "tasks.monthly_report.send_monthly_report",
            "schedule": crontab(day_of_month=1, hour=9, minute=0),
            "args": ()
        }
    }
)

# DO NOT import tasks here - this causes circular imports
# Tasks will be auto-discovered when imported elsewhere