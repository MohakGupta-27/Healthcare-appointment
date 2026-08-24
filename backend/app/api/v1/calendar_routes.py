"""Google Calendar OAuth endpoints."""
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.calendar import get_google_auth_url, handle_google_callback

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/google/connect")
def connect_google_calendar(
    current_user: User = Depends(get_current_user),
):
    url = get_google_auth_url(current_user.id)
    if not url:
        return {"error": "Google Calendar not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."}
    return {"auth_url": url}


@router.get("/google/callback")
def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    conn = handle_google_callback(db, code, state)
    if conn:
        return {"status": "connected", "provider": "google"}
    return {"status": "failed", "error": "Could not connect Google Calendar"}


@router.get("/status")
def calendar_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.calendar import CalendarConnection, CalendarProvider
    conn = db.execute(
        select(CalendarConnection).where(
            CalendarConnection.user_id == current_user.id,
            CalendarConnection.provider == CalendarProvider.google,
        )
    ).scalar_one_or_none()
    return {
        "google_connected": conn is not None,
        "configured": bool(
            __import__("app.core.config", fromlist=["settings"]).settings.google_client_id
        ),
    }
