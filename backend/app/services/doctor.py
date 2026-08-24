import logging
from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.availability import DoctorAvailability
from app.models.doctor_leave import DoctorLeave
from app.models.doctor_profile import DoctorProfile
from app.models.user import User, UserRole
from app.repositories import doctor as doctor_repo
from app.repositories import appointment as appt_repo
from app.schemas.doctor import (
    AvailabilityCreate,
    AvailabilityOut,
    AvailableSlot,
    DoctorLeaveCreate,
    DoctorLeaveOut,
    DoctorListOut,
    DoctorProfileCreate,
    DoctorProfileOut,
    DoctorProfileUpdate,
)

logger = logging.getLogger(__name__)


def create_doctor_profile(db: Session, data: DoctorProfileCreate) -> DoctorProfileOut:
    user = db.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != UserRole.doctor:
        # Promote user to doctor role
        user.role = UserRole.doctor
    existing = doctor_repo.get_doctor_by_user_id(db, data.user_id)
    if existing:
        raise HTTPException(status_code=409, detail="Doctor profile already exists")
    profile = DoctorProfile(
        user_id=data.user_id,
        specialization=data.specialization,
        bio=data.bio,
        consultation_duration_minutes=data.consultation_duration_minutes,
    )
    created = doctor_repo.create_doctor_profile(db, profile)
    return _profile_to_out(created)


