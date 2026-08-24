import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function AdminCreateDoctorPage() {
    const navigate = useNavigate();

    const [userId, setUserId] = useState("");
    const [specialization, setSpecialization] = useState("");
    const [bio, setBio] = useState("");
    const [duration, setDuration] = useState("30");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();

        if (!userId.trim() || !specialization.trim()) {
            setError("User ID and specialization are required.");
            return;
        }

        try {
            setLoading(true);
            setError("");

            const response = await api.post("/admin/doctors", {
                user_id: userId.trim(),
                specialization: specialization.trim(),
                bio: bio.trim(),
                consultation_duration_minutes: Number(duration),
            });

            navigate(`/admin/doctors/${response.data.id}`);
        } catch (err: any) {
            setError(
                err.response?.data?.detail || "Failed to create doctor profile.",
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <div className="mb-6">
                <Link
                    to="/admin/doctors"
                    className="text-sm text-teal-600 hover:underline"
                >
                    ← Back to doctors
                </Link>

                <h1 className="text-3xl font-bold text-slate-900 mt-3">
                    Add Doctor
                </h1>

                <p className="mt-1 text-slate-500">
                    Create a doctor profile for an existing user account.
                </p>
            </div>

            <form
                onSubmit={handleSubmit}
                className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5"
            >
                {error && (
                    <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                        {error}
                    </div>
                )}

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        User ID
                    </label>
                    <input
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        placeholder="Enter the existing user's UUID"
                        className="w-full rounded-xl border border-slate-300 px-4 py-2.5 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                    />
                    <p className="mt-1.5 text-xs text-slate-400">
                        The user must already exist in the system.
                    </p>
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Specialization
                    </label>
                    <input
                        value={specialization}
                        onChange={(e) => setSpecialization(e.target.value)}
                        placeholder="e.g. Cardiologist"
                        className="w-full rounded-xl border border-slate-300 px-4 py-2.5 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
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
                        placeholder="Short professional biography"
                        className="w-full rounded-xl border border-slate-300 px-4 py-2.5 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100 resize-none"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                        Consultation Duration
                    </label>
                    <select
                        value={duration}
                        onChange={(e) => setDuration(e.target.value)}
                        className="w-full rounded-xl border border-slate-300 px-4 py-2.5 bg-white outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                    >
                        <option value="15">15 minutes</option>
                        <option value="30">30 minutes</option>
                        <option value="45">45 minutes</option>
                        <option value="60">60 minutes</option>
                    </select>
                </div>

                <div className="flex justify-end gap-3 pt-2">
                    <Link
                        to="/admin/doctors"
                        className="px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-700 hover:bg-slate-50"
                    >
                        Cancel
                    </Link>

                    <button
                        type="submit"
                        disabled={loading}
                        className="px-5 py-2.5 rounded-xl bg-teal-600 text-white text-sm font-medium hover:bg-teal-700 disabled:opacity-50"
                    >
                        {loading ? "Creating..." : "Create Doctor"}
                    </button>
                </div>
            </form>
        </div>
    );
}