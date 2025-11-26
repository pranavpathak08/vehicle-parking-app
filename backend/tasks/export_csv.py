from celery_app import celery
from flask_mail import Message, Mail
from datetime import datetime
import pandas as pd
import os

@celery.task(name="tasks.export_csv.export_user_reservations", bind=True)
def export_user_reservations(self, user_id, user_email, username):
    """
    Export user's parking reservation history to CSV
    This is triggered by the user from their dashboard
    """
    
    from app import create_app
    from models import Reservation, ExportJob
    
    app = create_app()
    mail = Mail(app)
    
    # Update job status to processing
    with app.app_context():
        job = ExportJob.query.get(self.request.id.split('-')[-1]) if '-' in str(self.request.id) else None
        # For simplicity, we'll track by user_id and update the latest pending job
        job = ExportJob.query.filter_by(user_id=user_id, status="pending").order_by(ExportJob.requested_at.desc()).first()
        
        if job:
            job.status = "processing"
            from models import db
            db.session.commit()

    try:
        with app.app_context():
            # Fetch all user reservations
            reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
            
            if not reservations:
                # Update job status
                if job:
                    job.status = "failed"
                    from models import db
                    db.session.commit()
                return "No reservations found for user"
            
            # Prepare data for CSV
            data = []
            for r in reservations:
                lot_name = r.spot.lot.name if r.spot and r.spot.lot else "N/A"
                lot_address = r.spot.lot.address if r.spot and r.spot.lot else "N/A"
                spot_number = r.spot.spot_number if r.spot else "N/A"
                
                # Calculate duration
                duration = ""
                if r.leaving_timestamp and r.parking_timestamp:
                    delta = r.leaving_timestamp - r.parking_timestamp
                    hours = delta.total_seconds() / 3600
                    duration = f"{hours:.2f} hours"
                elif r.status == "active":
                    duration = "Active"
                
                data.append({
                    "Reservation ID": r.id,
                    "Parking Lot": lot_name,
                    "Address": lot_address,
                    "Spot Number": spot_number,
                    "Check-in Time": r.parking_timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.parking_timestamp else "N/A",
                    "Check-out Time": r.leaving_timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.leaving_timestamp else "N/A",
                    "Duration": duration,
                    "Cost (₹)": f"{r.parking_cost:.2f}" if r.parking_cost else "0.00",
                    "Status": r.status.capitalize(),
                    "Booking Date": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "N/A"
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
            os.makedirs(exports_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"parking_history_{user_id}_{timestamp}.csv"
            filepath = os.path.join(exports_dir, filename)
            
            # Save to CSV
            df.to_csv(filepath, index=False)
            
            # Update job status
            with app.app_context():
                if job:
                    job.status = "done"
                    job.file_path = filepath
                    job.completed_at = datetime.utcnow()
                    from models import db
                    db.session.commit()
            
            # Send email notification with CSV attachment
            try:
                msg = Message(
                    subject="📄 Your Parking History Export is Ready",
                    sender=os.getenv("MAIL_USERNAME"),
                    recipients=[user_email]
                )
                
                msg.html = f"""
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 30px; border-radius: 10px;">
                        <h2 style="color: #667eea;">✓ Export Complete!</h2>
                        <p>Hello {username},</p>
                        <p>Your parking history export has been successfully generated.</p>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #333;">📊 Export Details</h3>
                            <ul style="color: #666;">
                                <li><strong>Total Reservations:</strong> {len(reservations)}</li>
                                <li><strong>File Format:</strong> CSV</li>
                                <li><strong>Generated:</strong> {datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")}</li>
                            </ul>
                        </div>
                        
                        <p>Your parking history is attached to this email as a CSV file. You can open it with Excel, Google Sheets, or any spreadsheet application.</p>
                        
                        <p style="margin-top: 30px; color: #666; font-size: 14px;">
                            Best regards,<br>
                            Vehicle Parking Management Team
                        </p>
                    </div>
                </body>
                </html>
                """
                
                # Attach CSV file
                with app.open_resource(filepath) as fp:
                    msg.attach(filename, "text/csv", fp.read())
                
                mail.send(msg)
                print(f"✓ Sent export notification with CSV to {user_email}")
                
            except Exception as e:
                print(f"✗ Failed to send email: {str(e)}")
                # Don't fail the task if email fails
            
            return f"Successfully exported {len(reservations)} reservations for user {user_id}"
            
    except Exception as e:
        # Update job status to failed
        with app.app_context():
            if job:
                job.status = "failed"
                from models import db
                db.session.commit()
        
        print(f"✗ Export failed: {str(e)}")
        raise e