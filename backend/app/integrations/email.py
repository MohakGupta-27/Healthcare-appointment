"""Email abstraction — console backend for dev, SendGrid for production."""
import logging
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send email using configured backend. Returns True on success."""
    backend = settings.email_backend.lower()
    if backend == "sendgrid" and settings.sendgrid_api_key:
        return _send_sendgrid(to, subject, body)
    else:
        return _send_console(to, subject, body)


def _send_console(to: str, subject: str, body: str) -> bool:
    """Development fallback — logs email instead of sending."""
    logger.info(
        "=== EMAIL (console) ===\n"
        f"To: {to}\n"
        f"Subject: {subject}\n"
        f"Body:\n{body}\n"
        "=== END EMAIL ==="
    )
    return True


def _send_sendgrid(to: str, subject: str, body: str) -> bool:
    """Production email via SendGrid."""
    try:
        import httpx
        response = httpx.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {settings.sendgrid_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": "noreply@healthcare-app.local", "name": settings.app_name},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}],
            },
            timeout=10,
        )
        if response.status_code in (200, 201, 202):
            logger.info(f"SendGrid email sent to {to}")
            return True
        else:
            logger.error(f"SendGrid error {response.status_code}: {response.text}")
            return False
    except Exception:
        logger.exception(f"SendGrid send failed to {to}")
        return False
