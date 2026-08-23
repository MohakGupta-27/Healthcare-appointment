import { Route, Routes } from "react-router-dom";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-sm font-medium uppercase tracking-wide text-teal-700">
          Phase 0
        </p>
        <h1 className="mt-2 text-3xl font-semibold">Healthcare Appointment Manager</h1>
        <p className="mt-4 text-slate-600">
          Frontend scaffold is running. Patient, doctor, and admin dashboards will
          be added in later phases.
        </p>
        <Routes>
          <Route path="/" element={null} />
        </Routes>
      </main>
    </div>
  );
}
