from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.doctor_profile import DoctorProfile
from app.models.availability import DoctorAvailability
from app.models.doctor_leave import DoctorLeave
from app.models.user import User


def create_doctor_profile(db: Session, profile: DoctorProfile) -> DoctorProfile:
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_doctor_profile(db: Session, doctor_id: str) -> DoctorProfile | None:
    return db.execute(
        select(DoctorProfile).where(DoctorProfile.id == doctor_id)
    ).scalar_one_or_none()


def get_doctor_by_user_id(db: Session, user_id: str) -> DoctorProfile | None:
    return db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user_id)
    ).scalar_one_or_none()


def list_doctors(
    db: Session,
    specialization: str | None = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50,
) -> list[DoctorProfile]:
    stmt = select(DoctorProfile).join(User, DoctorProfile.user_id == User.id)
    if active_only:
        stmt = stmt.where(DoctorProfile.is_active == True)
    if specialization:
        stmt = stmt.where(DoctorProfile.specialization.ilike(f"%{specialization}%"))
    stmt = stmt.offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def update_doctor_profile(db: Session, profile: DoctorProfile) -> DoctorProfile:
    db.commit()
    db.refresh(profile)
    return profile


# --- Availability ---

def set_availability(db: Session, doctor_id: str, slots: list[DoctorAvailability]) -> list[DoctorAvailability]:
    # Deactivate all existing
    existing = db.execute(
        select(DoctorAvailability).where(DoctorAvailability.doctor_id == doctor_id)
    ).scalars().all()
    for slot in existing:
        db.delete(slot)
    db.flush()
    for slot in slots:
        db.add(slot)
    db.commit()
    result = db.execute(
        select(DoctorAvailability).where(DoctorAvailability.doctor_id == doctor_id)
    ).scalars().all()
    return list(result)


def get_availability(db: Session, doctor_id: str) -> list[DoctorAvailability]:
    return list(db.execute(
        select(DoctorAvailability).where(
            and_(DoctorAvailability.doctor_id == doctor_id, DoctorAvailability.is_active == True)
        )
    ).scalars().all())


# --- Leave ---

def add_leave(db: Session, leave: DoctorLeave) -> DoctorLeave:
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


def get_leave_days(db: Session, doctor_id: str) -> list[DoctorLeave]:
    return list(db.execute(
        select(DoctorLeave).where(DoctorLeave.doctor_id == doctor_id).order_by(DoctorLeave.leave_date)
    ).scalars().all())


def get_leave_for_date(db: Session, doctor_id: str, target_date: date) -> DoctorLeave | None:
    return db.execute(
        select(DoctorLeave).where(
            and_(DoctorLeave.doctor_id == doctor_id, DoctorLeave.leave_date == target_date)
        )
    ).scalar_one_or_none()


def delete_leave(db: Session, leave: DoctorLeave) -> None:
    db.delete(leave)
    db.commit()
