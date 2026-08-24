import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Welcome back, {user.full_name}
        </h1>
        <p className="mt-1 text-slate-500">
          {user.role === "patient" && "Manage your health appointments and find doctors."}
          {user.role === "doctor" && "View your appointments and manage patient care."}
          {user.role === "admin" && "Manage doctors, availability, and appointments."}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {user.role === "patient" && (
          <>
            <DashCard to="/doctors" icon="🔍" title="Find Doctors" desc="Search doctors by specialization and book appointments" color="from-teal-500 to-emerald-600" />
            <DashCard to="/appointments" icon="📅" title="My Appointments" desc="View upcoming and past appointments" color="from-blue-500 to-indigo-600" />
          </>
        )}

        {user.role === "doctor" && (
          <>
            <DashCard to="/appointments" icon="📋" title="My Appointments" desc="View today's and upcoming appointments" color="from-teal-500 to-emerald-600" />
            <DashCard to="/doctor/profile" icon="⚙️" title="My Profile" desc="Manage your profile and availability" color="from-purple-500 to-indigo-600" />
          </>
        )}

        {user.role === "admin" && (
          <>
            <DashCard to="/admin/doctors" icon="👨‍⚕️" title="Manage Doctors" desc="Create, edit, and manage doctor profiles" color="from-teal-500 to-emerald-600" />
            <DashCard to="/admin/doctors/new" icon="➕" title="Add Doctor" desc="Create a new doctor profile" color="from-blue-500 to-indigo-600" />
            <DashCard to="/appointments" icon="📅" title="All Appointments" desc="View and manage all appointments" color="from-purple-500 to-violet-600" />
          </>
        )}
      </div>

      <div className="mt-8 rounded-2xl bg-white/60 backdrop-blur-sm border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-2">Account Info</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-slate-500">Email</span>
            <p className="font-medium text-slate-800">{user.email}</p>
          </div>
          <div>
            <span className="text-slate-500">Role</span>
            <p className="font-medium text-slate-800 capitalize">{user.role}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function DashCard({ to, icon, title, desc, color }: { to: string; icon: string; title: string; desc: string; color: string }) {
  return (
    <Link to={to} className="group block">
      <div className="relative overflow-hidden rounded-2xl bg-white border border-slate-200 p-6 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
        <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${color} rounded-bl-[4rem] opacity-10 group-hover:opacity-20 transition`} />
        <div className="text-3xl mb-3">{icon}</div>
        <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
        <p className="mt-1 text-sm text-slate-500">{desc}</p>
      </div>
    </Link>
  );
}
