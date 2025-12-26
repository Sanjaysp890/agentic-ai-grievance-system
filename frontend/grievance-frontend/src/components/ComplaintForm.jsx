import { useState } from "react";
import { submitComplaint } from "../services/api";

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

      if (onSuccess) onSuccess(); // refresh dashboard
    } catch (err) {
      console.error("Submission failed", err);
      alert("Failed to submit complaint");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea
        placeholder="Describe your grievance in detail..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        style={{ width: "100%", padding: "10px" }}
      />

      <button
        onClick={handleSubmit}
        disabled={loading || !text.trim()}
        style={{ marginTop: "10px" }}
      >
        {loading ? "Submitting..." : "Submit Complaint"}
      </button>

      {success && (
        <p style={{ color: "green", marginTop: "10px" }}>
          ✔ Complaint submitted successfully
        </p>
      )}
    </div>
  );
}
