import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  getAdminComplaints,
  respondToComplaint
} from "../services/api";
import {
  LogOut,
  MessageSquare,
  FileText,
  Clock,
  TrendingUp,
  CheckCircle,
  AlertTriangle,
  ChevronLeft,
  ChevronRight
} from "lucide-react";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));
  const priorityRef = useRef(null);

  const [complaints, setComplaints] = useState([]);
  const [activeComplaintId, setActiveComplaintId] = useState(null);
  const [responseText, setResponseText] = useState("");
  const [loading, setLoading] = useState(false);
  const [successId, setSuccessId] = useState(null);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!user) navigate("/");
  }, [user, navigate]);

  const loadComplaints = async () => {
    const res = await getAdminComplaints(user.department);
    setComplaints(res.data);
  };

  useEffect(() => {
    loadComplaints();
  }, []);

  const submitResponse = async (complaintId) => {
    if (!responseText.trim()) return;
    setLoading(true);

    await respondToComplaint({
      complaint_id: complaintId,
      department: user.department,
      response: responseText
    });

    setLoading(false);
    setActiveComplaintId(null);
    setResponseText("");
    setSuccessId(complaintId);
    loadComplaints();
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  /* ---------- PRIORITY HELPERS ---------- */

  const normalizePriority = (p, classification) => {
    if (p) return p.toUpperCase();
    if (classification?.urgency_score) return classification.urgency_score.toUpperCase();
    return "LOW";
  };

  const priorityRank = { HIGH: 1, MEDIUM: 2, LOW: 3 };

  const filteredComplaints = complaints
    .filter((c) => {
      const statusOk =
        statusFilter === "ALL" || c.status === statusFilter;

      const priorityOk =
        priorityFilter === "ALL" ||
        normalizePriority(c.priority, c.classification) === priorityFilter;

      const textOk = (c.english_text || c.original_input || "")
        .toLowerCase()
        .includes(search.toLowerCase());

      return statusOk && priorityOk && textOk;
    })
    .sort(
      (a, b) =>
        priorityRank[normalizePriority(a.priority, a.classification)] -
        priorityRank[normalizePriority(b.priority, b.classification)]
    );

  const statusBadge = (s) =>
    s === "PENDING"
      ? "bg-yellow-100 text-yellow-700"
      : s === "IN_PROGRESS"
      ? "bg-blue-100 text-blue-700"
      : s === "ESCALATED"
      ? "bg-red-100 text-red-700"
      : "bg-green-100 text-green-700";

  const priorityBadge = (p, classification) => {
    const pr = normalizePriority(p, classification);
    if (pr === "HIGH") return "bg-red-100 text-red-700";
    if (pr === "MEDIUM") return "bg-amber-100 text-amber-700";
    return "bg-green-100 text-green-700";
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-100">
      {/* HEADER */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-10 py-6 flex justify-between items-center shadow">
        <div>
          <h1 className="text-3xl font-bold">
            {user.department} Dashboard
          </h1>
          <p className="text-sm opacity-90">Admin Control Panel</p>
        </div>

        <button
          onClick={handleLogout}
          className="bg-white/10 hover:bg-white/20 p-2 rounded-lg"
        >
          <LogOut />
        </button>
      </div>

      {/* STATS */}
      <div className="max-w-7xl mx-auto grid grid-cols-5 gap-6 px-8 mt-8">
        <Stat icon={<FileText />} label="Total" value={complaints.length}
          bg="bg-purple-100" color="text-purple-600" />
        <Stat icon={<Clock />} label="Pending"
          value={complaints.filter(c => c.status === "PENDING").length}
          bg="bg-amber-100" color="text-amber-600" />
        <Stat icon={<TrendingUp />} label="In Progress"
          value={complaints.filter(c => c.status === "IN_PROGRESS").length}
          bg="bg-blue-100" color="text-blue-600" />
        <Stat icon={<CheckCircle />} label="Resolved"
          value={complaints.filter(c => c.status === "RESOLVED").length}
          bg="bg-green-100" color="text-green-600" />
        <Stat icon={<AlertTriangle />} label="Escalated"
          value={complaints.filter(c => c.status === "ESCALATED").length}
          bg="bg-red-100" color="text-red-600" />
      </div>

      {/* SEARCH + FILTERS */}
      <div className="max-w-7xl mx-auto px-8 mt-8 space-y-4">
        <input
          className="w-full border rounded-lg px-4 py-2"
          placeholder="Search complaints..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {/* STATUS FILTER */}
        <div className="flex gap-2 flex-wrap">
          {["ALL", "PENDING", "IN_PROGRESS", "RESOLVED", "ESCALATED"].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-4 py-2 rounded-lg text-sm ${
                statusFilter === s
                  ? "bg-blue-600 text-white"
                  : "bg-white border"
              }`}
            >
              {s.replace("_", " ")}
            </button>
          ))}
        </div>

        {/* PRIORITY FILTER WITH SCROLL */}
        <div className="flex items-center gap-2">
          <button
            onClick={() =>
              priorityRef.current.scrollBy({ left: -150, behavior: "smooth" })
            }
            className="p-2 bg-white border rounded-full"
          >
            <ChevronLeft size={16} />
          </button>

          <div
            ref={priorityRef}
            className="flex gap-2 overflow-x-auto"
          >
            {["ALL", "HIGH", "MEDIUM", "LOW"].map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-4 py-2 rounded-full text-sm whitespace-nowrap ${
                  priorityFilter === p
                    ? "bg-indigo-600 text-white"
                    : "bg-white border"
                }`}
              >
                {p}
              </button>
            ))}
          </div>

          <button
            onClick={() =>
              priorityRef.current.scrollBy({ left: 150, behavior: "smooth" })
            }
            className="p-2 bg-white border rounded-full"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* TABLE */}
      <div className="max-w-7xl mx-auto px-8 mt-6">
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-50 text-sm text-gray-600">
              <tr>
                <th className="p-4 text-left">ID</th>
                <th className="p-4 text-left">Complaint</th>
                <th className="p-4 text-center">Priority</th>
                <th className="p-4 text-center">Status</th>
                <th className="p-4 text-center">Action</th>
              </tr>
            </thead>

            <tbody>
              {filteredComplaints.map((c) => (
                <tr key={c.complaint_id} className="border-t align-top">
                  <td className="p-4 font-semibold">#{c.complaint_id}</td>

                  <td className="p-4 w-1/2">
                    {c.english_text || c.original_input}
                  </td>

                  <td className="p-4 text-center">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${priorityBadge(c.priority, c.classification)}`}>
                      {normalizePriority(c.priority, c.classification)}
                    </span>
                  </td>

                  <td className="p-4 text-center">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusBadge(c.status)}`}>
                      {c.status}
                    </span>
                  </td>

                  <td className="p-4 text-center">
                    {activeComplaintId === c.complaint_id ? (
                      <div className="space-y-2">
                        {/* TOP BUTTONS */}
                        <div className="flex justify-center gap-2">
                          <button
                            onClick={() => submitResponse(c.complaint_id)}
                            disabled={loading}
                            className="bg-blue-600 text-white px-3 py-1 rounded-lg text-sm"
                          >
                            {loading ? "Submitting..." : "Submit"}
                          </button>
                          <button
                            onClick={() => {
                              setActiveComplaintId(null);
                              setResponseText("");
                            }}
                            className="bg-gray-200 px-3 py-1 rounded-lg text-sm"
                          >
                            Cancel
                          </button>
                        </div>

                        <textarea
                          rows={3}
                          className="w-full border rounded-lg p-2 text-sm"
                          placeholder="Enter response..."
                          value={responseText}
                          onChange={(e) => setResponseText(e.target.value)}
                        />
                      </div>
                    ) : (
                      <button
                        onClick={() => setActiveComplaintId(c.complaint_id)}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg inline-flex items-center gap-2"
                      >
                        <MessageSquare size={16} /> Respond
                      </button>
                    )}

                    {successId === c.complaint_id && (
                      <div className="text-green-600 text-xs mt-1">
                        ✔ Response submitted
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Stat({ icon, label, value, bg, color }) {
  return (
    <div className="bg-white rounded-xl p-6 flex items-center gap-4 shadow hover:shadow-xl transition">
      <div className={`p-3 rounded-xl ${bg} ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </div>
  );
}