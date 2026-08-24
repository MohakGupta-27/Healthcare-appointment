import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
    getAvailableSlots,
    getDoctor,
    getDoctorAvailability,
} from "../services/doctors";
import { createAppointment } from "../services/appointments";
import type {
    AvailableSlot,
    Availability,
    DoctorProfile,
} from "../types";

export default function DoctorDetailPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
    const [availability, setAvailability] = useState<Availability[]>([]);
    const [slots, setSlots] = useState<AvailableSlot[]>([]);

    const [selectedDate, setSelectedDate] = useState(
        new Date().toISOString().split("T")[0],
    );
    const [selectedSlot, setSelectedSlot] =
        useState<AvailableSlot | null>(null);

    const [reason, setReason] = useState("");
    const [symptoms, setSymptoms] = useState("");

    const [loading, setLoading] = useState(true);
    const [slotsLoading, setSlotsLoading] = useState(false);
    const [booking, setBooking] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!id) return;

        const loadDoctor = async () => {
            try {
                setLoading(true);
                setError("");

                const [doctorData, availabilityData] = await Promise.all([
                    getDoctor(id),
                    getDoctorAvailability(id),
                ]);

                setDoctor(doctorData);
                setAvailability(availabilityData);
            } catch (err) {
                console.error(err);
                setError("Unable to load doctor details.");
            } finally {
                setLoading(false);
            }
        };

        loadDoctor();
    }, [id]);

    useEffect(() => {
        if (!id || !selectedDate) return;

        const loadSlots = async () => {
            try {
                setSlotsLoading(true);
                setSelectedSlot(null);

                const data = await getAvailableSlots(id, selectedDate);
                setSlots(data);
            } catch (err) {
                console.error(err);
                setSlots([]);
            } finally {
                setSlotsLoading(false);
            }
        };

        loadSlots();
    }, [id, selectedDate]);

    const handleBooking = async () => {
        if (!id || !selectedSlot) {
            setError("Please select an available time slot.");
            return;
        }

        try {
            setBooking(true);
            setError("");

            const appointment = await createAppointment({
                doctor_id: id,
                start_time: selectedSlot.start_time,
                reason: reason.trim() || undefined,
                symptoms: symptoms.trim() || undefined,
            });

            navigate(`/appointments/${appointment.id}`);
        } catch (err: any) {
            console.error(err);

            const message =
                err?.response?.data?.detail ||
                "Unable to book this appointment.";

            setError(message);
        } finally {
            setBooking(false);
        }
    };

    if (loading) {
        return (
            <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-500">
                Loading doctor details...
            </div>
        );
    }

    if (error && !doctor) {
        return (
            <div className="space-y-4">
                <Link
                    to="/doctors"
                    className="text-sm font-medium text-teal-600 hover:text-teal-700"
                >
                    ← Back to doctors
                </Link>

                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </div>
            </div>
        );
    }

    if (!doctor) return null;

    const doctorName = doctor.user?.full_name || "Doctor";

    const activeAvailability = availability.filter(
        (item) => item.is_active,
    );

    return (
        <div className="space-y-8">
            <Link
                to="/doctors"
                className="inline-block text-sm font-medium text-teal-600 hover:text-teal-700"
            >
                ← Back to doctors
            </Link>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Doctor information */}
                <div className="lg:col-span-1">
                    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
                        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-teal-500 to-blue-600 flex items-center justify-center text-white font-bold text-3xl">
                            {doctorName.charAt(0).toUpperCase()}
                        </div>

                        <h1 className="mt-5 text-2xl font-bold text-slate-900">
                            Dr. {doctorName}
                        </h1>

                        <p className="mt-1 font-medium text-teal-600">
                            {doctor.specialization}
                        </p>

                        <p className="mt-5 text-sm leading-6 text-slate-600">
                            {doctor.bio || "No biography available."}
                        </p>

                        <div className="mt-6 pt-5 border-t border-slate-100 space-y-3">
                            <InfoRow
                                label="Consultation"
                                value={`${doctor.consultation_duration_minutes} minutes`}
                            />

                            {doctor.user?.email && (
                                <InfoRow
                                    label="Email"
                                    value={doctor.user.email}
                                />
                            )}

                            <InfoRow
                                label="Status"
                                value={doctor.is_active ? "Active" : "Inactive"}
                            />
                        </div>
                    </div>

                    <div className="mt-6 rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
                        <h2 className="font-semibold text-slate-800">
                            Weekly availability
                        </h2>

                        {activeAvailability.length === 0 ? (
                            <p className="mt-3 text-sm text-slate-500">
                                No availability has been configured.
                            </p>
                        ) : (
                            <div className="mt-4 space-y-2">
                                {activeAvailability.map((slot) => (
                                    <div
                                        key={slot.id}
                                        className="flex justify-between text-sm"
                                    >
                                        <span className="text-slate-600">
                                            {dayName(slot.day_of_week)}
                                        </span>

                                        <span className="font-medium text-slate-800">
                                            {slot.start_time} – {slot.end_time}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Booking */}
                <div className="lg:col-span-2">
                    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
                        <h2 className="text-xl font-semibold text-slate-900">
                            Book an appointment
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            Select a date and an available time slot.
                        </p>

                        <div className="mt-6">
                            <label className="block text-sm font-medium text-slate-700">
                                Date
                            </label>

                            <input
                                type="date"
                                value={selectedDate}
                                min={new Date().toISOString().split("T")[0]}
                                onChange={(event) =>
                                    setSelectedDate(event.target.value)
                                }
                                className="mt-2 w-full sm:w-auto rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                            />
                        </div>

                        <div className="mt-6">
                            <h3 className="text-sm font-medium text-slate-700">
                                Available times
                            </h3>

                            {slotsLoading ? (
                                <p className="mt-3 text-sm text-slate-500">
                                    Loading available slots...
                                </p>
                            ) : slots.length === 0 ? (
                                <div className="mt-3 rounded-xl bg-slate-50 border border-slate-200 p-5 text-sm text-slate-500">
                                    No available slots for this date.
                                </div>
                            ) : (
                                <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                                    {slots.map((slot) => {
                                        const selected =
                                            selectedSlot?.start_time === slot.start_time;

                                        return (
                                            <button
                                                key={slot.start_time}
                                                type="button"
                                                disabled={slot.is_held}
                                                onClick={() => setSelectedSlot(slot)}
                                                className={`rounded-xl border px-3 py-3 text-sm font-medium transition ${slot.is_held
                                                    ? "cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400"
                                                    : selected
                                                        ? "border-teal-600 bg-teal-600 text-white"
                                                        : "border-slate-200 bg-white text-slate-700 hover:border-teal-400 hover:bg-teal-50"
                                                    }`}
                                            >
                                                {formatTime(slot.start_time)}
                                                {slot.is_held && (
                                                    <span className="block text-xs mt-1">
                                                        Held
                                                    </span>
                                                )}
                                            </button>
                                        );
                                    })}
                                </div>
                            )}
                        </div>

                        <div className="mt-8 space-y-5">
                            <div>
                                <label className="block text-sm font-medium text-slate-700">
                                    Reason for visit
                                </label>

                                <input
                                    type="text"
                                    value={reason}
                                    onChange={(event) =>
                                        setReason(event.target.value)
                                    }
                                    placeholder="e.g. Regular consultation"
                                    className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700">
                                    Symptoms
                                </label>

                                <textarea
                                    value={symptoms}
                                    onChange={(event) =>
                                        setSymptoms(event.target.value)
                                    }
                                    rows={4}
                                    placeholder="Describe any symptoms you are experiencing..."
                                    className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none resize-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                                />
                            </div>
                        </div>

                        <div className="mt-6 flex items-center justify-between gap-4 rounded-xl bg-slate-50 border border-slate-200 p-4">
                            <div>
                                <p className="text-xs text-slate-500">
                                    Selected slot
                                </p>

                                <p className="mt-1 font-semibold text-slate-800">
                                    {selectedSlot
                                        ? `${selectedDate} • ${formatTime(selectedSlot.start_time)}`
                                        : "No slot selected"}
                                </p>
                            </div>

                            <button
                                type="button"
                                disabled={!selectedSlot || booking || !doctor.is_active}
                                onClick={handleBooking}
                                className="rounded-xl bg-teal-600 px-6 py-3 text-sm font-semibold text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-slate-300 transition"
                            >
                                {booking ? "Booking..." : "Book appointment"}
                            </button>
                        </div>

                        {!doctor.is_active && (
                            <p className="mt-3 text-sm text-red-600">
                                This doctor is currently inactive and cannot accept
                                appointments.
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function InfoRow({
    label,
    value,
}: {
    label: string;
    value: string;
}) {
    return (
        <div className="flex justify-between gap-4 text-sm">
            <span className="text-slate-500">{label}</span>
            <span className="text-right font-medium text-slate-700">
                {value}
            </span>
        </div>
    );
}

function dayName(day: number) {
    const days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ];

    return days[day] ?? "Unknown";
}

function formatTime(value: string) {
    const date = new Date(value);

    return date.toLocaleTimeString([], {
        hour: "numeric",
        minute: "2-digit",
    });
}