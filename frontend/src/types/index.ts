export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "patient" | "doctor" | "admin";
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface DoctorProfile {
  id: string;
  user_id: string;
  specialization: string;
  bio: string;
  consultation_duration_minutes: number;
  is_active: boolean;
  created_at: string;
  user?: { id: string; email: string; full_name: string };
}

export interface DoctorListItem {
  id: string;
  user_id: string;
  specialization: string;
  bio: string;
  consultation_duration_minutes: number;
  is_active: boolean;
  doctor_name: string;
  doctor_email: string;
}

export interface Availability {
  id: string;
  doctor_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_active: boolean;
}

export interface AvailableSlot {
  start_time: string;
  end_time: string;
  is_held: boolean;
}

export interface DoctorLeave {
  id: string;
  doctor_id: string;
  leave_date: string;
  reason?: string;
  created_at: string;
}

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  start_time: string;
  end_time: string;
  status: "scheduled" | "cancelled" | "completed";
  reason?: string;
  cancellation_reason?: string;
  created_at: string;
  patient_name: string;
  patient_email: string;
  doctor_name: string;
  doctor_specialization: string;
}

export interface SymptomSubmission {
  id: string;
  appointment_id: string;
  symptoms: string;
  created_at: string;
}

export interface AISummary {
  id: string;
  appointment_id: string;
  summary_type: "pre_visit" | "post_visit";
  urgency_level?: string;
  chief_complaint?: string;
  suggested_questions?: string;
  patient_summary?: string;
  status: "pending" | "completed" | "failed";
  error_message?: string;
  disclaimer: string;
  created_at: string;
}

export interface ClinicalNote {
  id: string;
  appointment_id: string;
  doctor_id: string;
  notes: string;
  diagnosis?: string;
  follow_up_instructions?: string;
  created_at: string;
}

export interface Medication {
  id: string;
  prescription_id: string;
  name: string;
  dosage: string;
  frequency: string;
  start_date: string;
  end_date?: string;
  instructions?: string;
}

export interface Prescription {
  id: string;
  appointment_id: string;
  doctor_id: string;
  notes?: string;
  medications: Medication[];
  created_at: string;
}
