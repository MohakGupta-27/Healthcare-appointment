from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    doctor_id: str
    start_time: datetime
    reason: Optional[str] = None
    symptoms: Optional[str] = None


class AppointmentOut(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    start_time: datetime
    end_time: datetime
    status: str
    reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    patient_name: str = ""
    patient_email: str = ""
    doctor_name: str = ""
    doctor_specialization: str = ""

    model_config = {"from_attributes": True}


class AppointmentCancel(BaseModel):
    cancellation_reason: Optional[str] = None


class SlotHoldRequest(BaseModel):
    doctor_id: str
    start_time: datetime


class SlotHoldOut(BaseModel):
    id: str
    doctor_id: str
    start_time: datetime
    end_time: datetime
    expires_at: datetime
    status: str

    model_config = {"from_attributes": True}


# --- Symptoms ---

class SymptomSubmit(BaseModel):
    symptoms: str = Field(..., min_length=1, max_length=5000)


class SymptomOut(BaseModel):
    id: str
    appointment_id: str
    symptoms: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- AI Summary ---

class AISummaryOut(BaseModel):
    id: str
    appointment_id: str
    summary_type: str
    urgency_level: Optional[str] = None
    chief_complaint: Optional[str] = None
    suggested_questions: Optional[str] = None
    patient_summary: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    disclaimer: str = "AI-generated pre-visit summary — not a medical diagnosis."

    model_config = {"from_attributes": True}


# --- Clinical Notes ---

class ClinicalNoteCreate(BaseModel):
    notes: str = Field(..., min_length=1)
    diagnosis: Optional[str] = None
    follow_up_instructions: Optional[str] = None


class ClinicalNoteOut(BaseModel):
    id: str
    appointment_id: str
    doctor_id: str
    notes: str
    diagnosis: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Prescription ---

class MedicationCreate(BaseModel):
    name: str = Field(..., max_length=200)
    dosage: str = Field(..., max_length=100)
    frequency: str = Field(..., max_length=50)
    start_date: str
    end_date: Optional[str] = None
    instructions: Optional[str] = None


class MedicationOut(BaseModel):
    id: str
    prescription_id: str
    name: str
    dosage: str
    frequency: str
    start_date: str
    end_date: Optional[str] = None
    instructions: Optional[str] = None

    model_config = {"from_attributes": True}


class PrescriptionCreate(BaseModel):
    notes: Optional[str] = None
    medications: list[MedicationCreate] = []


class PrescriptionOut(BaseModel):
    id: str
    appointment_id: str
    doctor_id: str
    notes: Optional[str] = None
    medications: list[MedicationOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}
