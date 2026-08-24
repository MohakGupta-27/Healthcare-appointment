import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.appointment import Appointment, AppointmentStatus
from app.models.clinical_note import ClinicalNote
from app.models.prescription import Prescription, Medication
from app.models.slot_hold import SlotHold, HoldStatus
from app.models.symptom import AISummary, AISummaryStatus, SymptomSubmission
from app.models.user import User, UserRole
from app.repositories import appointment as appt_repo
from app.repositories import doctor as doctor_repo

logger = logging.getLogger(__name__)


def hold_slot(db: Session, patient: User, doctor_id: str, start_time: datetime) -> SlotHold:
    profile = doctor_repo.get_doctor_profile(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor not found")

    end_time = start_time + timedelta(minutes=profile.consultation_duration_minutes)

    # Check for existing appointment
    overlap = appt_repo.get_overlapping_appointment(db, doctor_id, start_time, end_time)
    if overlap:
        raise HTTPException(status_code=409, detail="Slot already booked")

    # Check for active hold by another patient
    existing_hold = appt_repo.get_active_hold(db, doctor_id, start_time, end_time, exclude_patient=patient.id)
    if existing_hold:
        raise HTTPException(status_code=409, detail="Slot is currently held by another patient")

    hold = SlotHold(
        doctor_id=doctor_id,
        patient_id=patient.id,
        start_time=start_time,
        end_time=end_time,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.hold_ttl_seconds),
    )
    return appt_repo.create_slot_hold(db, hold)


def book_appointment(
    db: Session, patient: User, doctor_id: str, start_time: datetime,
    reason: str | None = None, symptoms: str | None = None,
) -> Appointment:
    profile = doctor_repo.get_doctor_profile(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not profile.is_active:
        raise HTTPException(status_code=400, detail="Doctor is not active")

    end_time = start_time + timedelta(minutes=profile.consultation_duration_minutes)

    # Check leave
    from app.repositories.doctor import get_leave_for_date
    leave = get_leave_for_date(db, doctor_id, start_time.date())
    if leave:
        raise HTTPException(status_code=400, detail="Doctor is on leave on this date")

    # Double-booking protection: check overlap inside a serializable transaction block
    overlap = appt_repo.get_overlapping_appointment(db, doctor_id, start_time, end_time)
    if overlap:
        raise HTTPException(status_code=409, detail="Time slot already booked")

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        start_time=start_time,
        end_time=end_time,
        reason=reason,
    )
    created = appt_repo.create_appointment(db, appointment)

    # Expire any holds for this slot
    try:
        appt_repo.expire_holds(db, doctor_id, start_time)
    except Exception:
        logger.exception("Failed to expire holds")

    # Store symptoms if provided
    if symptoms:
        try:
            submit_symptoms(db, created.id, symptoms)
        except Exception:
            logger.exception("Failed to store symptoms")

    # Queue notifications
    try:
        from app.services.notification import queue_booking_confirmation
        queue_booking_confirmation(db, created, profile)
    except Exception:
        logger.exception("Failed to queue booking notification")

    # Queue calendar sync
    try:
        from app.services.calendar import create_calendar_events
        create_calendar_events(db, created, profile)
    except Exception:
        logger.exception("Failed to queue calendar sync")

    return created


def cancel_appointment(
    db: Session, user: User, appointment_id: str, cancellation_reason: str | None = None
) -> Appointment:
    appt = appt_repo.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Authorization
    doctor_profile = doctor_repo.get_doctor_by_user_id(db, user.id)
    if user.role == UserRole.patient and appt.patient_id != user.id:
        raise HTTPException(status_code=403, detail="Not your appointment")
    if user.role == UserRole.doctor:
        if not doctor_profile or doctor_profile.id != appt.doctor_id:
            raise HTTPException(status_code=403, detail="Not your appointment")

    if appt.status != AppointmentStatus.scheduled:
        raise HTTPException(status_code=400, detail="Only scheduled appointments can be cancelled")

    appt.status = AppointmentStatus.cancelled
    appt.cancellation_reason = cancellation_reason
    db.commit()
    db.refresh(appt)

    # Queue notification
    try:
        from app.services.notification import queue_cancellation
        profile = doctor_repo.get_doctor_profile(db, appt.doctor_id)
        queue_cancellation(db, appt, profile)
    except Exception:
        logger.exception("Failed to queue cancellation notification")

    return appt


def complete_appointment(db: Session, doctor_user: User, appointment_id: str) -> Appointment:
    appt = appt_repo.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    doctor_profile = doctor_repo.get_doctor_by_user_id(db, doctor_user.id)
    if not doctor_profile or doctor_profile.id != appt.doctor_id:
        raise HTTPException(status_code=403, detail="Not your appointment")

    if appt.status != AppointmentStatus.scheduled:
        raise HTTPException(status_code=400, detail="Only scheduled appointments can be completed")

    appt.status = AppointmentStatus.completed
    db.commit()
    db.refresh(appt)
    return appt


def get_appointment_detail(db: Session, user: User, appointment_id: str) -> Appointment:
    appt = appt_repo.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    doctor_profile = doctor_repo.get_doctor_by_user_id(db, user.id)
    if user.role == UserRole.patient and appt.patient_id != user.id:
        raise HTTPException(status_code=403, detail="Not your appointment")
    if user.role == UserRole.doctor:
        if not doctor_profile or doctor_profile.id != appt.doctor_id:
            raise HTTPException(status_code=403, detail="Not your appointment")
    return appt


