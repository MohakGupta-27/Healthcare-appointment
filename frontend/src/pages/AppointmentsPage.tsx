import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import {
    cancelAppointment,
    listAppointments,
} from "../services/appointments";
import type { Appointment } from "../types";

export default function AppointmentsPage() {
    const { user } = useAuth();

    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadAppointments = async () => {
        try {
            setLoading(true);
            setError("");

            const data = await listAppointments();
            setAppointments(data);
        } catch (err) {
            console.error(err);
            setError("Unable to load appointments.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAppointments();
    }, []);

    const handleCancel = async (appointmentId: string) => {
        const confirmed = window.confirm(
            "Are you sure you want to cancel this appointment?",
        );

        if (!confirmed) return;

        try {
            await cancelAppointment(appointmentId);
            await loadAppointments();
        } catch (err: any) {
            console.error(err);

            setError(
                err?.response?.data?.detail ||
                "Unable to cancel the appointment.",
            );
        }
    };

    if (loading) {
        return (
            <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-500">
                Loading appointments...
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">
                        {user?.role === "doctor"
                            ? "Appointments"
                            : user?.role === "admin"
                                ? "All Appointments"
                                : "My Appointments"}
                    </h1>

                    <p className="mt-1 text-slate-500">
                        View appointment history and manage scheduled visits.
                    </p>
                </div>

                {user?.role === "patient" && (
                    <Link
                        to="/doctors"
                        className="inline-flex items-center justify-center rounded-xl bg-teal-600 px-5 py-3 text-sm font-semibold text-white hover:bg-teal-700 transition"
                    >
                        Find a Doctor
                    </Link>
                )}
            </div>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            {appointments.length === 0 ? (
                <div className="rounded-2xl bg-white border border-slate-200 p-10 text-center">
                    <div className="text-4xl">📅</div>

                    <h2 className="mt-4 text-lg font-semibold text-slate-800">
                        No appointments
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        {user?.role === "patient"
                            ? "You don't have any appointments yet."
                            : "There are no appointments to display."}
                    </p>
                </div>
            ) : (
                <div className="space-y-4">
                    {appointments.map((appointment) => (
                        <AppointmentCard
                            key={appointment.id}
                            appointment={appointment}
                            role={user?.role}
                            onCancel={handleCancel}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

function AppointmentCard({
    appointment,
    role,
    onCancel,
}: {
    appointment: Appointment;
    role?: "patient" | "doctor" | "admin";
    onCancel: (id: string) => void;
}) {
    const statusClass = {
        scheduled: "bg-emerald-50 text-emerald-700",
        completed: "bg-blue-50 text-blue-700",
        cancelled: "bg-red-50 text-red-700",
    }[appointment.status];

    const date = new Date(appointment.start_time);

    return (
        <div className="rounded-2xl bg-white border border-slate-200 p-5 shadow-sm">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5">
                <div className="flex items-start gap-4">
                    <div className="w-12 h-12 shrink-0 rounded-xl bg-gradient-to-br from-teal-500 to-blue-600 flex items-center justify-center text-white text-xl">
                        📅
                    </div>

                    <div>
                        <h2 className="font-semibold text-slate-800">
                            {role === "doctor" ? (
                                appointment.patient_name || "Patient"
                            ) : (
                                <>
                                    Dr. {appointment.doctor_name || "Doctor"}
                                </>
                            )}
                        </h2>

                        {role !== "doctor" && appointment.doctor_specialization && (
                            <p className="text-sm text-teal-600">
                                {appointment.doctor_specialization}
                            </p>
                        )}

                        {role === "doctor" && appointment.patient_email && (
                            <p className="text-sm text-slate-500">
                                {appointment.patient_email}
                            </p>
                        )}

                        <div className="mt-2 text-sm text-slate-600">
                            <span className="font-medium">
                                {date.toLocaleDateString([], {
                                    weekday: "short",
                                    month: "short",
                                    day: "numeric",
                                    year: "numeric",
                                })}
                            </span>

                            <span className="mx-2">•</span>

                            <span>
                                {date.toLocaleTimeString([], {
                                    hour: "numeric",
                                    minute: "2-digit",
                                })}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                    <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${statusClass}`}
                    >
                        {appointment.status}
                    </span>

                    <Link
                        to={`/appointments/${appointment.id}`}
                        className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition"
                    >
                        View details
                    </Link>

                    {appointment.status === "scheduled" &&
                        (role === "patient" || role === "doctor") && (
                            <button
                                type="button"
                                onClick={() => onCancel(appointment.id)}
                                className="rounded-xl border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition"
                            >
                                Cancel
                            </button>
                        )}
                </div>
            </div>

            {appointment.reason && (
                <div className="mt-4 pt-4 border-t border-slate-100">
                    <span className="text-xs text-slate-400">
                        Reason
                    </span>
                    <p className="mt-1 text-sm text-slate-600">
                        {appointment.reason}
                    </p>
                </div>
            )}

            {appointment.cancellation_reason && (
                <div className="mt-4 rounded-xl bg-red-50 border border-red-100 px-4 py-3">
                    <p className="text-xs font-medium text-red-600">
                        Cancellation reason
                    </p>
                    <p className="mt-1 text-sm text-red-700">
                        {appointment.cancellation_reason}
                    </p>
                </div>
            )}
        </div>
    );
}