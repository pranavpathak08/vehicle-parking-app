from celery_app import celery

# Import all tasks to register them with Celery
# This is safe here because we import celery_app FIRST (which has no task imports)
from tasks.daily_reminder import send_daily_reminder
from tasks.monthly_report import send_monthly_report
from tasks.export_csv import export_user_reservations

# Make tasks available when this module is imported
__all__ = ['celery', 'send_daily_reminder', 'send_monthly_report', 'export_user_reservations']