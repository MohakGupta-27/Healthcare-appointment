"""Public and doctor-facing doctor endpoints."""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.doctor import (
    AvailabilityBulkSet,
    AvailabilityOut,
    AvailableSlot,
    DoctorListOut,
    DoctorProfileOut,
    DoctorProfileUpdate,
)
from app.services.doctor import (
    get_availability_service,
    get_available_slots,
    get_doctor_detail,
    list_doctors_service,
    set_availability_service,
    update_doctor_profile_by_admin,
)
from app.repositories.doctor import get_doctor_by_user_id

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorListOut])
def list_doctors(
    specialization: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[DoctorListOut]:
    return list_doctors_service(db, specialization=specialization, skip=skip, limit=limit)


@router.get("/{doctor_id}", response_model=DoctorProfileOut)
def get_doctor(
    doctor_id: str,
    db: Session = Depends(get_db),
) -> DoctorProfileOut:
    return get_doctor_detail(db, doctor_id)


@router.get("/{doctor_id}/availability", response_model=list[AvailabilityOut])
def get_doctor_availability(
    doctor_id: str,
    db: Session = Depends(get_db),
) -> list[AvailabilityOut]:
    return get_availability_service(db, doctor_id)


@router.get("/{doctor_id}/slots", response_model=list[AvailableSlot])
def get_doctor_slots(
    doctor_id: str,
    date: date = Query(...),
    db: Session = Depends(get_db),
) -> list[AvailableSlot]:
    return get_available_slots(db, doctor_id, date)


# Doctor self-management
@router.patch("/me/profile", response_model=DoctorProfileOut)
def update_own_profile(
    data: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
) -> DoctorProfileOut:
    profile = get_doctor_by_user_id(db, current_user.id)
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return update_doctor_profile_by_admin(db, profile.id, data)


@router.put("/me/availability", response_model=list[AvailabilityOut])
def set_own_availability(
    data: AvailabilityBulkSet,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
) -> list[AvailabilityOut]:
    profile = get_doctor_by_user_id(db, current_user.id)
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return set_availability_service(db, profile.id, data.slots)
