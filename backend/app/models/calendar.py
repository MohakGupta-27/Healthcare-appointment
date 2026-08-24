import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CalendarProvider(str, enum.Enum):
    google = "google"


class CalendarConnection(Base):
    __tablename__ = "calendar_connections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[CalendarProvider] = mapped_column(
        Enum(CalendarProvider, name="calendarprovider", native_enum=False, length=20),
        nullable=False,
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow, onupdate=_utcnow
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("created_at", _utcnow())
        kwargs.setdefault("updated_at", _utcnow())
        super().__init__(**kwargs)


class CalendarSyncStatus(str, enum.Enum):
    synced = "synced"
    failed = "failed"
    pending = "pending"
    cancelled = "cancelled"


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    appointment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[CalendarProvider] = mapped_column(
        Enum(CalendarProvider, name="calendarprovider", native_enum=False, length=20, create_constraint=False),
        nullable=False,
    )
    external_event_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[CalendarSyncStatus] = mapped_column(
        Enum(CalendarSyncStatus, name="calendarsyncstatus", native_enum=False, length=20),
        nullable=False,
        insert_default=CalendarSyncStatus.pending,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("status", CalendarSyncStatus.pending)
        kwargs.setdefault("created_at", _utcnow())
        super().__init__(**kwargs)
