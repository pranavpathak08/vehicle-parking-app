from celery_app import celery
from flask_mail import Message
from datetime import datetime, timedelta
import os

from app import create_app  # absolute import
from models import User, Reservation
from flask_mail import Mail

@celery.task(name="tasks.daily_reminder.send_daily_reminder")
def send_daily_reminder():
    """Daily reminder at 6 PM to users who haven't booked parking today"""

    app = create_app()
    mail = Mail(app)

    with app.app_context():
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        users = User.query.filter_by(role="user").all()
        sent_count = 0

        for user in users:
            if not user.email:
                continue

            today_reservation = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.parking_timestamp >= today_start,
                Reservation.parking_timestamp < today_end
            ).first()

            if not today_reservation:
                try:
                    msg = Message(
                        subject="🚗 Daily Parking Reminder",
                        sender=os.getenv("MAIL_USERNAME"),
                        recipients=[user.email]
                    )
                    msg.html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2>Hello {user.username}!</h2>
                        <p>We noticed you haven't booked a parking spot today.</p>
                        <p>If you need parking, please book your spot at your earliest convenience.</p>
                        <br>
                        <p>Best regards,<br>Vehicle Parking Management</p>
                    </body>
                    </html>
                    """
                    mail.send(msg)
                    sent_count += 1
                    print(f"✓ Sent reminder to {user.email}")
                except Exception as e:
                    print(f"✗ Failed to send to {user.email}: {str(e)}")

        return f"Daily reminders sent to {sent_count} users"
