import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-teal-500 to-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">H+</span>
          </div>
          <span className="font-bold text-lg text-slate-800">HealthCare</span>
        </Link>

        <div className="flex items-center gap-1">
          <Link to="/dashboard" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition">
            Dashboard
          </Link>

          {user.role === "patient" && (
            <>
              <Link to="/doctors" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition">
                Find Doctors
              </Link>
              <Link to="/appointments" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition">
                My Appointments
              </Link>
            </>
          )}

          {user.role === "doctor" && (
            <>
              <Link to="/appointments" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition">
                Appointments
              </Link>
              <Link to="/doctor/profile" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition">
                My Profile
              </Link>
            </>
          )}

          {user.role === "admin" && (
            <>
              <Link to="/admin/doctors" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition">
                Manage Doctors
              </Link>
              <Link to="/appointments" className="px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition">
                Appointments
              </Link>
            </>
          )}
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-slate-700">{user.full_name}</p>
            <p className="text-xs text-slate-400 capitalize">{user.role}</p>
          </div>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 rounded-lg bg-slate-100 text-sm font-medium text-slate-600 hover:bg-slate-200 transition"
          >
            Sign out
          </button>
        </div>
      </div>
    </nav>
  );
}
