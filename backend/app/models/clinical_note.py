import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ClinicalNote(Base):
    __tablename__ = "clinical_notes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    appointment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    doctor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
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
