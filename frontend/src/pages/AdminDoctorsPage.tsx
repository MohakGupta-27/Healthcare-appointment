import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import type { DoctorListItem } from "../types";

export default function AdminDoctorsPage() {
    const [doctors, setDoctors] = useState<DoctorListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadDoctors = async () => {
        try {
            setLoading(true);
            const response = await api.get<DoctorListItem[]>("/doctors");
            setDoctors(response.data);
            setError("");
        } catch {
            setError("Failed to load doctors.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDoctors();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">
                        Manage Doctors
                    </h1>
                    <p className="mt-1 text-slate-500">
                        Create and manage doctor profiles, availability, and status.
                    </p>
                </div>

                <Link
                    to="/admin/doctors/new"
                    className="inline-flex items-center justify-center px-4 py-2.5 rounded-xl bg-teal-600 text-white font-medium hover:bg-teal-700 transition"
                >
                    + Add Doctor
                </Link>
            </div>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-500">
                    Loading doctors...
                </div>
            ) : doctors.length === 0 ? (
                <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center">
                    <p className="text-slate-600">No doctors found.</p>
                    <Link
                        to="/admin/doctors/new"
                        className="inline-block mt-4 text-teal-600 font-medium hover:underline"
                    >
                        Add the first doctor
                    </Link>
                </div>
            ) : (
                <div className="grid gap-4">
                    {doctors.map((doctor) => (
                        <div
                            key={doctor.id}
                            className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm"
                        >
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-3">
                                        <h2 className="text-lg font-semibold text-slate-900">
                                            {doctor.doctor_name}
                                        </h2>

                                        <span
                                            className={`px-2.5 py-1 rounded-full text-xs font-medium ${doctor.is_active
                                                    ? "bg-emerald-100 text-emerald-700"
                                                    : "bg-slate-100 text-slate-500"
                                                }`}
                                        >
                                            {doctor.is_active ? "Active" : "Inactive"}
                                        </span>
                                    </div>

                                    <p className="text-sm text-teal-600 mt-1">
                                        {doctor.specialization}
                                    </p>

                                    <p className="text-sm text-slate-500 mt-2">
                                        {doctor.doctor_email}
                                    </p>

                                    <p className="text-sm text-slate-500 mt-1">
                                        Consultation: {doctor.consultation_duration_minutes} minutes
                                    </p>
                                </div>

                                <Link
                                    to={`/admin/doctors/${doctor.id}`}
                                    className="inline-flex items-center justify-center px-4 py-2 rounded-xl border border-slate-200 text-sm font-medium text-slate-700 hover:bg-slate-50 transition"
                                >
                                    Manage
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}