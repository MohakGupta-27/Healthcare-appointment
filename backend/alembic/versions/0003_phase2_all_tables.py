"""Phase 2: doctor profiles, availability, leave, appointments, slot holds, symptoms, AI summaries,
clinical notes, prescriptions, medications, notifications, calendar connections, calendar events.

Revision ID: 0003
Revises: 0002_users_table
Create Date: 2026-08-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002_users_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "doctor_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("specialization", sa.String(100), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False, server_default=""),
        sa.Column("consultation_duration_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_doctor_profiles_user_id", "doctor_profiles", ["user_id"])
    op.create_index("ix_doctor_profiles_specialization", "doctor_profiles", ["specialization"])

    op.create_table(
        "doctor_availability",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("doctor_id", sa.String(36), sa.ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_doctor_availability_doctor_id", "doctor_availability", ["doctor_id"])

    op.create_table(
        "doctor_leave",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("doctor_id", sa.String(36), sa.ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("leave_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_doctor_leave_doctor_id", "doctor_leave", ["doctor_id"])

    op.create_table(
        "appointments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doctor_id", sa.String(36), sa.ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="scheduled"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_start_time", "appointments", ["start_time"])
    op.create_index("ix_appointments_doctor_time", "appointments", ["doctor_id", "start_time", "end_time"])

    op.create_table(
        "slot_holds",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("doctor_id", sa.String(36), sa.ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_slot_holds_doctor_id", "slot_holds", ["doctor_id"])

    op.create_table(
        "symptom_submissions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("appointment_id", sa.String(36), sa.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("symptoms", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_symptom_submissions_appointment_id", "symptom_submissions", ["appointment_id"])

    op.create_table(
        "ai_summaries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("appointment_id", sa.String(36), sa.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("summary_type", sa.String(20), nullable=False),
        sa.Column("urgency_level", sa.String(20), nullable=True),
        sa.Column("chief_complaint", sa.Text(), nullable=True),
        sa.Column("suggested_questions", sa.Text(), nullable=True),
        sa.Column("patient_summary", sa.Text(), nullable=True),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_summaries_appointment_id", "ai_summaries", ["appointment_id"])

    op.create_table(
        "clinical_notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("appointment_id", sa.String(36), sa.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("doctor_id", sa.String(36), sa.ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("follow_up_instructions", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_clinical_notes_appointment_id", "clinical_notes", ["appointment_id"])

    op.create_table(
        "prescriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("appointment_id", sa.String(36), sa.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doctor_id", sa.String(36), sa.ForeignKey("doctor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_prescriptions_appointment_id", "prescriptions", ["appointment_id"])

    op.create_table(
        "medications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("prescription_id", sa.String(36), sa.ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("dosage", sa.String(100), nullable=False),
        sa.Column("frequency", sa.String(50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_medications_prescription_id", "medications", ["prescription_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("recipient_email", sa.String(320), nullable=False),
        sa.Column("recipient_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notification_type", sa.String(40), nullable=False),
        sa.Column("appointment_id", sa.String(36), sa.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_recipient_email", "notifications", ["recipient_email"])

    op.create_table(
        "calendar_connections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_calendar_connections_user_id", "calendar_connections", ["user_id"])

    op.create_table(
        "calendar_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("appointment_id", sa.String(36), sa.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("external_event_id", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_calendar_events_appointment_id", "calendar_events", ["appointment_id"])


def downgrade() -> None:
    op.drop_table("calendar_events")
    op.drop_table("calendar_connections")
    op.drop_table("notifications")
    op.drop_table("medications")
    op.drop_table("prescriptions")
    op.drop_table("clinical_notes")
    op.drop_table("ai_summaries")
    op.drop_table("symptom_submissions")
    op.drop_table("slot_holds")
    op.drop_table("appointments")
    op.drop_table("doctor_leave")
    op.drop_table("doctor_availability")
    op.drop_table("doctor_profiles")