def list_appointments(db: Session, user: User, skip: int = 0, limit: int = 50) -> list[Appointment]:
    if user.role == UserRole.doctor:
        profile = doctor_repo.get_doctor_by_user_id(db, user.id)
        if not profile:
            return []
        return appt_repo.get_appointments_for_doctor(db, profile.id, skip, limit)
    elif user.role == UserRole.admin:
        # Admin sees all - simplified
        from sqlalchemy import select
        from app.models.appointment import Appointment
        return list(db.execute(
            select(Appointment).order_by(Appointment.start_time.desc()).offset(skip).limit(limit)
        ).scalars().all())
    else:
        return appt_repo.get_appointments_for_patient(db, user.id, skip, limit)


# --- Symptoms ---

def submit_symptoms(db: Session, appointment_id: str, symptoms_text: str) -> SymptomSubmission:
    existing = appt_repo.get_symptom(db, appointment_id)
    if existing:
        raise HTTPException(status_code=409, detail="Symptoms already submitted")

    submission = SymptomSubmission(
        appointment_id=appointment_id,
        symptoms=symptoms_text,
    )
    created = appt_repo.create_symptom(db, submission)

    # Trigger AI analysis (non-blocking)
    try:
        _generate_pre_visit_summary(db, appointment_id, symptoms_text)
    except Exception:
        logger.exception("AI pre-visit summary generation failed — booking continues")

    return created


def _generate_pre_visit_summary(db: Session, appointment_id: str, symptoms: str) -> None:
    from app.integrations.llm import analyze_symptoms
    summary = AISummary(
        appointment_id=appointment_id,
        summary_type="pre_visit",
    )
    try:
        result = analyze_symptoms(symptoms)
        summary.urgency_level = result.get("urgency_level", "Unknown")
        summary.chief_complaint = result.get("chief_complaint", "")
        summary.suggested_questions = result.get("suggested_questions", "")
        summary.raw_response = result.get("raw_response", "")
        summary.status = AISummaryStatus.completed
    except Exception as e:
        logger.exception("LLM call failed for pre-visit summary")
        summary.status = AISummaryStatus.failed
        summary.error_message = str(e)

    appt_repo.create_ai_summary(db, summary)


# --- Clinical Notes ---

def submit_clinical_notes(
    db: Session, doctor_user: User, appointment_id: str,
    notes: str, diagnosis: str | None = None, follow_up: str | None = None,
) -> ClinicalNote:
    appt = appt_repo.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    doctor_profile = doctor_repo.get_doctor_by_user_id(db, doctor_user.id)
    if not doctor_profile or doctor_profile.id != appt.doctor_id:
        raise HTTPException(status_code=403, detail="Not your appointment")

    existing = appt_repo.get_clinical_note(db, appointment_id)
    if existing:
        existing.notes = notes
        existing.diagnosis = diagnosis
        existing.follow_up_instructions = follow_up
        db.commit()
        db.refresh(existing)
        return existing

    note = ClinicalNote(
        appointment_id=appointment_id,
        doctor_id=doctor_profile.id,
        notes=notes,
        diagnosis=diagnosis,
        follow_up_instructions=follow_up,
    )
    return appt_repo.create_clinical_note(db, note)


# --- Post Visit AI Summary ---

def generate_post_visit_summary(db: Session, doctor_user: User, appointment_id: str) -> AISummary:
    appt = appt_repo.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    doctor_profile = doctor_repo.get_doctor_by_user_id(db, doctor_user.id)
    if not doctor_profile or doctor_profile.id != appt.doctor_id:
        raise HTTPException(status_code=403, detail="Not your appointment")

    clinical_note = appt_repo.get_clinical_note(db, appointment_id)
    if not clinical_note:
        raise HTTPException(status_code=400, detail="Submit clinical notes first")

    existing = appt_repo.get_ai_summary(db, appointment_id, "post_visit")
    summary = existing or AISummary(
        appointment_id=appointment_id,
        summary_type="post_visit",
    )

    try:
        from app.integrations.llm import generate_patient_summary
        result = generate_patient_summary(
            clinical_note.notes,
            clinical_note.diagnosis,
            clinical_note.follow_up_instructions,
        )
        summary.patient_summary = result.get("patient_summary", "")
        summary.raw_response = result.get("raw_response", "")
        summary.status = AISummaryStatus.completed
    except Exception as e:
        logger.exception("LLM call failed for post-visit summary")
        summary.status = AISummaryStatus.failed
        summary.error_message = str(e)

    if existing:
        appt_repo.update_ai_summary(db, summary)
    else:
        appt_repo.create_ai_summary(db, summary)
    return summary


# --- Prescription ---

def submit_prescription(
    db: Session, doctor_user: User, appointment_id: str,
    notes: str | None, medications_data: list[dict],
) -> Prescription:
    appt = appt_repo.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    doctor_profile = doctor_repo.get_doctor_by_user_id(db, doctor_user.id)
    if not doctor_profile or doctor_profile.id != appt.doctor_id:
        raise HTTPException(status_code=403, detail="Not your appointment")

    from datetime import date
    prescription = Prescription(
        appointment_id=appointment_id,
        doctor_id=doctor_profile.id,
        notes=notes,
    )
    meds = []
    for m in medications_data:
        meds.append(Medication(
            name=m["name"],
            dosage=m["dosage"],
            frequency=m["frequency"],
            start_date=date.fromisoformat(m["start_date"]),
            end_date=date.fromisoformat(m["end_date"]) if m.get("end_date") else None,
            instructions=m.get("instructions"),
        ))
    return appt_repo.create_prescription(db, prescription, meds)
