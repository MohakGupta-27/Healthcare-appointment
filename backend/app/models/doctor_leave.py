import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DoctorLeave(Base):
    __tablename__ = "doctor_leave"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    doctor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    leave_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )

    doctor = relationship("DoctorProfile", back_populates="leave_days")

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("created_at", _utcnow())
        super().__init__(**kwargs)
