import { useState } from "react";
import { submitComplaint } from "../services/api";

export default function ComplaintForm() {
  const user = JSON.parse(localStorage.getItem("user"));
  const [text, setText] = useState("");

  const handleSubmit = async () => {
    await submitComplaint({
      input_type: "text",
      input_content: text,
      user_id: user.user_id,
    });
    alert("Complaint submitted successfully");
    setText("");
  };

  return (
    <div>
      <textarea
        placeholder="Describe your grievance..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
      />
      <br />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}
