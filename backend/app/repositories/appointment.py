from datetime import datetime

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.slot_hold import SlotHold, HoldStatus
from app.models.symptom import SymptomSubmission, AISummary
from app.models.clinical_note import ClinicalNote
from app.models.prescription import Prescription, Medication
from app.models.notification import Notification


def create_appointment(db: Session, appointment: Appointment) -> Appointment:
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment(db: Session, appointment_id: str) -> Appointment | None:
    return db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    ).scalar_one_or_none()


def get_overlapping_appointment(
    db: Session, doctor_id: str, start_time: datetime, end_time: datetime, exclude_id: str | None = None
) -> Appointment | None:
    """Check if there's already a scheduled appointment overlapping the time range."""
    stmt = select(Appointment).where(
        and_(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.scheduled,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time,
        )
    )
    if exclude_id:
        stmt = stmt.where(Appointment.id != exclude_id)
    return db.execute(stmt).scalar_one_or_none()


def get_appointments_for_patient(
    db: Session, patient_id: str, skip: int = 0, limit: int = 50
) -> list[Appointment]:
    return list(db.execute(
        select(Appointment)
        .where(Appointment.patient_id == patient_id)
        .order_by(Appointment.start_time.desc())
        .offset(skip).limit(limit)
    ).scalars().all())


def get_appointments_for_doctor(
    db: Session, doctor_id: str, skip: int = 0, limit: int = 50
) -> list[Appointment]:
    return list(db.execute(
        select(Appointment)
        .where(Appointment.doctor_id == doctor_id)
        .order_by(Appointment.start_time.desc())
        .offset(skip).limit(limit)
    ).scalars().all())


def get_appointments_for_doctor_on_date(
    db: Session, doctor_id: str, date_start: datetime, date_end: datetime
) -> list[Appointment]:
    return list(db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status == AppointmentStatus.scheduled,
                Appointment.start_time >= date_start,
                Appointment.start_time < date_end,
            )
        )
    ).scalars().all())


# --- Slot Holds ---

def create_slot_hold(db: Session, hold: SlotHold) -> SlotHold:
    db.add(hold)
    db.commit()
    db.refresh(hold)
    return hold


def get_active_hold(
    db: Session, doctor_id: str, start_time: datetime, end_time: datetime,
    exclude_patient: str | None = None,
) -> SlotHold | None:
    now = datetime.now(start_time.tzinfo)
    stmt = select(SlotHold).where(
        and_(
            SlotHold.doctor_id == doctor_id,
            SlotHold.status == HoldStatus.active,
            SlotHold.expires_at > now,
            SlotHold.start_time < end_time,
            SlotHold.end_time > start_time,
        )
    )
    if exclude_patient:
        stmt = stmt.where(SlotHold.patient_id != exclude_patient)
    return db.execute(stmt).scalar_one_or_none()


def expire_holds(db: Session, doctor_id: str, start_time: datetime) -> None:
    holds = db.execute(
        select(SlotHold).where(
            and_(
                SlotHold.doctor_id == doctor_id,
                SlotHold.start_time == start_time,
                SlotHold.status == HoldStatus.active,
            )
        )
    ).scalars().all()
    for h in holds:
        h.status = HoldStatus.expired
    db.commit()


# --- Symptoms ---

def create_symptom(db: Session, submission: SymptomSubmission) -> SymptomSubmission:
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def get_symptom(db: Session, appointment_id: str) -> SymptomSubmission | None:
    return db.execute(
        select(SymptomSubmission).where(SymptomSubmission.appointment_id == appointment_id)
    ).scalar_one_or_none()


# --- AI Summary ---

def create_ai_summary(db: Session, summary: AISummary) -> AISummary:
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


def get_ai_summary(db: Session, appointment_id: str, summary_type: str) -> AISummary | None:
    return db.execute(
        select(AISummary).where(
            and_(AISummary.appointment_id == appointment_id, AISummary.summary_type == summary_type)
        )
    ).scalar_one_or_none()


def update_ai_summary(db: Session, summary: AISummary) -> AISummary:
    db.commit()
    db.refresh(summary)
    return summary


# --- Clinical Notes ---

def create_clinical_note(db: Session, note: ClinicalNote) -> ClinicalNote:
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_clinical_note(db: Session, appointment_id: str) -> ClinicalNote | None:
    return db.execute(
        select(ClinicalNote).where(ClinicalNote.appointment_id == appointment_id)
    ).scalar_one_or_none()


# --- Prescriptions ---

def create_prescription(db: Session, prescription: Prescription, medications: list[Medication]) -> Prescription:
    db.add(prescription)
    db.flush()
    for med in medications:
        med.prescription_id = prescription.id
        db.add(med)
    db.commit()
    db.refresh(prescription)
    return prescription


def get_prescription(db: Session, appointment_id: str) -> Prescription | None:
    return db.execute(
        select(Prescription).where(Prescription.appointment_id == appointment_id)
    ).scalar_one_or_none()


def get_medications(db: Session, prescription_id: str) -> list[Medication]:
    return list(db.execute(
        select(Medication).where(Medication.prescription_id == prescription_id)
    ).scalars().all())


# --- Notifications ---

def create_notification(db: Session, notification: Notification) -> Notification:
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_pending_notifications(db: Session, limit: int = 50) -> list[Notification]:
    from app.models.notification import NotificationStatus
    return list(db.execute(
        select(Notification)
        .where(
            and_(
                Notification.status == NotificationStatus.pending,
                Notification.attempts < 3,
            )
        )
        .order_by(Notification.created_at)
        .limit(limit)
    ).scalars().all())
