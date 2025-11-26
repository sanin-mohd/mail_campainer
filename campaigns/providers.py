import logging
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

# Try SendGrid first (if API key present); otherwise fallback to SMTP
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except Exception:
    SENDGRID_AVAILABLE = False

def send_via_sendgrid(subject: str, html_content: str, recipient_email: str, from_email=None):
    """Send email via SendGrid API"""
    if not SENDGRID_AVAILABLE:
        raise RuntimeError("SendGrid package not installed")
    
    api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    if not api_key:
        raise RuntimeError("SendGrid API key not configured")
    
    from_addr = from_email or getattr(settings, 'SENDGRID_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
    
    message = Mail(
        from_email=from_addr,
        to_emails=recipient_email,
        subject=subject,
        html_content=html_content,
    )
    
    client = SendGridAPIClient(api_key)
    response = client.send(message)
    logger.info(f"SendGrid sent email to {recipient_email}: Status {response.status_code}")
    return response.status_code, response.body

def send_via_smtp(subject: str, html_content: str, recipient_email: str, from_email=None):
    msg = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    msg.content_subtype = "html"
    # Use django's email connection (configured by settings)
    msg.send(fail_silently=False)
    logger.info(f"SMTP sent email to {recipient_email}")
    return 250, b"OK"

def send_email_to_recipient(campaign, recipient):
    """
    Attempt to send email via provider, fallback to SMTP.
    Raises exception on irrecoverable failure.
    """
    subject = campaign.subject
    html = campaign.content  # content should be safe / sanitized upstream
    email = recipient.email

    # Rate limiting / pacing could be handled here (sleep between requests) but
    # prefer Celery rate_limit at task level. Minimal backoff on provider errors.
    try:
        if settings.SENDGRID_API_KEY and SENDGRID_AVAILABLE:
            code, _ = send_via_sendgrid(subject, html, email)
            if 200 <= int(code) < 300:
                return "sent"
            # non-2xx from provider => fallback to smtp
        # Fallback to SMTP
        code, _ = send_via_smtp(subject, html, email)
        if code and int(code) < 400:
            return "sent"
        raise RuntimeError(f"SMTP returned code {code}")
    except Exception as exc:
        logger.exception("Failed to send email to %s: %s", email, exc)
        raise

def get_rate_limit_for_provider():
    """
    Calculate optimal rate limit based on email provider.
    Returns rate limit string for Celery.
    """
    from django.conf import settings
    
    # Check which provider is configured
    if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
        # SendGrid Pro: 600 emails/second max
        # With BATCH_SIZE=200, we need 3 tasks/second per worker
        # With 2 workers: 1.5 tasks/second per worker
        return "1.5/s"  # Conservative: 300 emails/s per worker
    
    elif settings.EMAIL_HOST == 'smtp.gmail.com':
        # Gmail: 500 emails/day = very slow
        return "0.0001/s"  # ~10 emails/day per worker
    
    else:
        # Default: conservative
        return "1/s"
