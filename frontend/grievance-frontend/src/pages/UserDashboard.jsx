import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  submitComplaint,
  getUserComplaints
} from "../services/api";
import { LogOut, FileText, Send, Mic, Clock, CheckCircle2, AlertCircle, Loader2, User, Calendar } from "lucide-react";

export default function UserDashboard() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const [complaint, setComplaint] = useState("");
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(false);

  /* 🔒 Route protection */
  useEffect(() => {
    if (!user) navigate("/");
  }, [user, navigate]);

  /* 📥 Load complaint history */
  const loadComplaints = async () => {
    try {
      const res = await getUserComplaints(user.user_id);
      setComplaints(res.data);
    } catch (err) {
      console.error("Failed to load complaints", err);
    }
  };

  useEffect(() => {
    loadComplaints();
  }, []);

  /* 📨 Submit complaint */
  const handleSubmit = async () => {
    if (!complaint.trim()) return;

    setLoading(true);
    try {
      await submitComplaint({
        input_type: "text",
        input_content: complaint,
        user_id: user.user_id
      });

      setComplaint("");
      loadComplaints();
    } catch (err) {
      alert("Failed to submit complaint");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  const getStatusConfig = (status) => {
    const configs = {
      PENDING: {
        color: "bg-amber-100 text-amber-700 border-amber-200",
        icon: <Clock className="w-4 h-4" />,
        label: "Pending Review"
      },
      IN_PROGRESS: {
        color: "bg-blue-100 text-blue-700 border-blue-200",
        icon: <Loader2 className="w-4 h-4 animate-spin" />,
        label: "In Progress"
      },
      RESOLVED: {
        color: "bg-green-100 text-green-700 border-green-200",
        icon: <CheckCircle2 className="w-4 h-4" />,
        label: "Resolved"
      }
    };
    return configs[status] || configs.PENDING;
  };

  const getPriorityConfig = (priority) => {
    const pr = priority ? priority.toUpperCase() : "LOW";
    const configs = {
      HIGH: { color: "bg-red-100 text-red-700 border-red-200", label: "High Priority" },
      MEDIUM: { color: "bg-orange-100 text-orange-700 border-orange-200", label: "Medium Priority" },
      LOW: { color: "bg-slate-100 text-slate-700 border-slate-200", label: "Low Priority" }
    };
    return configs[pr] || configs.LOW;
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* HEADER */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-8 py-5 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl shadow-lg">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Citizen Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome, {user.name || "User"}</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all font-medium"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-8 space-y-8">
        {/* SUBMIT COMPLAINT CARD */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Card Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Submit New Grievance</h2>
                <p className="text-blue-100 text-sm">Provide detailed information to help us assist you</p>
              </div>
            </div>
          </div>

          {/* Card Body */}
          <div className="p-8 space-y-6">
            {/* Textarea */}
            <div className="relative">
              <textarea
                rows={6}
                className="w-full px-5 py-4 bg-gray-50 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all resize-none text-gray-900 placeholder-gray-400"
                placeholder="Please describe your grievance in detail. Include relevant dates, locations, and any other important information..."
                value={complaint}
                onChange={(e) => setComplaint(e.target.value)}
              />
              <div className="absolute bottom-4 right-4 text-sm text-gray-400 font-medium">
                {complaint.length} characters
              </div>
            </div>

            {/* Character Guide */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Complaint detail level:</span>
                <span className={`font-semibold ${
                  complaint.length < 50 ? 'text-red-600' :
                  complaint.length < 100 ? 'text-orange-600' :
                  'text-green-600'
                }`}>
                  {complaint.length < 50 ? 'Add more details' :
                   complaint.length < 100 ? 'Good progress' :
                   'Excellent!'}
                </span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${
                    complaint.length < 50 ? 'bg-red-500' :
                    complaint.length < 100 ? 'bg-orange-500' :
                    'bg-green-500'
                  }`}
                  style={{ width: `${Math.min((complaint.length / 200) * 100, 100)}%` }}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <button
                className="flex items-center gap-2 px-4 py-2.5 text-blue-600 hover:bg-blue-50 rounded-xl transition-all font-medium"
                title="Audio input coming soon"
              >
                <Mic className="w-5 h-5" />
                Add Audio
              </button>

              <button
                onClick={handleSubmit}
                disabled={loading || !complaint.trim()}
                className={`flex items-center gap-3 px-6 py-3 rounded-xl font-semibold transition-all ${
                  loading || !complaint.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]'
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Submit Grievance
                  </>
                )}
              </button>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-semibold text-blue-900 mb-2">What happens next?</p>
                  <ul className="text-blue-800 space-y-1.5">
                    <li className="flex items-start gap-2">
                      <span className="text-blue-600 mt-0.5">•</span>
                      <span>Your complaint will be reviewed by the relevant department</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-600 mt-0.5">•</span>
                      <span>You'll receive updates on the status of your grievance</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-600 mt-0.5">•</span>
                      <span>Expected response time: 3-5 business days</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* COMPLAINT HISTORY */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Section Header */}
          <div className="px-8 py-6 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Grievance History</h2>
                  <p className="text-sm text-gray-600">Track all your submitted complaints</p>
                </div>
              </div>
              <div className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full font-semibold text-sm">
                {complaints.length} {complaints.length === 1 ? 'Complaint' : 'Complaints'}
              </div>
            </div>
          </div>

          {/* Complaints List */}
          <div className="p-8">
            {complaints.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                  <FileText className="w-8 h-8 text-gray-400" />
                </div>
                <p className="text-gray-600 font-medium">No complaints submitted yet</p>
                <p className="text-gray-500 text-sm mt-1">Your submitted grievances will appear here</p>
              </div>
            ) : (
              <div className="space-y-4">
                {complaints.map((c, index) => {
                  const statusConfig = getStatusConfig(c.status);
                  const priorityConfig = getPriorityConfig(c.priority);

                  return (
                    <div
                      key={c.complaint_id}
                      className="border-2 border-gray-200 rounded-xl p-6 hover:border-blue-300 hover:shadow-md transition-all bg-gradient-to-r from-white to-gray-50"
                    >
                      {/* Header Row */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 text-white font-bold rounded-lg">
                            #{index + 1}
                          </div>
                          <div>
                            <p className="font-bold text-gray-900 text-lg">Grievance #{index + 1}</p>
                            <p className="text-xs text-gray-500 flex items-center gap-1.5 mt-0.5">
                              <Calendar className="w-3 h-3" />
                              Reference ID: {c.complaint_id}
                            </p>
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${statusConfig.color}`}>
                            {statusConfig.icon}
                            {statusConfig.label}
                          </span>
                        </div>
                      </div>

                      {/* Complaint Text */}
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <p className="text-gray-700 leading-relaxed">
                          {c.english_text || c.original_input}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}