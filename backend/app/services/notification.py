"""Notification service — queues email notifications without blocking the main transaction."""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.doctor_profile import DoctorProfile
from app.models.notification import Notification, NotificationType
from app.models.user import User

logger = logging.getLogger(__name__)


def _get_user(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def queue_booking_confirmation(db: Session, appt: Appointment, doctor_profile: DoctorProfile) -> None:
    patient = _get_user(db, appt.patient_id)
    doctor_user = _get_user(db, doctor_profile.user_id) if doctor_profile else None

    start_str = appt.start_time.strftime("%Y-%m-%d %H:%M UTC")
    end_str = appt.end_time.strftime("%H:%M UTC")

    # Notify patient
    if patient:
        _create_notification(
            db, patient.email, patient.id,
            NotificationType.appointment_confirmation, appt.id,
            subject=f"Appointment Confirmed — {start_str}",
            body=(
                f"Dear {patient.full_name},\n\n"
                f"Your appointment has been confirmed.\n"
                f"Doctor: {doctor_user.full_name if doctor_user else 'N/A'} ({doctor_profile.specialization})\n"
                f"Time: {start_str} - {end_str}\n\n"
                f"Please arrive on time. You can view details in your dashboard."
            ),
        )

    # Notify doctor
    if doctor_user:
        _create_notification(
            db, doctor_user.email, doctor_user.id,
            NotificationType.appointment_confirmation, appt.id,
            subject=f"New Appointment — {start_str}",
            body=(
                f"Dear Dr. {doctor_user.full_name},\n\n"
                f"A new appointment has been booked.\n"
                f"Patient: {patient.full_name if patient else 'N/A'}\n"
                f"Time: {start_str} - {end_str}\n"
                f"Reason: {appt.reason or 'Not provided'}"
            ),
        )


def queue_cancellation(db: Session, appt: Appointment, doctor_profile: DoctorProfile | None) -> None:
    patient = _get_user(db, appt.patient_id)
    doctor_user = _get_user(db, doctor_profile.user_id) if doctor_profile else None

    start_str = appt.start_time.strftime("%Y-%m-%d %H:%M UTC")

    if patient:
        _create_notification(
            db, patient.email, patient.id,
            NotificationType.appointment_cancellation, appt.id,
            subject=f"Appointment Cancelled — {start_str}",
            body=(
                f"Dear {patient.full_name},\n\n"
                f"Your appointment on {start_str} has been cancelled.\n"
                f"Reason: {appt.cancellation_reason or 'Not provided'}\n\n"
                f"Please book a new appointment if needed."
            ),
        )

    if doctor_user:
        _create_notification(
            db, doctor_user.email, doctor_user.id,
            NotificationType.appointment_cancellation, appt.id,
            subject=f"Appointment Cancelled — {start_str}",
            body=(
                f"Dear Dr. {doctor_user.full_name},\n\n"
                f"An appointment on {start_str} has been cancelled.\n"
                f"Patient: {patient.full_name if patient else 'N/A'}\n"
                f"Reason: {appt.cancellation_reason or 'Not provided'}"
            ),
        )


def queue_leave_cancellation(db: Session, appt: Appointment, doctor_profile: DoctorProfile) -> None:
    patient = _get_user(db, appt.patient_id)
    doctor_user = _get_user(db, doctor_profile.user_id)
    start_str = appt.start_time.strftime("%Y-%m-%d %H:%M UTC")

    if patient:
        _create_notification(
            db, patient.email, patient.id,
            NotificationType.leave_cancellation, appt.id,
            subject=f"Appointment Cancelled (Doctor Leave) — {start_str}",
            body=(
                f"Dear {patient.full_name},\n\n"
                f"Your appointment on {start_str} has been cancelled because "
                f"Dr. {doctor_user.full_name if doctor_user else 'your doctor'} is on leave.\n\n"
                f"Please book a new appointment for a different date."
            ),
        )


def _create_notification(
    db: Session, email: str, user_id: str | None,
    notif_type: NotificationType, appointment_id: str | None,
    subject: str, body: str,
) -> Notification:
    notif = Notification(
        recipient_email=email,
        recipient_id=user_id,
        notification_type=notif_type,
        appointment_id=appointment_id,
        subject=subject,
        body=body,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
