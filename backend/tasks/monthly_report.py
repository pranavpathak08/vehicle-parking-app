from celery_app import celery
from flask_mail import Message, Mail
from datetime import datetime, timedelta
from sqlalchemy import func
import os
import calendar

@celery.task(name="tasks.monthly_reminder.send_monthly_report", bind=False)
def send_monthly_report():
    """Send monthly activity report to all users on the 1st of each month"""
    
    from app import create_app
    from models import User, Reservation, ParkingLot, ParkingSpot
    
    app = create_app()
    mail = Mail(app)

    with app.app_context():
        # Get previous month's date range
        today = datetime.utcnow()
        first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_prev_month = first_day_current_month - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        month_name = last_day_prev_month.strftime("%B %Y")
        
        users = User.query.filter_by(role="user").all()
        sent_count = 0

        for user in users:
            if not user.email:
                continue

            # Get user's reservations for previous month
            reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.parking_timestamp >= first_day_prev_month,
                Reservation.parking_timestamp < first_day_current_month
            ).all()

            if not reservations:
                # Skip users with no activity
                continue

            # Calculate statistics
            total_bookings = len(reservations)
            total_cost = sum(r.parking_cost or 0 for r in reservations)
            completed_bookings = len([r for r in reservations if r.status == "completed"])
            active_bookings = len([r for r in reservations if r.status == "active"])
            
            # Find most used parking lot
            lot_usage = {}
            total_hours = 0
            
            for r in reservations:
                if r.spot and r.spot.lot:
                    lot_name = r.spot.lot.name
                    lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
                
                # Calculate total parking duration
                if r.leaving_timestamp and r.parking_timestamp:
                    duration = r.leaving_timestamp - r.parking_timestamp
                    total_hours += duration.total_seconds() / 3600
            
            most_used_lot = max(lot_usage.items(), key=lambda x: x[1]) if lot_usage else ("N/A", 0)
            avg_cost_per_booking = total_cost / total_bookings if total_bookings > 0 else 0
            
            # Generate HTML report
            html_content = generate_monthly_report_html(
                user.username,
                month_name,
                total_bookings,
                completed_bookings,
                active_bookings,
                total_cost,
                avg_cost_per_booking,
                most_used_lot,
                total_hours,
                reservations
            )

            try:
                msg = Message(
                    subject=f"📊 Your Monthly Parking Report - {month_name}",
                    sender=os.getenv("MAIL_USERNAME"),
                    recipients=[user.email]
                )
                msg.html = html_content
                mail.send(msg)
                sent_count += 1
                print(f"✓ Sent monthly report to {user.email}")
            except Exception as e:
                print(f"✗ Failed to send to {user.email}: {str(e)}")

        return f"Monthly reports sent to {sent_count} users for {month_name}"


def generate_monthly_report_html(username, month_name, total_bookings, completed_bookings, 
                                 active_bookings, total_cost, avg_cost, most_used_lot, 
                                 total_hours, reservations):
    """Generate HTML email template for monthly report"""
    
    # Build reservation details table
    reservation_rows = ""
    for r in reservations[:10]:  # Show latest 10 reservations
        lot_name = r.spot.lot.name if r.spot and r.spot.lot else "N/A"
        spot_num = r.spot.spot_number if r.spot else "N/A"
        parking_time = r.parking_timestamp.strftime("%d %b, %I:%M %p") if r.parking_timestamp else "N/A"
        leaving_time = r.leaving_timestamp.strftime("%d %b, %I:%M %p") if r.leaving_timestamp else "Active"
        cost = f"₹{r.parking_cost:.2f}" if r.parking_cost else "₹0.00"
        
        reservation_rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{lot_name}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{spot_num}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{parking_time}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{leaving_time}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{cost}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
        <div style="max-width: 650px; margin: 30px auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 28px;">🚗 Monthly Parking Report</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">{month_name}</p>
            </div>
            
            <!-- Greeting -->
            <div style="padding: 30px;">
                <h2 style="color: #333; margin-top: 0;">Hello {username}!</h2>
                <p style="color: #666; line-height: 1.6;">Here's your parking activity summary for {month_name}. We've compiled your usage statistics and spending insights.</p>
            </div>
            
            <!-- Statistics Cards -->
            <div style="padding: 0 30px 20px 30px; display: flex; flex-wrap: wrap; gap: 15px;">
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <div style="font-size: 32px; font-weight: bold; color: #667eea;">{total_bookings}</div>
                    <div style="color: #666; font-size: 14px; margin-top: 5px;">Total Bookings</div>
                </div>
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">
                    <div style="font-size: 32px; font-weight: bold; color: #28a745;">₹{total_cost:.2f}</div>
                    <div style="color: #666; font-size: 14px; margin-top: 5px;">Total Spent</div>
                </div>
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <div style="font-size: 32px; font-weight: bold; color: #ffc107;">{total_hours:.1f}h</div>
                    <div style="color: #666; font-size: 14px; margin-top: 5px;">Total Hours</div>
                </div>
            </div>
            
            <!-- Key Insights -->
            <div style="padding: 20px 30px; background: #f8f9fa; margin: 20px 30px; border-radius: 8px;">
                <h3 style="color: #333; margin-top: 0;">📈 Key Insights</h3>
                <ul style="color: #666; line-height: 1.8; padding-left: 20px;">
                    <li><strong>Most Used Parking Lot:</strong> {most_used_lot[0]} ({most_used_lot[1]} visits)</li>
                    <li><strong>Completed Bookings:</strong> {completed_bookings}</li>
                    <li><strong>Active Bookings:</strong> {active_bookings}</li>
                    <li><strong>Average Cost per Booking:</strong> ₹{avg_cost:.2f}</li>
                </ul>
            </div>
            
            <!-- Recent Activity -->
            <div style="padding: 20px 30px;">
                <h3 style="color: #333;">📋 Recent Activity (Last 10 Bookings)</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <thead>
                        <tr style="background-color: #667eea; color: white;">
                            <th style="padding: 12px; text-align: left;">Lot</th>
                            <th style="padding: 12px; text-align: left;">Spot</th>
                            <th style="padding: 12px; text-align: left;">Check-in</th>
                            <th style="padding: 12px; text-align: left;">Check-out</th>
                            <th style="padding: 12px; text-align: left;">Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reservation_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Footer -->
            <div style="padding: 30px; background-color: #f8f9fa; text-align: center; color: #666;">
                <p style="margin: 0; font-size: 14px;">Thank you for using Vehicle Parking Management</p>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">This is an automated report. Please do not reply to this email.</p>
            </div>
            
        </div>
    </body>
    </html>
    """
    return html