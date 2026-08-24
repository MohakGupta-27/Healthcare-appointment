import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointmentstatus", native_enum=False, length=20),
        nullable=False,
        insert_default=AppointmentStatus.scheduled,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow, onupdate=_utcnow
    )

    patient = relationship("User", foreign_keys=[patient_id], backref="patient_appointments")
    doctor_profile = relationship("DoctorProfile", backref="appointments")

    __table_args__ = (
        # Exclusion-like index: prevent overlapping appointments for same doctor
        Index("ix_appointments_doctor_time", "doctor_id", "start_time", "end_time"),
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("status", AppointmentStatus.scheduled)
        kwargs.setdefault("created_at", _utcnow())
        kwargs.setdefault("updated_at", _utcnow())
        super().__init__(**kwargs)
