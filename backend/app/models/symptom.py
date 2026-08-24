import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AISummaryStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class SymptomSubmission(Base):
    __tablename__ = "symptom_submissions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    appointment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("created_at", _utcnow())
        super().__init__(**kwargs)


class AISummary(Base):
    """Pre-visit AI analysis or post-visit patient-friendly summary."""
    __tablename__ = "ai_summaries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, insert_default=lambda: str(uuid.uuid4())
    )
    appointment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    summary_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="pre_visit or post_visit"
    )
    urgency_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_questions: Mapped[str | None] = mapped_column(Text, nullable=True)
    patient_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AISummaryStatus] = mapped_column(
        Enum(AISummaryStatus, name="aisummarystatus", native_enum=False, length=20),
        nullable=False,
        insert_default=AISummaryStatus.pending,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, insert_default=_utcnow
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("status", AISummaryStatus.pending)
        kwargs.setdefault("created_at", _utcnow())
        super().__init__(**kwargs)
