import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NotificationType(str, enum.Enum):
    appointment_confirmation = "appointment_confirmation"
    appointment_reminder = "appointment_reminder"
    appointment_cancellation = "appointment_cancellation"
    leave_cancellation = "leave_cancellation"
    medication_reminder = "medication_reminder"
    reschedule = "reschedule"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    recipient_email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    recipient_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notificationtype", native_enum=False, length=40),
        nullable=False,
    )
    appointment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notificationstatus", native_enum=False, length=20),
        nullable=False,
        insert_default=NotificationStatus.pending,
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, insert_default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("status", NotificationStatus.pending)
        kwargs.setdefault("attempts", 0)
        kwargs.setdefault("created_at", _utcnow())
        super().__init__(**kwargs)
