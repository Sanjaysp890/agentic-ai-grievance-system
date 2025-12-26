import { Routes, Route, Navigate } from "react-router-dom";

import Auth from "./pages/Auth";
import UserDashboard from "./pages/UserDashboard";
import AdminDashboard from "./pages/AdminDashboard";

export default function App() {
  return (
    <Routes>
      {/* Default → Auth */}
      <Route path="/" element={<Navigate to="/auth" />} />

      {/* Auth (Login + Signup for users) */}
      <Route path="/auth" element={<Auth />} />

      {/* Dashboards */}
      <Route path="/user/dashboard" element={<UserDashboard />} />
      <Route path="/admin/dashboard" element={<AdminDashboard />} />

      {/* Fallback */}
      <Route path="*" element={<h2>Page Not Found</h2>} />
    </Routes>
  );
}
