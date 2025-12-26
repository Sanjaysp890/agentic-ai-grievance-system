import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  submitComplaint,
  getUserComplaints
} from "../services/api";
import {
  LogOut,
  FileText,
  Send,
  Mic,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  User,
  Calendar,
  BookOpen
} from "lucide-react";

export default function UserDashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const [complaint, setComplaint] = useState("");
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) navigate("/");
  }, [user, navigate]);

  const loadComplaints = async () => {
    const res = await getUserComplaints(user.user_id);
    setComplaints(res.data);
  };

  useEffect(() => {
    loadComplaints();
  }, []);

  const handleSubmit = async () => {
    if (!complaint.trim()) return;
    setLoading(true);

    await submitComplaint({
      input_type: "text",
      input_content: complaint,
      user_id: user.user_id
    });

    setComplaint("");
    loadComplaints();
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  const statusConfig = (status) => ({
    PENDING: "bg-amber-100 text-amber-700",
    IN_PROGRESS: "bg-blue-100 text-blue-700",
    RESOLVED: "bg-green-100 text-green-700"
  }[status]);

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-100">
      {/* HEADER */}
      <div className="bg-white shadow border-b sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-8 py-4 flex justify-between">
          <div className="flex gap-3 items-center">
            <div className="p-3 bg-blue-600 rounded-xl">
              <User className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Citizen Dashboard</h1>
              <p className="text-sm text-gray-500">{user.name}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-gray-100 px-4 py-2 rounded-lg"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-8 space-y-8">
        {/* SUBMIT */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="font-semibold mb-3">Submit New Grievance</h2>

          <textarea
            rows={5}
            value={complaint}
            onChange={(e) => setComplaint(e.target.value)}
            className="w-full border rounded-lg p-4"
            placeholder="Describe your grievance..."
          />

          <div className="flex justify-between mt-4">
            <button className="flex gap-2 text-blue-600">
              <Mic /> Add Audio
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg"
            >
              {loading ? "Submitting..." : "Submit"}
            </button>
          </div>
        </div>

        {/* HISTORY */}
        <div className="bg-white rounded-xl shadow">
          <div className="border-b px-6 py-4 font-semibold">
            Grievance History
          </div>

          <div className="p-6 space-y-6">
            {complaints.map((c, index) => (
              <div
                key={c.complaint_id}
                className="border rounded-xl p-5 bg-slate-50"
              >
                {/* HEADER */}
                <div className="flex justify-between mb-3">
                  <div>
                    <p className="font-semibold">
                      Grievance #{index + 1}
                    </p>
                    <p className="text-xs text-gray-500 flex gap-1">
                      <Calendar size={12} /> ID: {c.complaint_id}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${statusConfig(
                      c.status
                    )}`}
                  >
                    {c.status}
                  </span>
                </div>

                {/* COMPLAINT */}
                <p className="text-gray-700 mb-4">
                  {c.english_text || c.original_input}
                </p>

                {/* ✅ ADMIN RESPONSE */}
                {c.admin_response && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-3">
                    <h4 className="font-semibold text-green-800 mb-1">
                      Official Department Response
                    </h4>
                    <p className="text-green-700">
                      {c.admin_response}
                    </p>
                  </div>
                )}

                {/* 📚 PREVIOUS SIMILAR CASES */}
                {c.previous_responses &&
                  c.previous_responses.length > 0 && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-800 mb-2 flex gap-2 items-center">
                        <BookOpen size={16} />
                        Past Similar Resolutions (Reference)
                      </h4>
                      <ul className="list-disc list-inside text-blue-700 text-sm space-y-1">
                        {c.previous_responses.map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
