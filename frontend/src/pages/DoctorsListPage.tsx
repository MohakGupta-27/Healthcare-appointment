import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listDoctors } from "../services/doctors";
import type { DoctorListItem } from "../types";

export default function DoctorsListPage() {
    const [doctors, setDoctors] = useState<DoctorListItem[]>([]);
    const [specialization, setSpecialization] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadDoctors = async () => {
        try {
            setLoading(true);
            setError("");

            const data = await listDoctors(
                specialization.trim() || undefined,
            );

            setDoctors(data);
        } catch (err) {
            console.error(err);
            setError("Unable to load doctors. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDoctors();
    }, []);

    const handleSearch = (event: React.FormEvent) => {
        event.preventDefault();
        loadDoctors();
    };

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-slate-900">
                    Find a Doctor
                </h1>
                <p className="mt-1 text-slate-500">
                    Browse available doctors and choose a convenient appointment
                    slot.
                </p>
            </div>

            <form
                onSubmit={handleSearch}
                className="rounded-2xl bg-white border border-slate-200 p-5 shadow-sm"
            >
                <div className="flex flex-col sm:flex-row gap-3">
                    <input
                        type="text"
                        value={specialization}
                        onChange={(event) =>
                            setSpecialization(event.target.value)
                        }
                        placeholder="Search by specialization, e.g. Cardiologist"
                        className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                    />

                    <button
                        type="submit"
                        className="rounded-xl bg-teal-600 px-6 py-3 text-sm font-semibold text-white hover:bg-teal-700 transition"
                    >
                        Search
                    </button>
                </div>
            </form>

            {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-500">
                    Loading doctors...
                </div>
            ) : doctors.length === 0 ? (
                <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center">
                    <h2 className="text-lg font-semibold text-slate-800">
                        No doctors found
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                        Try another specialization.
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {doctors.map((doctor) => (
                        <DoctorCard key={doctor.id} doctor={doctor} />
                    ))}
                </div>
            )}
        </div>
    );
}

function DoctorCard({ doctor }: { doctor: DoctorListItem }) {
    return (
        <Link
            to={`/doctors/${doctor.id}`}
            className="group block"
        >
            <div className="h-full rounded-2xl bg-white border border-slate-200 p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <div className="flex items-start justify-between gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-teal-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg">
                        {doctor.doctor_name?.charAt(0).toUpperCase() || "D"}
                    </div>

                    <span
                        className={`rounded-full px-3 py-1 text-xs font-medium ${doctor.is_active
                                ? "bg-emerald-50 text-emerald-700"
                                : "bg-slate-100 text-slate-500"
                            }`}
                    >
                        {doctor.is_active ? "Available" : "Inactive"}
                    </span>
                </div>

                <h2 className="mt-5 text-lg font-semibold text-slate-800 group-hover:text-teal-700 transition">
                    Dr. {doctor.doctor_name || "Doctor"}
                </h2>

                <p className="mt-1 text-sm font-medium text-teal-600">
                    {doctor.specialization}
                </p>

                <p className="mt-3 text-sm text-slate-500 line-clamp-3">
                    {doctor.bio || "No biography available."}
                </p>

                <div className="mt-5 pt-4 border-t border-slate-100">
                    <p className="text-xs text-slate-400">
                        Consultation duration
                    </p>
                    <p className="mt-1 text-sm font-medium text-slate-700">
                        {doctor.consultation_duration_minutes} minutes
                    </p>
                </div>
            </div>
        </Link>
    );
}