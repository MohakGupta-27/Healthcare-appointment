import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    specialization: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    bio: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    consultation_duration_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, insert_default=30
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, insert_default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow, onupdate=_utcnow
    )

    user = relationship("User", backref="doctor_profile", uselist=False, lazy="joined")
    availability_slots = relationship("DoctorAvailability", back_populates="doctor", cascade="all, delete-orphan")
    leave_days = relationship("DoctorLeave", back_populates="doctor", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("consultation_duration_minutes", 30)
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("created_at", _utcnow())
        kwargs.setdefault("updated_at", _utcnow())
        super().__init__(**kwargs)
