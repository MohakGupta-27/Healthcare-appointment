import api from "./api";
import type {
    AISummary,
    Appointment,
    ClinicalNote,
    Prescription,
    SymptomSubmission,
} from "../types";

export async function listAppointments(): Promise<Appointment[]> {
    const response = await api.get<Appointment[]>("/appointments");
    return response.data;
}

export async function getAppointment(
    appointmentId: string,
): Promise<Appointment> {
    const response = await api.get<Appointment>(
        `/appointments/${appointmentId}`,
    );

    return response.data;
}

export async function holdSlot(data: {
    doctor_id: string;
    start_time: string;
}) {
    const response = await api.post("/appointments/hold", data);
    return response.data;
}

export async function createAppointment(data: {
    doctor_id: string;
    start_time: string;
    reason?: string;
    symptoms?: string;
}): Promise<Appointment> {
    const response = await api.post<Appointment>(
        "/appointments",
        data,
    );

    return response.data;
}

export async function cancelAppointment(
    appointmentId: string,
    cancellationReason?: string,
): Promise<Appointment> {
    const response = await api.patch<Appointment>(
        `/appointments/${appointmentId}/cancel`,
        {
            cancellation_reason: cancellationReason,
        },
    );

    return response.data;
}

export async function completeAppointment(
    appointmentId: string,
): Promise<Appointment> {
    const response = await api.patch<Appointment>(
        `/appointments/${appointmentId}/complete`,
    );

    return response.data;
}

// Symptoms

export async function submitSymptoms(
    appointmentId: string,
    symptoms: string,
): Promise<SymptomSubmission> {
    const response = await api.post<SymptomSubmission>(
        `/appointments/${appointmentId}/symptoms`,
        { symptoms },
    );

    return response.data;
}

export async function getSymptoms(
    appointmentId: string,
): Promise<SymptomSubmission | null> {
    const response = await api.get<SymptomSubmission | null>(
        `/appointments/${appointmentId}/symptoms`,
    );

    return response.data;
}

// AI summaries

export async function getAISummaries(
    appointmentId: string,
): Promise<AISummary[]> {
    const response = await api.get<AISummary[]>(
        `/appointments/${appointmentId}/summary`,
    );

    return response.data;
}

// Clinical notes

export async function submitClinicalNotes(
    appointmentId: string,
    data: {
        notes: string;
        diagnosis?: string;
        follow_up_instructions?: string;
    },
): Promise<ClinicalNote> {
    const response = await api.post<ClinicalNote>(
        `/appointments/${appointmentId}/visit-notes`,
        data,
    );

    return response.data;
}

export async function generateAISummary(
    appointmentId: string,
): Promise<AISummary> {
    const response = await api.post<AISummary>(
        `/appointments/${appointmentId}/generate-summary`,
    );

    return response.data;
}

// Prescription

export async function getPrescription(
    appointmentId: string,
): Promise<Prescription | null> {
    const response = await api.get<Prescription | null>(
        `/appointments/${appointmentId}/prescription`,
    );

    return response.data;
}

export async function createPrescription(
    appointmentId: string,
    data: {
        notes?: string;
        medications: {
            name: string;
            dosage: string;
            frequency: string;
            start_date: string;
            end_date?: string;
            instructions?: string;
        }[];
    },
): Promise<Prescription> {
    const response = await api.post<Prescription>(
        `/appointments/${appointmentId}/prescription`,
        data,
    );

    return response.data;
}