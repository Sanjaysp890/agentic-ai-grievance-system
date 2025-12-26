import { useState } from "react";
import { submitComplaint } from "../services/api";
import { Send, FileText, CheckCircle, AlertCircle, Loader } from "lucide-react";

export default function ComplaintForm({ onSuccess }) {
  const user = JSON.parse(localStorage.getItem("user"));
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setSuccess(false);

    try {
      await submitComplaint({
        input_type: "text",
        input_content: text,
        user_id: user.user_id,
      });

      setText("");
      setSuccess(true);

      setTimeout(() => {
        setSuccess(false);
        if (onSuccess) onSuccess();
      }, 3000);
    } catch (err) {
      console.error("Submission failed", err);
      alert("Failed to submit complaint");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <style>{`
        @keyframes successPulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
        .animate-success-pulse {
          animation: successPulse 0.6s ease-in-out;
        }
      `}</style>

      {/* Form Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl">
          <FileText className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Describe Your Grievance</h3>
          <p className="text-sm text-gray-600">Provide detailed information to help us assist you better</p>
        </div>
      </div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          placeholder="Please describe your grievance in detail. Include relevant dates, locations, and any other important information..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={6}
          disabled={loading}
          className="w-full px-5 py-4 bg-white border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none text-gray-800 placeholder-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
        />
        <div className="absolute bottom-4 right-4 text-sm text-gray-400">
          {text.length} characters
        </div>
      </div>

      {/* Character Guide */}
      <div className="flex items-center gap-2 text-sm">
        <div className={`h-2 flex-1 rounded-full overflow-hidden bg-gray-200`}>
          <div
            className={`h-full transition-all duration-300 ${
              text.length < 50 ? 'bg-red-500' :
              text.length < 100 ? 'bg-yellow-500' :
              'bg-green-500'
            }`}
            style={{ width: `${Math.min((text.length / 200) * 100, 100)}%` }}
          />
        </div>
        <span className={`font-medium ${
          text.length < 50 ? 'text-red-600' :
          text.length < 100 ? 'text-yellow-600' :
          'text-green-600'
        }`}>
          {text.length < 50 ? 'Add more details' :
           text.length < 100 ? 'Good progress' :
           'Excellent!'}
        </span>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={loading || !text.trim()}
        className={`w-full py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
          loading || !text.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]'
        }`}
      >
        {loading ? (
          <>
            <Loader className="w-5 h-5 animate-spin" />
            <span>Submitting...</span>
          </>
        ) : (
          <>
            <Send className="w-5 h-5" />
            <span>Submit Complaint</span>
          </>
        )}
      </button>

      {/* Success Message */}
      {success && (
        <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl p-5 flex items-center gap-4 shadow-lg animate-success-pulse">
          <div className="p-2 bg-white/20 rounded-lg">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="font-semibold text-lg">Complaint Submitted Successfully!</p>
            <p className="text-sm text-green-50">Your grievance has been recorded and will be reviewed shortly.</p>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm">
          <p className="font-semibold text-blue-900 mb-1">What happens next?</p>
          <ul className="text-blue-800 space-y-1">
            <li>• Your complaint will be reviewed by the relevant department</li>
            <li>• You'll receive updates on the status of your grievance</li>
            <li>• Expected response time: 3-5 business days</li>
          </ul>
        </div>
      </div>
    </div>
  );
}