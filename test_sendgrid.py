#!/usr/bin/env python
"""
SendGrid Email Test Script

This script tests SendGrid configuration and sends a test email.
Run this after setting up your SendGrid API key to verify everything works.

Usage:
    python test_sendgrid.py your-email@example.com
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailer_project.settings')
django.setup()

from django.conf import settings
from campaigns.providers import send_via_sendgrid

def test_sendgrid_connection():
    """Test SendGrid API key and configuration"""
    print("\n" + "="*70)
    print("SendGrid Configuration Test")
    print("="*70)
    
    # Check if SendGrid is configured
    api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    from_email = getattr(settings, 'SENDGRID_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
    from_name = getattr(settings, 'SENDGRID_FROM_NAME', 'Campaign Mailer')
    
    if not api_key:
        print("\n❌ ERROR: SENDGRID_API_KEY is not configured!")
        print("\nPlease add the following to your .env file:")
        print("  SENDGRID_API_KEY=SG.your-api-key-here")
        print("\nSee SENDGRID_SETUP_GUIDE.md for complete setup instructions.")
        sys.exit(1)
    
    print(f"\n✓ SendGrid API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
    print(f"✓ From Email: {from_email}")
    print(f"✓ From Name: {from_name}")
    print(f"✓ Rate Limit: {getattr(settings, 'SENDGRID_RATE_LIMIT_PER_SEC', 100)} emails/sec")
    
    return True

def send_test_email(recipient_email):
    """Send a test email via SendGrid"""
    print("\n" + "-"*70)
    print(f"Sending test email to: {recipient_email}")
    print("-"*70)
    
    subject = "🚀 SendGrid Test - Campaign Mailer System"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px 10px 0 0;
                text-align: center;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .badge {{
                display: inline-block;
                background: #10b981;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .info {{
                background: white;
                padding: 20px;
                border-left: 4px solid #667eea;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .footer {{
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>✅ SendGrid Successfully Connected!</h1>
            <p>Your email campaign system is ready</p>
        </div>
        <div class="content">
            <div class="badge">🎯 Test Email</div>
            
            <p>Congratulations! Your SendGrid integration is working perfectly.</p>
            
            <div class="info">
                <h3>📊 System Information:</h3>
                <ul>
                    <li><strong>Provider:</strong> SendGrid API</li>
                    <li><strong>Status:</strong> Active ✓</li>
                    <li><strong>Capacity:</strong> Ready for high-volume sending</li>
                    <li><strong>From:</strong> {settings.SENDGRID_FROM_EMAIL}</li>
                </ul>
            </div>
            
            <h3>🚀 Next Steps:</h3>
            <ol>
                <li>Verify your domain in SendGrid (for better deliverability)</li>
                <li>Upgrade to Pro plan for 200,000 emails capacity</li>
                <li>Set up email templates in Django admin</li>
                <li>Create your first campaign!</li>
            </ol>
            
            <div class="info">
                <h4>💡 Pro Tips:</h4>
                <ul>
                    <li>Single sender verification: 100 emails/day (current setup)</li>
                    <li>Domain verification: Unlimited sending with Pro plan</li>
                    <li>Expected send time for 200k emails: 1-2 hours</li>
                    <li>Monitor your dashboard: <a href="https://app.sendgrid.com">app.sendgrid.com</a></li>
                </ul>
            </div>
            
            <p><strong>Your campaign system is ready to send emails! 🎉</strong></p>
        </div>
        <div class="footer">
            <p>Campaign Mailer System | Powered by SendGrid</p>
            <p>This is an automated test email from your Django application</p>
        </div>
    </body>
    </html>
    """
    
    try:
        status_code, response_body = send_via_sendgrid(
            subject=subject,
            html_content=html_content,
            recipient_email=recipient_email
        )
        
        print(f"\n✅ SUCCESS! Email sent successfully!")
        print(f"   Status Code: {status_code}")
        print(f"   Response: {response_body}")
        
        print("\n" + "="*70)
        print("📧 Check your inbox at:", recipient_email)
        print("="*70)
        print("\n📝 Notes:")
        print("  - Email should arrive within 1-2 minutes")
        print("  - Check spam folder if not in inbox")
        print("  - Monitor SendGrid dashboard for delivery stats")
        print(f"  - Dashboard: https://app.sendgrid.com/stats")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to send email!")
        print(f"   Error: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("  1. Verify API key is correct in .env file")
        print("  2. Check sender email is verified in SendGrid")
        print("  3. Ensure you have sending credits available")
        print("  4. Review SendGrid dashboard for blocks/issues")
        print("  5. See SENDGRID_SETUP_GUIDE.md for detailed help")
        return False

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("\n❌ Usage: python test_sendgrid.py your-email@example.com")
        print("\nExample:")
        print("  python test_sendgrid.py john@example.com")
        sys.exit(1)
    
    recipient_email = sys.argv[1]
    
    # Validate email format (basic check)
    if '@' not in recipient_email or '.' not in recipient_email:
        print(f"\n❌ Invalid email format: {recipient_email}")
        sys.exit(1)
    
    # Test configuration
    if not test_sendgrid_connection():
        sys.exit(1)
    
    # Send test email
    success = send_test_email(recipient_email)
    
    if success:
        print("\n✅ All tests passed! SendGrid is configured correctly.")
        print("\n📚 Next: Read SENDGRID_SETUP_GUIDE.md for production setup")
        sys.exit(0)
    else:
        print("\n❌ Test failed. Please fix the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
