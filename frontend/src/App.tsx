import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import DoctorsListPage from "./pages/DoctorsListPage";
import DoctorDetailPage from "./pages/DoctorDetailPage";
import AppointmentsPage from "./pages/AppointmentsPage";
import AppointmentDetailPage from "./pages/AppointmentDetailPage";
import AdminDoctorsPage from "./pages/AdminDoctorsPage";
import AdminCreateDoctorPage from "./pages/AdminCreateDoctorPage";
import AdminEditDoctorPage from "./pages/AdminEditDoctorPage";
import DoctorProfilePage from "./pages/DoctorProfilePage";

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-teal-50 text-slate-900">
        <Navbar />
        <main className="px-4 sm:px-6 py-8 max-w-7xl mx-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/doctors" element={<ProtectedRoute><DoctorsListPage /></ProtectedRoute>} />
            <Route path="/doctors/:id" element={<ProtectedRoute><DoctorDetailPage /></ProtectedRoute>} />
            <Route path="/appointments" element={<ProtectedRoute><AppointmentsPage /></ProtectedRoute>} />
            <Route path="/appointments/:id" element={<ProtectedRoute><AppointmentDetailPage /></ProtectedRoute>} />
            <Route path="/admin/doctors" element={<ProtectedRoute roles={["admin"]}><AdminDoctorsPage /></ProtectedRoute>} />
            <Route path="/admin/doctors/new" element={<ProtectedRoute roles={["admin"]}><AdminCreateDoctorPage /></ProtectedRoute>} />
            <Route path="/admin/doctors/:id" element={<ProtectedRoute roles={["admin"]}><AdminEditDoctorPage /></ProtectedRoute>} />
            <Route path="/doctor/profile" element={<ProtectedRoute roles={["doctor"]}><DoctorProfilePage /></ProtectedRoute>} />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  );
}