def update_doctor_profile_by_admin(
    db: Session, doctor_id: str, data: DoctorProfileUpdate
) -> DoctorProfileOut:
    profile = doctor_repo.get_doctor_profile(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if data.specialization is not None:
        profile.specialization = data.specialization
    if data.bio is not None:
        profile.bio = data.bio
    if data.consultation_duration_minutes is not None:
        profile.consultation_duration_minutes = data.consultation_duration_minutes
    if data.is_active is not None:
        profile.is_active = data.is_active
    updated = doctor_repo.update_doctor_profile(db, profile)
    return _profile_to_out(updated)


def list_doctors_service(
    db: Session, specialization: str | None = None, skip: int = 0, limit: int = 50
) -> list[DoctorListOut]:
    profiles = doctor_repo.list_doctors(db, specialization=specialization, skip=skip, limit=limit)
    result = []
    for p in profiles:
        result.append(DoctorListOut(
            id=p.id,
            user_id=p.user_id,
            specialization=p.specialization,
            bio=p.bio,
            consultation_duration_minutes=p.consultation_duration_minutes,
            is_active=p.is_active,
            doctor_name=p.user.full_name if p.user else "",
            doctor_email=p.user.email if p.user else "",
        ))
    return result


def get_doctor_detail(db: Session, doctor_id: str) -> DoctorProfileOut:
    profile = doctor_repo.get_doctor_profile(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return _profile_to_out(profile)


def set_availability_service(
    db: Session, doctor_id: str, slots: list[AvailabilityCreate]
) -> list[AvailabilityOut]:
    profile = doctor_repo.get_doctor_profile(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor not found")
    models = []
    for s in slots:
        models.append(DoctorAvailability(
            doctor_id=doctor_id,
            day_of_week=s.day_of_week,
            start_time=time.fromisoformat(s.start_time),
            end_time=time.fromisoformat(s.end_time),
        ))
    created = doctor_repo.set_availability(db, doctor_id, models)
    return [_avail_to_out(a) for a in created]


def get_availability_service(db: Session, doctor_id: str) -> list[AvailabilityOut]:
    profile = doctor_repo.get_doctor_profile(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor not found")
    avails = doctor_repo.get_availability(db, doctor_id)
    return [_avail_to_out(a) for a in avails]


def get_available_slots(db: Session, doctor_id: str, target_date: date) -> list[AvailableSlot]:
    profile = doctor_repo.get_doctor_profile(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check if on leave
    leave = doctor_repo.get_leave_for_date(db, doctor_id, target_date)
    if leave:
        return []

    day_of_week = target_date.weekday()
    avails = doctor_repo.get_availability(db, doctor_id)
    day_avails = [a for a in avails if a.day_of_week == day_of_week]
    if not day_avails:
        return []

    duration = timedelta(minutes=profile.consultation_duration_minutes)
    date_start = datetime.combine(target_date, time.min, tzinfo=timezone.utc)
    date_end = date_start + timedelta(days=1)

    # Get existing appointments
    booked = appt_repo.get_appointments_for_doctor_on_date(db, doctor_id, date_start, date_end)
    booked_ranges = [(a.start_time, a.end_time) for a in booked]

    slots = []
    for avail in day_avails:
        slot_start = datetime.combine(target_date, avail.start_time, tzinfo=timezone.utc)
        window_end = datetime.combine(target_date, avail.end_time, tzinfo=timezone.utc)
        while slot_start + duration <= window_end:
            slot_end = slot_start + duration
            is_booked = any(
                s < slot_end and e > slot_start for s, e in booked_ranges
            )
            if not is_booked:
                # Check active holds
                held = appt_repo.get_active_hold(db, doctor_id, slot_start, slot_end)
                slots.append(AvailableSlot(
                    start_time=slot_start,
                    end_time=slot_end,
                    is_held=held is not None,
                ))
            slot_start += duration
    return slots


# --- Leave ---

def add_leave_service(db: Session, doctor_id: str, data: DoctorLeaveCreate) -> DoctorLeaveOut:
    profile = doctor_repo.get_doctor_profile(db, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor not found")

    existing = doctor_repo.get_leave_for_date(db, doctor_id, data.leave_date)
    if existing:
        raise HTTPException(status_code=409, detail="Leave already exists for this date")

    leave = DoctorLeave(
        doctor_id=doctor_id,
        leave_date=data.leave_date,
        reason=data.reason,
    )
    created = doctor_repo.add_leave(db, leave)

    # Cancel affected appointments
    _cancel_appointments_for_leave(db, doctor_id, data.leave_date, profile)

    return DoctorLeaveOut.model_validate(created)


def _cancel_appointments_for_leave(
    db: Session, doctor_id: str, leave_date: date, profile: DoctorProfile
) -> None:
    from app.models.appointment import AppointmentStatus
    date_start = datetime.combine(leave_date, time.min, tzinfo=timezone.utc)
    date_end = date_start + timedelta(days=1)
    appointments = appt_repo.get_appointments_for_doctor_on_date(db, doctor_id, date_start, date_end)
    for appt in appointments:
        appt.status = AppointmentStatus.cancelled
        appt.cancellation_reason = f"Doctor on leave: {leave_date}"
        # Queue notification
        from app.services.notification import queue_leave_cancellation
        try:
            queue_leave_cancellation(db, appt, profile)
        except Exception:
            logger.exception("Failed to queue leave cancellation notification")
    db.commit()


def delete_leave_service(db: Session, doctor_id: str, leave_id: str) -> None:
    leaves = doctor_repo.get_leave_days(db, doctor_id)
    target = None
    for l in leaves:
        if l.id == leave_id:
            target = l
            break
    if not target:
        raise HTTPException(status_code=404, detail="Leave not found")
    doctor_repo.delete_leave(db, target)


def get_leave_service(db: Session, doctor_id: str) -> list[DoctorLeaveOut]:
    leaves = doctor_repo.get_leave_days(db, doctor_id)
    return [DoctorLeaveOut.model_validate(l) for l in leaves]


# --- Helpers ---

def _profile_to_out(p: DoctorProfile) -> DoctorProfileOut:
    from app.schemas.doctor import DoctorUserOut
    user_out = None
    if p.user:
        user_out = DoctorUserOut(id=p.user.id, email=p.user.email, full_name=p.user.full_name)
    return DoctorProfileOut(
        id=p.id,
        user_id=p.user_id,
        specialization=p.specialization,
        bio=p.bio,
        consultation_duration_minutes=p.consultation_duration_minutes,
        is_active=p.is_active,
        created_at=p.created_at,
        user=user_out,
    )


def _avail_to_out(a: DoctorAvailability) -> AvailabilityOut:
    return AvailabilityOut(
        id=a.id,
        doctor_id=a.doctor_id,
        day_of_week=a.day_of_week,
        start_time=a.start_time.strftime("%H:%M"),
        end_time=a.end_time.strftime("%H:%M"),
        is_active=a.is_active,
    )
