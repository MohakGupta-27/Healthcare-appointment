import { FormEvent, useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../auth/AuthContext";
import type { Availability, DoctorProfile } from "../types";

const DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
];

export default function DoctorProfilePage() {
    const { user } = useAuth();

    const [profile, setProfile] = useState<DoctorProfile | null>(null);
    const [availability, setAvailability] = useState<Availability[]>([]);

    const [specialization, setSpecialization] = useState("");
    const [bio, setBio] = useState("");
    const [duration, setDuration] = useState("30");

    const [day, setDay] = useState("0");
    const [startTime, setStartTime] = useState("09:00");
    const [endTime, setEndTime] = useState("17:00");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const loadProfile = async () => {
        if (!user) return;

        try {
            setLoading(true);

            /*
             * There is no GET /doctors/me endpoint in the current backend.
             * We therefore find the doctor's profile from the public doctor list
             * using the authenticated user's ID.
             */
            const doctorsResponse = await api.get<
                Array<{
                    id: string;
                    user_id: string;
                    specialization: string;
                    bio: string;
                    consultation_duration_minutes: number;
                    is_active: boolean;
                    doctor_name: string;
                    doctor_email: string;
                }>
            >("/doctors");

            const doctor = doctorsResponse.data.find(
                (item) => item.user_id === user.id,
            );

            if (!doctor) {
                setError("Doctor profile not found.");
                return;
            }

            const [profileResponse, availabilityResponse] = await Promise.all([
                api.get<DoctorProfile>(`/doctors/${doctor.id}`),
                api.get<Availability[]>(`/doctors/${doctor.id}/availability`),
            ]);

            const data = profileResponse.data;

            setProfile(data);
            setSpecialization(data.specialization);
            setBio(data.bio || "");
            setDuration(String(data.consultation_duration_minutes));
            setAvailability(availabilityResponse.data);
            setError("");
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Failed to load doctor profile.",
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadProfile();
    }, [user]);

    const saveProfile = async (event: FormEvent) => {
        event.preventDefault();

        try {
            setSaving(true);
            setError("");
            setSuccess("");

            await api.patch("/doctors/me/profile", {
                specialization,
                bio,
                consultation_duration_minutes: Number(duration),
            });

            setSuccess("Profile updated successfully.");
            await loadProfile();
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to update profile.");
        } finally {
            setSaving(false);
        }
    };

    const addAvailability = async () => {
        const updated = [
            ...availability.map((item) => ({
                day_of_week: item.day_of_week,
                start_time: item.start_time,
                end_time: item.end_time,
            })),
            {
                day_of_week: Number(day),
                start_time: startTime,
                end_time: endTime,
            },
        ];

        try {
            setSaving(true);
            setError("");
            setSuccess("");

            await api.put("/doctors/me/availability", {
                slots: updated,
            });

            setSuccess("Availability updated successfully.");
            await loadProfile();
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Failed to update availability.",
            );
        } finally {
            setSaving(false);
        }
    };

    const removeAvailability = async (availabilityId: string) => {
        const updated = availability
            .filter((item) => item.id !== availabilityId)
            .map((item) => ({
                day_of_week: item.day_of_week,
                start_time: item.start_time,
                end_time: item.end_time,
            }));

        try {
            setSaving(true);
            setError("");
            setSuccess("");

            await api.put("/doctors/me/availability", {
                slots: updated,
            });

            setSuccess("Availability updated successfully.");
            await loadProfile();
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Failed to update availability.",
            );
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-500">
                Loading profile...
            </div>
        );
    }

    if (!profile) {
        return (
            <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center">
                <p className="text-slate-600">
                    {error || "Doctor profile not found."}
                </p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-slate-900">
                    My Doctor Profile
                </h1>
                <p className="mt-1 text-slate-500">
                    Manage your professional information and consultation availability.
                </p>
            </div>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                    {error}
                </div>
            )}

            {success && (
                <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
                    {success}
                </div>
            )}

            <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-slate-900">
                    Professional Information
                </h2>

                <form onSubmit={saveProfile} className="mt-5 space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">
                            Name
                        </label>
                        <input
                            value={user?.full_name || ""}
                            disabled
                            className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-slate-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">
                            Email
                        </label>
                        <input
                            value={user?.email || ""}
                            disabled
                            className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-slate-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">
                            Specialization
                        </label>
                        <input
                            value={specialization}
                            onChange={(e) => setSpecialization(e.target.value)}
                            className="w-full rounded-xl border border-slate-300 px-4 py-2.5 outline-none focus:border-teal-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">
                            Bio
                        </label>
                        <textarea
                            value={bio}
                            onChange={(e) => setBio(e.target.value)}
                            rows={5}
                            className="w-full rounded-xl border border-slate-300 px-4 py-2.5 outline-none focus:border-teal-500 resize-none"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">
                            Consultation Duration
                        </label>
                        <select
                            value={duration}
                            onChange={(e) => setDuration(e.target.value)}
                            className="w-full rounded-xl border border-slate-300 px-4 py-2.5 bg-white"
                        >
                            <option value="15">15 minutes</option>
                            <option value="30">30 minutes</option>
                            <option value="45">45 minutes</option>
                            <option value="60">60 minutes</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        disabled={saving}
                        className="px-5 py-2.5 rounded-xl bg-teal-600 text-white font-medium hover:bg-teal-700 disabled:opacity-50"
                    >
                        {saving ? "Saving..." : "Save Profile"}
                    </button>
                </form>
            </section>

            <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-slate-900">
                    Availability
                </h2>

                <div className="mt-5 grid sm:grid-cols-4 gap-3">
                    <select
                        value={day}
                        onChange={(e) => setDay(e.target.value)}
                        className="rounded-xl border border-slate-300 px-3 py-2.5 bg-white"
                    >
                        {DAYS.map((name, index) => (
                            <option key={name} value={index}>
                                {name}
                            </option>
                        ))}
                    </select>

                    <input
                        type="time"
                        value={startTime}
                        onChange={(e) => setStartTime(e.target.value)}
                        className="rounded-xl border border-slate-300 px-3 py-2.5"
                    />

                    <input
                        type="time"
                        value={endTime}
                        onChange={(e) => setEndTime(e.target.value)}
                        className="rounded-xl border border-slate-300 px-3 py-2.5"
                    />

                    <button
                        type="button"
                        onClick={addAvailability}
                        disabled={saving}
                        className="rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50"
                    >
                        Add Slot
                    </button>
                </div>

                <div className="mt-6 space-y-2">
                    {availability.length === 0 ? (
                        <p className="text-sm text-slate-500">
                            No availability configured.
                        </p>
                    ) : (
                        availability.map((item) => (
                            <div
                                key={item.id}
                                className="flex items-center justify-between rounded-xl bg-slate-50 border border-slate-200 px-4 py-3"
                            >
                                <div>
                                    <span className="font-medium text-slate-800">
                                        {DAYS[item.day_of_week]}
                                    </span>

                                    <span className="text-slate-500 ml-3">
                                        {item.start_time} – {item.end_time}
                                    </span>
                                </div>

                                <button
                                    type="button"
                                    onClick={() => removeAvailability(item.id)}
                                    disabled={saving}
                                    className="text-sm text-red-600 hover:underline disabled:opacity-50"
                                >
                                    Remove
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </section>
        </div>
    );
}