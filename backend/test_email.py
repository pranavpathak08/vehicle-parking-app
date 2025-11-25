import os
from dotenv import load_dotenv
from app import create_app, mail
from flask_mail import Message

load_dotenv()

app = create_app()

with app.app_context():
    print("Testing email configuration...")
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
    print(f"MAIL_USE_SSL: {app.config['MAIL_USE_SSL']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_PASSWORD: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'NOT SET'}")
    
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("\n❌ ERROR: MAIL_USERNAME or MAIL_PASSWORD not set in .env file!")
        exit(1)
    
    try:
        msg = Message(
            subject="Test Email from Vehicle Parking App",
            sender=app.config['MAIL_USERNAME'],
            recipients=["ppathak2002@gmail.com"]
        )
        msg.body = "This is a test email. If you received this, your email configuration is working!"
        msg.html = """
        <html>
            <body>
                <h2>Test Email</h2>
                <p>This is a test email from your Vehicle Parking App.</p>
                <p>If you received this, your email configuration is working correctly! ✓</p>
            </body>
        </html>
        """
        
        mail.send(msg)
        print("\n✓ Email sent successfully!")
        print("Check your inbox at ppathak2002@gmail.com")
        
    except Exception as e:
        print(f"\n✗ Failed to send email: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you're using Gmail App Password (not regular password)")
        print("2. Check your .env file has correct credentials")
        print("3. Make sure MAIL_USE_TLS=True and MAIL_USE_SSL=False")