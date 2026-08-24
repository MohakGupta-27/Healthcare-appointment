"""Google Calendar integration with OAuth 2.0 — graceful fallback if not configured."""
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.appointment import Appointment
from app.models.calendar import (
    CalendarConnection, CalendarEvent, CalendarProvider, CalendarSyncStatus,
)
from app.models.doctor_profile import DoctorProfile

logger = logging.getLogger(__name__)


def get_google_auth_url(user_id: str) -> str | None:
    """Generate Google OAuth consent URL."""
    if not settings.google_client_id or not settings.google_client_secret:
        return None

    from urllib.parse import urlencode
    params = urlencode({
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar.events",
        "access_type": "offline",
        "prompt": "consent",
        "state": user_id,
    })
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"


def handle_google_callback(db: Session, code: str, user_id: str) -> CalendarConnection | None:
    """Exchange auth code for tokens and store connection."""
    if not settings.google_client_id:
        return None

    try:
        import httpx
        resp = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        from sqlalchemy import select
        existing = db.execute(
            select(CalendarConnection).where(
                CalendarConnection.user_id == user_id,
                CalendarConnection.provider == CalendarProvider.google,
            )
        ).scalar_one_or_none()

        if existing:
            existing.access_token = data["access_token"]
            existing.refresh_token = data.get("refresh_token", existing.refresh_token)
            db.commit()
            db.refresh(existing)
            return existing

        conn = CalendarConnection(
            user_id=user_id,
            provider=CalendarProvider.google,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
        )
        db.add(conn)
        db.commit()
        db.refresh(conn)
        return conn
    except Exception:
        logger.exception("Google Calendar OAuth callback failed")
        return None


def create_calendar_events(db: Session, appt: Appointment, doctor_profile: DoctorProfile) -> None:
    """Create calendar events for both patient and doctor if connected."""
    for user_id in [appt.patient_id, doctor_profile.user_id]:
        _create_event_for_user(db, user_id, appt, doctor_profile)


def _create_event_for_user(
    db: Session, user_id: str, appt: Appointment, doctor_profile: DoctorProfile
) -> None:
    from sqlalchemy import select
    conn = db.execute(
        select(CalendarConnection).where(
            CalendarConnection.user_id == user_id,
            CalendarConnection.provider == CalendarProvider.google,
        )
    ).scalar_one_or_none()

    event = CalendarEvent(
        appointment_id=appt.id,
        user_id=user_id,
        provider=CalendarProvider.google,
    )

    if not conn:
        event.status = CalendarSyncStatus.failed
        event.error_message = "Google Calendar not connected"
        db.add(event)
        db.commit()
        return

    try:
        import httpx
        patient = db.get(from_import("app.models.user", "User"), appt.patient_id)
        doctor_user = db.get(from_import("app.models.user", "User"), doctor_profile.user_id)

        resp = httpx.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {conn.access_token}"},
            json={
                "summary": f"Medical Appointment - {doctor_profile.specialization}",
                "description": (
                    f"Patient: {patient.full_name if patient else 'N/A'}\n"
                    f"Doctor: {doctor_user.full_name if doctor_user else 'N/A'}\n"
                    f"Specialization: {doctor_profile.specialization}\n"
                    f"Reason: {appt.reason or 'General consultation'}"
                ),
                "start": {"dateTime": appt.start_time.isoformat(), "timeZone": "UTC"},
                "end": {"dateTime": appt.end_time.isoformat(), "timeZone": "UTC"},
            },
            timeout=10,
        )
        resp.raise_for_status()
        event_data = resp.json()
        event.external_event_id = event_data.get("id")
        event.status = CalendarSyncStatus.synced
    except Exception as e:
        logger.exception(f"Failed to create calendar event for user {user_id}")
        event.status = CalendarSyncStatus.failed
        event.error_message = str(e)

    db.add(event)
    db.commit()


def cancel_calendar_events(db: Session, appointment_id: str) -> None:
    """Cancel calendar events when appointment is cancelled."""
    from sqlalchemy import select
    events = db.execute(
        select(CalendarEvent).where(
            CalendarEvent.appointment_id == appointment_id,
            CalendarEvent.status == CalendarSyncStatus.synced,
        )
    ).scalars().all()

    for event in events:
        if event.external_event_id:
            conn = db.execute(
                select(CalendarConnection).where(
                    CalendarConnection.user_id == event.user_id,
                    CalendarConnection.provider == CalendarProvider.google,
                )
            ).scalar_one_or_none()
            if conn:
                try:
                    import httpx
                    httpx.delete(
                        f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event.external_event_id}",
                        headers={"Authorization": f"Bearer {conn.access_token}"},
                        timeout=10,
                    )
                except Exception:
                    logger.exception(f"Failed to delete calendar event {event.external_event_id}")
        event.status = CalendarSyncStatus.cancelled
    db.commit()


def from_import(module: str, name: str):
    """Dynamic import helper."""
    import importlib
    mod = importlib.import_module(module)
    return getattr(mod, name)
