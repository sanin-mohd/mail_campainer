#!/usr/bin/env python
"""
Test Gmail SMTP Configuration
Send a test email using Gmail SMTP to verify configuration.

Usage:
    python test_gmail.py recipient@example.com
    python test_gmail.py recipient@example.com "Custom Subject" "Custom Message"
"""
import os
import sys
import django
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailer_project.settings')
django.setup()

from django.conf import settings


def send_test_email_gmail(recipient_email, subject=None, message=None):
    """
    Send a test email using Gmail SMTP
    
    Args:
        recipient_email: Email address to send to
        subject: Email subject (optional)
        message: Email message (optional)
    """
    
    print("=" * 70)
    print("Testing Gmail SMTP Configuration")
    print("=" * 70)
    
    # Check Gmail configuration
    if not getattr(settings, 'EMAIL_HOST_USER', None):
        print("\n❌ ERROR: EMAIL_HOST_USER not configured")
        print("Add EMAIL_HOST_USER to your .env file")
        return False
    
    if not getattr(settings, 'EMAIL_HOST_PASSWORD', None):
        print("\n❌ ERROR: EMAIL_HOST_PASSWORD not configured")
        print("Add EMAIL_HOST_PASSWORD (App Password) to your .env file")
        return False
    
    # Display configuration
    print(f"\n📧 Gmail SMTP Settings:")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   Username: {settings.EMAIL_HOST_USER}")
    print(f"   Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # Prepare email
    from_email = settings.EMAIL_HOST_USER
    to_email = recipient_email
    
    if not subject:
        subject = "✅ Gmail SMTP Test - Configuration Successful!"
    
    if not message:
        message = f"""
Hello!

This is a test email sent using Gmail SMTP from your Campaign System.

Configuration Details:
- SMTP Host: {settings.EMAIL_HOST}
- Port: {settings.EMAIL_PORT}
- From: {from_email}
- To: {to_email}

Your Gmail SMTP configuration is working correctly! 🎉

You can now use Gmail to send campaign emails.

Note: Gmail has a limit of 500 emails per day for free accounts.
For high-volume sending (200k emails), consider using SendGrid or AWS SES.

Best regards,
Campaign Mailer System
"""
    
    # Create HTML version
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #28a745; border-bottom: 2px solid #28a745; padding-bottom: 10px;">
                ✅ Gmail SMTP Test Successful!
            </h2>
            
            <p>Hello!</p>
            
            <p>This is a test email sent using Gmail SMTP from your <strong>Campaign System</strong>.</p>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #555;">📋 Configuration Details:</h3>
                <ul style="list-style: none; padding-left: 0;">
                    <li>📧 <strong>SMTP Host:</strong> {settings.EMAIL_HOST}</li>
                    <li>🔌 <strong>Port:</strong> {settings.EMAIL_PORT}</li>
                    <li>📤 <strong>From:</strong> {from_email}</li>
                    <li>📥 <strong>To:</strong> {to_email}</li>
                    <li>🔐 <strong>TLS:</strong> {settings.EMAIL_USE_TLS}</li>
                </ul>
            </div>
            
            <p style="color: #28a745; font-weight: bold;">
                🎉 Your Gmail SMTP configuration is working correctly!
            </p>
            
            <p>You can now use Gmail to send campaign emails.</p>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 20px 0;">
                <p style="margin: 0;">
                    <strong>⚠️ Note:</strong> Gmail has a limit of <strong>500 emails per day</strong> for free accounts.
                    <br>
                    For high-volume sending (200k emails), consider using SendGrid or AWS SES.
                </p>
            </div>
            
            <p style="margin-top: 30px; color: #666;">
                Best regards,<br>
                <strong>Campaign Mailer System</strong>
            </p>
        </div>
    </body>
    </html>
    """
    
    print(f"\n📨 Sending test email...")
    print(f"   From: {from_email}")
    print(f"   To: {to_email}")
    print(f"   Subject: {subject}")
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(message, 'plain')
        part2 = MIMEText(html_message, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect to Gmail SMTP server
        print(f"\n⏳ Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
        
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.set_debuglevel(0)  # Set to 1 for debug output
        
        # Start TLS encryption
        if settings.EMAIL_USE_TLS:
            print("🔒 Starting TLS encryption...")
            server.starttls()
        
        # Login
        print("🔐 Authenticating...")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        
        # Send email
        print("📤 Sending email...")
        server.send_message(msg)
        
        # Close connection
        server.quit()
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Email sent successfully!")
        print("=" * 70)
        print(f"\n📬 Check the inbox: {to_email}")
        print("🎉 Gmail SMTP configuration is working correctly!")
        print("\n💡 Tip: Gmail allows 500 emails/day (free account)")
        print("   For high volume, use SendGrid or AWS SES")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n" + "=" * 70)
        print("❌ ERROR: Authentication Failed")
        print("=" * 70)
        print(f"\nError: {e}")
        print("\n🔧 Solutions:")
        print("1. Make sure you're using an App Password, not your regular Gmail password")
        print("2. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("3. Enable 2-Step Verification first (required for App Passwords)")
        print("4. Update EMAIL_HOST_PASSWORD in .env with the App Password")
        print("5. App Password format: 16 characters with spaces (e.g., 'xxxx xxxx xxxx xxxx')")
        return False
        
    except smtplib.SMTPException as e:
        print("\n" + "=" * 70)
        print("❌ ERROR: SMTP Error")
        print("=" * 70)
        print(f"\nError: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check EMAIL_HOST is 'smtp.gmail.com'")
        print("2. Check EMAIL_PORT is 587 (for TLS)")
        print("3. Check EMAIL_USE_TLS is True")
        print("4. Verify EMAIL_HOST_USER is correct")
        print("5. Verify EMAIL_HOST_PASSWORD is an App Password")
        return False
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERROR: Unexpected Error")
        print("=" * 70)
        print(f"\nError: {e}")
        print(f"Error Type: {type(e).__name__}")
        print("\n🔧 Check your network connection and firewall settings")
        return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python test_gmail.py recipient@example.com")
        print("       python test_gmail.py recipient@example.com 'Subject' 'Message'")
        sys.exit(1)
    
    recipient = sys.argv[1]
    subject = sys.argv[2] if len(sys.argv) > 2 else None
    message = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Validate email format
    if '@' not in recipient:
        print(f"❌ Invalid email address: {recipient}")
        sys.exit(1)
    
    success = send_test_email_gmail(recipient, subject, message)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
