import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import {
    cancelAppointment,
    completeAppointment,
    generateAISummary,
    getAISummaries,
    getAppointment,
    getPrescription,
    getSymptoms,
    submitClinicalNotes,
} from "../services/appointments";
import type {
    AISummary,
    Appointment,
    Prescription,
    SymptomSubmission,
} from "../types";

export default function AppointmentDetailPage() {
    const { id } = useParams<{ id: string }>();
    const { user } = useAuth();

    const [appointment, setAppointment] =
        useState<Appointment | null>(null);
    const [symptoms, setSymptoms] =
        useState<SymptomSubmission | null>(null);
    const [summaries, setSummaries] = useState<AISummary[]>([]);
    const [prescription, setPrescription] =
        useState<Prescription | null>(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [notes, setNotes] = useState("");
    const [diagnosis, setDiagnosis] = useState("");
    const [followUp, setFollowUp] = useState("");

    const [savingNotes, setSavingNotes] = useState(false);
    const [generatingSummary, setGeneratingSummary] =
        useState(false);
    const [completing, setCompleting] = useState(false);

    const loadData = async () => {
        if (!id) return;

        try {
            setLoading(true);
            setError("");

            const appointmentData = await getAppointment(id);

            setAppointment(appointmentData);

            const [symptomsData, summariesData, prescriptionData] =
                await Promise.all([
                    getSymptoms(id),
                    getAISummaries(id),
                    getPrescription(id),
                ]);

            setSymptoms(symptomsData);
            setSummaries(summariesData);
            setPrescription(prescriptionData);
        } catch (err: any) {
            console.error(err);

            setError(
                err?.response?.data?.detail ||
                "Unable to load appointment.",
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [id]);

    const handleCancel = async () => {
        if (!id) return;

        const confirmed = window.confirm(
            "Are you sure you want to cancel this appointment?",
        );

        if (!confirmed) return;

        try {
            await cancelAppointment(id);
            await loadData();
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                "Unable to cancel appointment.",
            );
        }
    };

    const handleComplete = async () => {
        if (!id) return;

        try {
            setCompleting(true);
            setError("");

            await completeAppointment(id);
            await loadData();
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                "Unable to complete appointment.",
            );
        } finally {
            setCompleting(false);
        }
    };

    const handleSaveNotes = async () => {
        if (!id || !notes.trim()) {
            setError("Clinical notes are required.");
            return;
        }

        try {
            setSavingNotes(true);
            setError("");

            await submitClinicalNotes(id, {
                notes: notes.trim(),
                diagnosis: diagnosis.trim() || undefined,
                follow_up_instructions:
                    followUp.trim() || undefined,
            });

            await loadData();
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                "Unable to save clinical notes.",
            );
        } finally {
            setSavingNotes(false);
        }
    };

    const handleGenerateSummary = async () => {
        if (!id) return;

        try {
            setGeneratingSummary(true);
            setError("");

            await generateAISummary(id);
            await loadData();
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                "Unable to generate AI summary.",
            );
        } finally {
            setGeneratingSummary(false);
        }
    };

    if (loading) {
        return (
            <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-500">
                Loading appointment...
            </div>
        );
    }

    if (!appointment) {
        return (
            <div className="space-y-4">
                <Link
                    to="/appointments"
                    className="text-sm font-medium text-teal-600"
                >
                    ← Back to appointments
                </Link>

                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error || "Appointment not found."}
                </div>
            </div>
        );
    }

    const start = new Date(appointment.start_time);
    const end = new Date(appointment.end_time);

    const isDoctor = user?.role === "doctor";
    const isScheduled = appointment.status === "scheduled";

    return (
        <div className="space-y-6">
            <Link
                to="/appointments"
                className="inline-block text-sm font-medium text-teal-600 hover:text-teal-700"
            >
                ← Back to appointments
            </Link>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            {/* Appointment header */}
            <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
                <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-5">
                    <div>
                        <p className="text-sm text-slate-500">
                            Appointment
                        </p>

                        <h1 className="mt-1 text-2xl font-bold text-slate-900">
                            {isDoctor
                                ? appointment.patient_name || "Patient"
                                : `Dr. ${appointment.doctor_name || "Doctor"}`}
                        </h1>

                        {!isDoctor && (
                            <p className="mt-1 text-sm font-medium text-teal-600">
                                {appointment.doctor_specialization}
                            </p>
                        )}
                    </div>

                    <span
                        className={`self-start rounded-full px-4 py-2 text-sm font-semibold capitalize ${appointment.status === "scheduled"
                            ? "bg-emerald-50 text-emerald-700"
                            : appointment.status === "completed"
                                ? "bg-blue-50 text-blue-700"
                                : "bg-red-50 text-red-700"
                            }`}
                    >
                        {appointment.status}
                    </span>
                </div>

                <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <DetailBox
                        label="Date"
                        value={start.toLocaleDateString([], {
                            weekday: "long",
                            month: "long",
                            day: "numeric",
                            year: "numeric",
                        })}
                    />

                    <DetailBox
                        label="Time"
                        value={`${start.toLocaleTimeString([], {
                            hour: "numeric",
                            minute: "2-digit",
                        })} – ${end.toLocaleTimeString([], {
                            hour: "numeric",
                            minute: "2-digit",
                        })}`}
                    />

                    <DetailBox
                        label="Reason"
                        value={appointment.reason || "Not provided"}
                    />
                </div>

                {appointment.cancellation_reason && (
                    <div className="mt-5 rounded-xl bg-red-50 border border-red-100 p-4">
                        <p className="text-sm font-semibold text-red-700">
                            Cancellation reason
                        </p>
                        <p className="mt-1 text-sm text-red-600">
                            {appointment.cancellation_reason}
                        </p>
                    </div>
                )}

                {isScheduled && (
                    <div className="mt-6 flex flex-wrap gap-3">
                        <button
                            type="button"
                            onClick={handleCancel}
                            className="rounded-xl border border-red-200 px-5 py-2.5 text-sm font-semibold text-red-600 hover:bg-red-50 transition"
                        >
                            Cancel appointment
                        </button>

                        {isDoctor && (
                            <button
                                type="button"
                                onClick={handleComplete}
                                disabled={completing}
                                className="rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-700 disabled:bg-slate-300 transition"
                            >
                                {completing
                                    ? "Completing..."
                                    : "Mark as completed"}
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Patient symptoms */}
            <section className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-slate-800">
                    Symptoms
                </h2>

                {symptoms ? (
                    <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-600">
                        {symptoms.symptoms}
                    </p>
                ) : (
                    <p className="mt-3 text-sm text-slate-500">
                        No symptoms have been submitted.
                    </p>
                )}
            </section>

            {/* AI summaries */}
            {summaries.length > 0 && (
                <section className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
                    <h2 className="text-lg font-semibold text-slate-800">
                        AI Visit Summary
                    </h2>

                    <div className="mt-5 space-y-5">
                        {summaries.map((summary) => (
                            <div
                                key={summary.id}
                                className="rounded-xl bg-slate-50 border border-slate-200 p-5"
                            >
                                <div className="flex flex-wrap items-center justify-between gap-3">
                                    <h3 className="font-medium text-slate-800">
                                        {summary.summary_type === "pre_visit"
                                            ? "Pre-visit analysis"
                                            : "Post-visit summary"}
                                    </h3>

                                    <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 capitalize">
                                        {summary.status}
                                    </span>
                                </div>

                                {summary.urgency_level && (
                                    <p className="mt-4 text-sm">
                                        <span className="font-medium">
                                            Urgency:
                                        </span>{" "}
                                        {summary.urgency_level}
                                    </p>
                                )}

                                {summary.chief_complaint && (
                                    <p className="mt-2 text-sm text-slate-600">
                                        <span className="font-medium text-slate-700">
                                            Chief complaint:
                                        </span>{" "}
                                        {summary.chief_complaint}
                                    </p>
                                )}

                                {summary.suggested_questions && (
                                    <p className="mt-2 whitespace-pre-wrap text-sm text-slate-600">
                                        <span className="font-medium text-slate-700">
                                            Suggested questions:
                                        </span>{" "}
                                        {summary.suggested_questions}
                                    </p>
                                )}

                                {summary.patient_summary && (
                                    <div className="mt-4">
                                        <p className="text-sm font-medium text-slate-700">
                                            Patient-friendly summary
                                        </p>

                                        <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600">
                                            {summary.patient_summary}
                                        </p>
                                    </div>
                                )}

                                <p className="mt-4 text-xs text-slate-400">
                                    {summary.disclaimer}
                                </p>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* Doctor clinical workflow */}
            {isDoctor && (
                <section className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
                    <h2 className="text-lg font-semibold text-slate-800">
                        Clinical notes
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        Record clinical information for this visit.
                    </p>

                    <div className="mt-5 space-y-4">
                        <textarea
                            value={notes}
                            onChange={(event) =>
                                setNotes(event.target.value)
                            }
                            rows={5}
                            placeholder="Clinical notes..."
                            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none resize-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                        />

                        <input
                            type="text"
                            value={diagnosis}
                            onChange={(event) =>
                                setDiagnosis(event.target.value)
                            }
                            placeholder="Diagnosis (optional)"
                            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                        />

                        <textarea
                            value={followUp}
                            onChange={(event) =>
                                setFollowUp(event.target.value)
                            }
                            rows={3}
                            placeholder="Follow-up instructions (optional)"
                            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none resize-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                        />

                        <button
                            type="button"
                            onClick={handleSaveNotes}
                            disabled={savingNotes}
                            className="rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-700 disabled:bg-slate-300 transition"
                        >
                            {savingNotes
                                ? "Saving..."
                                : "Save clinical notes"}
                        </button>
                    </div>

                    <div className="mt-6 pt-6 border-t border-slate-100">
                        <button
                            type="button"
                            onClick={handleGenerateSummary}
                            disabled={generatingSummary}
                            className="rounded-xl border border-purple-200 bg-purple-50 px-5 py-2.5 text-sm font-semibold text-purple-700 hover:bg-purple-100 disabled:opacity-50 transition"
                        >
                            {generatingSummary
                                ? "Generating..."
                                : "Generate AI patient summary"}
                        </button>
                    </div>
                </section>
            )}

            {/* Prescription */}
            <section className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-slate-800">
                    Prescription
                </h2>

                {!prescription ? (
                    <p className="mt-3 text-sm text-slate-500">
                        No prescription has been issued.
                    </p>
                ) : (
                    <div className="mt-5 space-y-4">
                        {prescription.notes && (
                            <div className="rounded-xl bg-slate-50 p-4">
                                <p className="text-xs text-slate-400">
                                    Doctor's notes
                                </p>
                                <p className="mt-1 text-sm text-slate-700">
                                    {prescription.notes}
                                </p>
                            </div>
                        )}

                        {prescription.medications.length === 0 ? (
                            <p className="text-sm text-slate-500">
                                No medications listed.
                            </p>
                        ) : (
                            <div className="space-y-3">
                                {prescription.medications.map((medication) => (
                                    <div
                                        key={medication.id}
                                        className="rounded-xl border border-slate-200 p-4"
                                    >
                                        <h3 className="font-semibold text-slate-800">
                                            {medication.name}
                                        </h3>

                                        <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                                            <div>
                                                <span className="text-slate-400">
                                                    Dosage
                                                </span>
                                                <p className="font-medium text-slate-700">
                                                    {medication.dosage}
                                                </p>
                                            </div>

                                            <div>
                                                <span className="text-slate-400">
                                                    Frequency
                                                </span>
                                                <p className="font-medium text-slate-700">
                                                    {medication.frequency}
                                                </p>
                                            </div>

                                            <div>
                                                <span className="text-slate-400">
                                                    Dates
                                                </span>
                                                <p className="font-medium text-slate-700">
                                                    {medication.start_date}
                                                    {medication.end_date
                                                        ? ` – ${medication.end_date}`
                                                        : ""}
                                                </p>
                                            </div>
                                        </div>

                                        {medication.instructions && (
                                            <p className="mt-3 text-sm text-slate-600">
                                                <span className="font-medium">
                                                    Instructions:
                                                </span>{" "}
                                                {medication.instructions}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </section>
        </div>
    );
}

function DetailBox({
    label,
    value,
}: {
    label: string;
    value: string;
}) {
    return (
        <div className="rounded-xl bg-slate-50 border border-slate-100 p-4">
            <p className="text-xs text-slate-400">{label}</p>
            <p className="mt-1 text-sm font-medium text-slate-700">
                {value}
            </p>
        </div>
    );
}