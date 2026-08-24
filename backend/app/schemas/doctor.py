from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, Field


# --- Doctor Profile ---

class DoctorProfileCreate(BaseModel):
    user_id: str
    specialization: str = Field(..., max_length=100)
    bio: str = ""
    consultation_duration_minutes: int = Field(30, ge=5, le=120)


class DoctorProfileUpdate(BaseModel):
    specialization: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    consultation_duration_minutes: Optional[int] = Field(None, ge=5, le=120)
    is_active: Optional[bool] = None


class DoctorUserOut(BaseModel):
    id: str
    email: str
    full_name: str

    model_config = {"from_attributes": True}


class DoctorProfileOut(BaseModel):
    id: str
    user_id: str
    specialization: str
    bio: str
    consultation_duration_minutes: int
    is_active: bool
    created_at: datetime
    user: Optional[DoctorUserOut] = None

    model_config = {"from_attributes": True}


class DoctorListOut(BaseModel):
    id: str
    user_id: str
    specialization: str
    bio: str
    consultation_duration_minutes: int
    is_active: bool
    doctor_name: str = ""
    doctor_email: str = ""

    model_config = {"from_attributes": True}


# --- Availability ---

class AvailabilityCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")


class AvailabilityOut(BaseModel):
    id: str
    doctor_id: str
    day_of_week: int
    start_time: str
    end_time: str
    is_active: bool

    model_config = {"from_attributes": True}


class AvailabilityBulkSet(BaseModel):
    slots: list[AvailabilityCreate]


# --- Leave ---

class DoctorLeaveCreate(BaseModel):
    leave_date: date
    reason: Optional[str] = None


class DoctorLeaveOut(BaseModel):
    id: str
    doctor_id: str
    leave_date: date
    reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Available Slot ---

class AvailableSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    is_held: bool = False
