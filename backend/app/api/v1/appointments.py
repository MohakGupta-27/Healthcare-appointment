"""Appointment endpoints — booking, listing, cancellation, completion, symptoms, notes, prescriptions, AI."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import appointment as appt_repo
from app.schemas.appointment import (
    AISummaryOut,
    AppointmentCancel,
    AppointmentCreate,
    AppointmentOut,
    ClinicalNoteCreate,
    ClinicalNoteOut,
    MedicationOut,
    PrescriptionCreate,
    PrescriptionOut,
    SlotHoldOut,
    SlotHoldRequest,
    SymptomOut,
    SymptomSubmit,
)
from app.services.appointment import (
    book_appointment,
    cancel_appointment,
    complete_appointment,
    generate_post_visit_summary,
    get_appointment_detail,
    hold_slot,
    list_appointments,
    submit_clinical_notes,
    submit_prescription,
    submit_symptoms,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


def _appt_to_out(appt) -> AppointmentOut:
    patient_name = appt.patient.full_name if appt.patient else ""
    patient_email = appt.patient.email if appt.patient else ""
    doctor_name = ""
    doctor_spec = ""
    if appt.doctor_profile and appt.doctor_profile.user:
        doctor_name = appt.doctor_profile.user.full_name
        doctor_spec = appt.doctor_profile.specialization
    return AppointmentOut(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        start_time=appt.start_time,
        end_time=appt.end_time,
        status=appt.status.value if hasattr(appt.status, "value") else appt.status,
        reason=appt.reason,
        cancellation_reason=appt.cancellation_reason,
        created_at=appt.created_at,
        patient_name=patient_name,
        patient_email=patient_email,
        doctor_name=doctor_name,
        doctor_specialization=doctor_spec,
    )


@router.post("/hold", response_model=SlotHoldOut, status_code=201)
def hold_appointment_slot(
    data: SlotHoldRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("patient")),
) -> SlotHoldOut:
    h = hold_slot(db, current_user, data.doctor_id, data.start_time)
    return SlotHoldOut.model_validate(h)


@router.post("", response_model=AppointmentOut, status_code=201)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("patient")),
) -> AppointmentOut:
    appt = book_appointment(
        db, current_user, data.doctor_id, data.start_time,
        reason=data.reason, symptoms=data.symptoms,
    )
    return _appt_to_out(appt)


@router.get("", response_model=list[AppointmentOut])
def list_my_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AppointmentOut]:
    appts = list_appointments(db, current_user, skip, limit)
    return [_appt_to_out(a) for a in appts]


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentOut:
    appt = get_appointment_detail(db, current_user, appointment_id)
    return _appt_to_out(appt)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel(
    appointment_id: str,
    data: AppointmentCancel = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentOut:
    reason = data.cancellation_reason if data else None
    appt = cancel_appointment(db, current_user, appointment_id, reason)
    return _appt_to_out(appt)


@router.patch("/{appointment_id}/complete", response_model=AppointmentOut)
def complete(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
) -> AppointmentOut:
    appt = complete_appointment(db, current_user, appointment_id)
    return _appt_to_out(appt)


# --- Symptoms ---

@router.post("/{appointment_id}/symptoms", response_model=SymptomOut, status_code=201)
def add_symptoms(
    appointment_id: str,
    data: SymptomSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SymptomOut:
    # Verify ownership
    appt = get_appointment_detail(db, current_user, appointment_id)
    sub = submit_symptoms(db, appointment_id, data.symptoms)
    return SymptomOut.model_validate(sub)


@router.get("/{appointment_id}/symptoms", response_model=SymptomOut | None)
def get_symptoms(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SymptomOut | None:
    appt = get_appointment_detail(db, current_user, appointment_id)
    sub = appt_repo.get_symptom(db, appointment_id)
    return SymptomOut.model_validate(sub) if sub else None


# --- AI Summary ---

@router.get("/{appointment_id}/summary", response_model=list[AISummaryOut])
def get_summaries(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AISummaryOut]:
    appt = get_appointment_detail(db, current_user, appointment_id)
    results = []
    for st in ["pre_visit", "post_visit"]:
        s = appt_repo.get_ai_summary(db, appointment_id, st)
        if s:
            out = AISummaryOut.model_validate(s)
            if st == "post_visit":
                out.disclaimer = "AI-generated patient-friendly summary. Follow your doctor's prescription and instructions."
            results.append(out)
    return results


# --- Clinical Notes ---

@router.post("/{appointment_id}/visit-notes", response_model=ClinicalNoteOut, status_code=201)
def add_visit_notes(
    appointment_id: str,
    data: ClinicalNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
) -> ClinicalNoteOut:
    note = submit_clinical_notes(
        db, current_user, appointment_id,
        data.notes, data.diagnosis, data.follow_up_instructions,
    )
    return ClinicalNoteOut.model_validate(note)


@router.post("/{appointment_id}/generate-summary", response_model=AISummaryOut)
def generate_summary(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
) -> AISummaryOut:
    summary = generate_post_visit_summary(db, current_user, appointment_id)
    out = AISummaryOut.model_validate(summary)
    out.disclaimer = "AI-generated patient-friendly summary. Follow your doctor's prescription and instructions."
    return out


# --- Prescription ---

@router.post("/{appointment_id}/prescription", response_model=PrescriptionOut, status_code=201)
def add_prescription(
    appointment_id: str,
    data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
) -> PrescriptionOut:
    meds_data = [m.model_dump() for m in data.medications]
    rx = submit_prescription(db, current_user, appointment_id, data.notes, meds_data)
    meds = appt_repo.get_medications(db, rx.id)
    med_outs = []
    for m in meds:
        med_outs.append(MedicationOut(
            id=m.id,
            prescription_id=m.prescription_id,
            name=m.name,
            dosage=m.dosage,
            frequency=m.frequency,
            start_date=str(m.start_date),
            end_date=str(m.end_date) if m.end_date else None,
            instructions=m.instructions,
        ))
    return PrescriptionOut(
        id=rx.id,
        appointment_id=rx.appointment_id,
        doctor_id=rx.doctor_id,
        notes=rx.notes,
        medications=med_outs,
        created_at=rx.created_at,
    )


@router.get("/{appointment_id}/prescription", response_model=PrescriptionOut | None)
def get_prescription_endpoint(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PrescriptionOut | None:
    appt = get_appointment_detail(db, current_user, appointment_id)
    rx = appt_repo.get_prescription(db, appointment_id)
    if not rx:
        return None
    meds = appt_repo.get_medications(db, rx.id)
    med_outs = []
    for m in meds:
        med_outs.append(MedicationOut(
            id=m.id,
            prescription_id=m.prescription_id,
            name=m.name,
            dosage=m.dosage,
            frequency=m.frequency,
            start_date=str(m.start_date),
            end_date=str(m.end_date) if m.end_date else None,
            instructions=m.instructions,
        ))
    return PrescriptionOut(
        id=rx.id,
        appointment_id=rx.appointment_id,
        doctor_id=rx.doctor_id,
        notes=rx.notes,
        medications=med_outs,
        created_at=rx.created_at,
    )
