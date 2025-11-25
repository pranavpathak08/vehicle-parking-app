import os
from celery import Celery
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "vehicle_parking_app",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.daily_reminder"]  # explicitly include task
)

celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    beat_schedule={
        "daily-reminder-task": {
            "task": "tasks.daily_reminder.send_daily_reminder",
            "schedule": crontab(hour=18, minute=0),
            "args": ()
        }
    }
)

celery.autodiscover_tasks(["tasks"])
