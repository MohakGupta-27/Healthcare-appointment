import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HoldStatus(str, enum.Enum):
    active = "active"
    confirmed = "confirmed"
    expired = "expired"
    released = "released"


class SlotHold(Base):
    __tablename__ = "slot_holds"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    doctor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[HoldStatus] = mapped_column(
        Enum(HoldStatus, name="holdstatus", native_enum=False, length=20),
        nullable=False,
        insert_default=HoldStatus.active,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("status", HoldStatus.active)
        kwargs.setdefault("created_at", _utcnow())
        super().__init__(**kwargs)
