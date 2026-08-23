import { useAuth } from "../auth/AuthContext";

export default function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-teal-700">
            Dashboard
          </p>
          <h1 className="mt-1 text-2xl font-bold text-slate-900">
            Welcome, {user?.full_name}
          </h1>
        </div>
        <button
          onClick={logout}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Sign out
        </button>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm">
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="font-medium text-slate-500">Email</dt>
            <dd className="mt-1 text-slate-900">{user?.email}</dd>
          </div>
          <div>
            <dt className="font-medium text-slate-500">Role</dt>
            <dd className="mt-1 capitalize text-slate-900">{user?.role}</dd>
          </div>
        </dl>
      </div>

      <p className="text-sm text-slate-500">
        Appointment booking, doctor schedules, and admin panels will be added in
        later phases.
      </p>
    </div>
  );
}
