import api from "./api";
import type {
    Availability,
    AvailableSlot,
    DoctorListItem,
    DoctorProfile,
    DoctorLeave,
} from "../types";

export async function listDoctors(
    specialization?: string,
): Promise<DoctorListItem[]> {
    const response = await api.get<DoctorListItem[]>("/doctors", {
        params: specialization ? { specialization } : undefined,
    });

    return response.data;
}

export async function getDoctor(
    doctorId: string,
): Promise<DoctorProfile> {
    const response = await api.get<DoctorProfile>(`/doctors/${doctorId}`);
    return response.data;
}

export async function getDoctorAvailability(
    doctorId: string,
): Promise<Availability[]> {
    const response = await api.get<Availability[]>(
        `/doctors/${doctorId}/availability`,
    );

    return response.data;
}

export async function getAvailableSlots(
    doctorId: string,
    date: string,
): Promise<AvailableSlot[]> {
    const response = await api.get<AvailableSlot[]>(
        `/doctors/${doctorId}/slots`,
        {
            params: { date },
        },
    );

    return response.data;
}

export async function updateMyDoctorProfile(data: {
    specialization?: string;
    bio?: string;
    consultation_duration_minutes?: number;
    is_active?: boolean;
}): Promise<DoctorProfile> {
    const response = await api.patch<DoctorProfile>(
        "/doctors/me/profile",
        data,
    );

    return response.data;
}

export async function setMyAvailability(
    slots: {
        day_of_week: number;
        start_time: string;
        end_time: string;
    }[],
): Promise<Availability[]> {
    const response = await api.put<Availability[]>(
        "/doctors/me/availability",
        { slots },
    );

    return response.data;
}

// Admin

export async function createDoctor(data: {
    user_id: string;
    specialization: string;
    bio: string;
    consultation_duration_minutes: number;
}): Promise<DoctorProfile> {
    const response = await api.post<DoctorProfile>(
        "/admin/doctors",
        data,
    );

    return response.data;
}

export async function updateDoctor(
    doctorId: string,
    data: {
        specialization?: string;
        bio?: string;
        consultation_duration_minutes?: number;
        is_active?: boolean;
    },
): Promise<DoctorProfile> {
    const response = await api.patch<DoctorProfile>(
        `/admin/doctors/${doctorId}`,
        data,
    );

    return response.data;
}

export async function setDoctorAvailability(
    doctorId: string,
    slots: {
        day_of_week: number;
        start_time: string;
        end_time: string;
    }[],
): Promise<Availability[]> {
    const response = await api.put<Availability[]>(
        `/admin/doctors/${doctorId}/availability`,
        { slots },
    );

    return response.data;
}

export async function getDoctorLeaves(
    doctorId: string,
): Promise<DoctorLeave[]> {
    const response = await api.get<DoctorLeave[]>(
        `/admin/doctors/${doctorId}/leave`,
    );

    return response.data;
}

export async function addDoctorLeave(
    doctorId: string,
    data: {
        leave_date: string;
        reason?: string;
    },
): Promise<DoctorLeave> {
    const response = await api.post<DoctorLeave>(
        `/admin/doctors/${doctorId}/leave`,
        data,
    );

    return response.data;
}

export async function deleteDoctorLeave(
    doctorId: string,
    leaveId: string,
): Promise<void> {
    await api.delete(
        `/admin/doctors/${doctorId}/leave/${leaveId}`,
    );
}