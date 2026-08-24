"""Admin doctor management endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.doctor import (
    AvailabilityBulkSet,
    AvailabilityOut,
    DoctorLeaveCreate,
    DoctorLeaveOut,
    DoctorProfileCreate,
    DoctorProfileOut,
    DoctorProfileUpdate,
)
from app.services.doctor import (
    add_leave_service,
    create_doctor_profile,
    delete_leave_service,
    get_leave_service,
    set_availability_service,
    update_doctor_profile_by_admin,
)

router = APIRouter(prefix="/admin/doctors", tags=["admin-doctors"])


@router.post("", response_model=DoctorProfileOut, status_code=201)
def admin_create_doctor(
    data: DoctorProfileCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> DoctorProfileOut:
    return create_doctor_profile(db, data)


@router.patch("/{doctor_id}", response_model=DoctorProfileOut)
def admin_update_doctor(
    doctor_id: str,
    data: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> DoctorProfileOut:
    return update_doctor_profile_by_admin(db, doctor_id, data)


@router.put("/{doctor_id}/availability", response_model=list[AvailabilityOut])
def admin_set_availability(
    doctor_id: str,
    data: AvailabilityBulkSet,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> list[AvailabilityOut]:
    return set_availability_service(db, doctor_id, data.slots)


@router.post("/{doctor_id}/leave", response_model=DoctorLeaveOut, status_code=201)
def admin_add_leave(
    doctor_id: str,
    data: DoctorLeaveCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> DoctorLeaveOut:
    return add_leave_service(db, doctor_id, data)


@router.delete("/{doctor_id}/leave/{leave_id}", status_code=204)
def admin_delete_leave(
    doctor_id: str,
    leave_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> None:
    delete_leave_service(db, doctor_id, leave_id)


@router.get("/{doctor_id}/leave", response_model=list[DoctorLeaveOut])
def admin_get_leave(
    doctor_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
) -> list[DoctorLeaveOut]:
    return get_leave_service(db, doctor_id)
