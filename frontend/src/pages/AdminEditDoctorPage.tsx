import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../services/api";
import type { Availability, DoctorLeave, DoctorProfile } from "../types";

const DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
];


export default function AdminEditDoctorPage() {
    const { id } = useParams<{ id: string }>();

    const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
    const [availability, setAvailability] = useState<Availability[]>([]);
    const [leaves, setLeaves] = useState<DoctorLeave[]>([]);

    const [specialization, setSpecialization] = useState("");
    const [bio, setBio] = useState("");
    const [duration, setDuration] = useState("30");
    const [isActive, setIsActive] = useState(true);

    const [day, setDay] = useState("0");
    const [startTime, setStartTime] = useState("09:00");
    const [endTime, setEndTime] = useState("17:00");

    const [leaveDate, setLeaveDate] = useState("");
    const [leaveReason, setLeaveReason] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    const loadData = async () => {
        if (!id) return;

        try {
            setLoading(true);

            const [doctorResponse, availabilityResponse, leaveResponse] =
                await Promise.all([
                    api.get<DoctorProfile>(`/doctors/${id}`),
                    api.get<Availability[]>(`/doctors/${id}/availability`),
                    api.get<DoctorLeave[]>(`/admin/doctors/${id}/leave`),
                ]);

            const data = doctorResponse.data;

            setDoctor(data);
            setSpecialization(data.specialization);
            setBio(data.bio || "");
            setDuration(String(data.consultation_duration_minutes));
            setIsActive(data.is_active);

            setAvailability(availabilityResponse.data);
            setLeaves(leaveResponse.data);
            setError("");
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Failed to load doctor information.",
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [id]);

    const saveProfile = async (event: FormEvent) => {
        event.preventDefault();

        if (!id) return;

        try {
            setSaving(true);
            setError("");

            await api.patch(`/admin/doctors/${id}`, {
                specialization,
                bio,
                consultation_duration_minutes: Number(duration),
                is_active: isActive,
            });

            await loadData();
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to update doctor.");
        } finally {
            setSaving(false);
        }
    };

    const addAvailability = async () => {
        if (!id) return;

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

            await api.put(`/admin/doctors/${id}/availability`, {
                slots: updated,
            });

            await loadData();
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Failed to update availability.",
            );
        } finally {
            setSaving(false);
        }
    };

    const removeAvailability = async (availabilityId: string) => {
        if (!id) return;

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

            await api.put(`/admin/doctors/${id}/availability`, {
                slots: updated,
            });

            await loadData();
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Failed to update availability.",
            );
        } finally {
            setSaving(false);
        }
    };

    const addLeave = async () => {
        if (!id || !leaveDate) {
            setError("Please select a leave date.");
            return;
        }

        try {
            setSaving(true);
            setError("");

            await api.post(`/admin/doctors/${id}/leave`, {
                leave_date: leaveDate,
                reason: leaveReason || undefined,
            });

            setLeaveDate("");
            setLeaveReason("");

            await loadData();
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to add leave.");
        } finally {
            setSaving(false);
        }
    };

    const deleteLeave = async (leaveId: string) => {
        if (!id) return;

        try {
            setSaving(true);
            setError("");

            await api.delete(`/admin/doctors/${id}/leave/${leaveId}`);

            await loadData();
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to remove leave.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-500">
                Loading doctor...
            </div>
        );
    }

    if (!doctor) {
        return (
            <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center">
                <p className="text-slate-600">Doctor not found.</p>
                <Link
                    to="/admin/doctors"
                    className="inline-block mt-4 text-teal-600 hover:underline"
                >
                    Back to doctors
                </Link>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div>
                <Link
                    to="/admin/doctors"
                    className="text-sm text-teal-600 hover:underline"
                >
                    ← Back to doctors
                </Link>

                <div className="mt-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">
                            {doctor.user?.full_name || "Doctor"}
                        </h1>
                        <p className="text-slate-500 mt-1">{doctor.user?.email}</p>
                    </div>

                    <span
                        className={`px-3 py-1.5 rounded-full text-sm font-medium w-fit ${isActive
                            ? "bg-emerald-100 text-emerald-700"
                            : "bg-slate-100 text-slate-500"
                            }`}
                    >
                        {isActive ? "Active" : "Inactive"}
                    </span>
                </div>
            </div>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                    {error}
                </div>
            )}

            {/* Profile */}
            <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-slate-900">
                    Doctor Profile
                </h2>

                <form onSubmit={saveProfile} className="mt-5 space-y-5">
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
                            rows={4}
                            className="w-full rounded-xl border border-slate-300 px-4 py-2.5 outline-none focus:border-teal-500 resize-none"
                        />
                    </div>

                    <div className="grid sm:grid-cols-2 gap-4">
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

                        <label className="flex items-center gap-3 sm:pt-8">
                            <input
                                type="checkbox"
                                checked={isActive}
                                onChange={(e) => setIsActive(e.target.checked)}
                                className="w-4 h-4"
                            />
                            <span className="text-sm font-medium text-slate-700">
                                Doctor is active
                            </span>
                        </label>
                    </div>

                    <button
                        type="submit"
                        disabled={saving}
                        className="px-5 py-2.5 rounded-xl bg-teal-600 text-white text-sm font-medium hover:bg-teal-700 disabled:opacity-50"
                    >
                        {saving ? "Saving..." : "Save Profile"}
                    </button>
                </form>
            </section>

            {/* Availability */}
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

            {/* Leave */}
            <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-slate-900">
                    Doctor Leave
                </h2>

                <div className="mt-5 grid sm:grid-cols-3 gap-3">
                    <input
                        type="date"
                        value={leaveDate}
                        onChange={(e) => setLeaveDate(e.target.value)}
                        className="rounded-xl border border-slate-300 px-3 py-2.5"
                    />

                    <input
                        value={leaveReason}
                        onChange={(e) => setLeaveReason(e.target.value)}
                        placeholder="Reason (optional)"
                        className="rounded-xl border border-slate-300 px-3 py-2.5"
                    />

                    <button
                        type="button"
                        onClick={addLeave}
                        disabled={saving}
                        className="rounded-xl bg-purple-600 text-white font-medium hover:bg-purple-700 disabled:opacity-50"
                    >
                        Add Leave
                    </button>
                </div>

                <div className="mt-6 space-y-2">
                    {leaves.length === 0 ? (
                        <p className="text-sm text-slate-500">
                            No leave dates configured.
                        </p>
                    ) : (
                        leaves.map((leave) => (
                            <div
                                key={leave.id}
                                className="flex items-center justify-between rounded-xl bg-slate-50 border border-slate-200 px-4 py-3"
                            >
                                <div>
                                    <span className="font-medium text-slate-800">
                                        {leave.leave_date}
                                    </span>

                                    {leave.reason && (
                                        <span className="text-sm text-slate-500 ml-3">
                                            {leave.reason}
                                        </span>
                                    )}
                                </div>

                                <button
                                    type="button"
                                    onClick={() => deleteLeave(leave.id)}
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