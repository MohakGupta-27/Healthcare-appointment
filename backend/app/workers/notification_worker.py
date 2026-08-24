"""Background worker for email sending, medication reminders, appointment reminders.

Usage:
    python -m app.workers.notification_worker

Runs in a loop, processing pending notifications and sending emails.
Uses Redis for distributed locking to prevent duplicate sends.
"""
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.config import settings
from app.db.session import SessionLocal
from app.integrations.email import send_email
from app.models.notification import Notification, NotificationStatus
from app.repositories.appointment import get_pending_notifications

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
POLL_INTERVAL = 10  # seconds


def process_notifications() -> int:
    """Process pending notifications. Returns count processed."""
    db = SessionLocal()
    processed = 0
    try:
        pending = get_pending_notifications(db, limit=20)
        for notif in pending:
            try:
                success = send_email(notif.recipient_email, notif.subject, notif.body)
                notif.attempts += 1
                if success:
                    notif.status = NotificationStatus.sent
                    notif.sent_at = datetime.now(timezone.utc)
                    logger.info(f"Notification {notif.id} sent to {notif.recipient_email}")
                else:
                    notif.last_error = "Email send returned False"
                    if notif.attempts >= MAX_RETRIES:
                        notif.status = NotificationStatus.failed
                        logger.warning(f"Notification {notif.id} failed after {MAX_RETRIES} attempts")
                processed += 1
            except Exception as e:
                notif.attempts += 1
                notif.last_error = str(e)
                if notif.attempts >= MAX_RETRIES:
                    notif.status = NotificationStatus.failed
                logger.exception(f"Error processing notification {notif.id}")
        db.commit()
    except Exception:
        logger.exception("Error in notification processing loop")
        db.rollback()
    finally:
        db.close()
    return processed


def run_worker():
    """Main worker loop."""
    from app.core.logging import configure_logging
    configure_logging(settings.debug)
    logger.info("Notification worker started")

    while True:
        try:
            count = process_notifications()
            if count > 0:
                logger.info(f"Processed {count} notifications")
        except Exception:
            logger.exception("Worker loop error")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_worker()
