import { useEffect, useState } from "react";
import {
  getAdminComplaints,
  respondToComplaint
} from "../services/api";

export default function AdminDashboard() {
  const user = JSON.parse(localStorage.getItem("user"));

  const [complaints, setComplaints] = useState([]);
  const [activeComplaintId, setActiveComplaintId] = useState(null);
  const [responseText, setResponseText] = useState("");

  // Load complaints for this admin's department
  const loadComplaints = async () => {
    try {
      const res = await getAdminComplaints(user.department);
      setComplaints(res.data);
    } catch (err) {
      alert("Failed to load complaints");
    }
  };

  useEffect(() => {
    loadComplaints();
  }, []);

  // Submit response
  const submitResponse = async (complaintId) => {
    if (!responseText.trim()) {
      alert("Response cannot be empty");
      return;
    }

    try {
      await respondToComplaint({
        complaint_id: complaintId,
        department: user.department,
        response: responseText
      });

      alert("Response submitted successfully");
      setActiveComplaintId(null);
      setResponseText("");
      loadComplaints();
    } catch (err) {
      alert("Failed to submit response");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h2>{user.department} Admin Dashboard</h2>

      <table
        border="1"
        cellPadding="10"
        style={{
          marginTop: "20px",
          borderCollapse: "collapse",
          width: "100%"
        }}
      >
        <thead>
          <tr>
            <th>ID</th>
            <th>Complaint</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {complaints.length === 0 ? (
            <tr>
              <td colSpan="4">No complaints found</td>
            </tr>
          ) : (
            complaints.map((c) => (
              <tr key={c.complaint_id}>
                <td>{c.complaint_id}</td>

                {/* 👇 Complaint text shown here */}
                <td style={{ maxWidth: "400px" }}>
                  {c.english_text || c.original_input || "N/A"}
                </td>

                <td>{c.status}</td>

                <td>
                  {activeComplaintId === c.complaint_id ? (
                    <>
                      <textarea
                        rows="3"
                        cols="35"
                        placeholder="Enter response..."
                        value={responseText}
                        onChange={(e) =>
                          setResponseText(e.target.value)
                        }
                      />
                      <br />
                      <button
                        onClick={() =>
                          submitResponse(c.complaint_id)
                        }
                        style={{ marginRight: "10px" }}
                      >
                        Submit
                      </button>
                      <button
                        onClick={() => {
                          setActiveComplaintId(null);
                          setResponseText("");
                        }}
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() =>
                        setActiveComplaintId(c.complaint_id)
                      }
                    >
                      Respond
                    </button>
                  )}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
