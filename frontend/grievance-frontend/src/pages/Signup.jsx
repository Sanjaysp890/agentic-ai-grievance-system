import { useState } from "react";
import { signupUser } from "../services/api";
import { useNavigate, Link } from "react-router-dom";

export default function Signup() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "user",
    department: ""
  });

  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSignup = async () => {
    setError("");

    if (!form.name || !form.email || !form.password) {
      setError("Please fill all required fields");
      return;
    }

    try {
      await signupUser(form);
      navigate("/login");
    } catch (err) {
      setError("Signup failed. Try again.");
    }
  };

  return (
    <div className="center-container">
      <div className="card auth-card">
        <h2>Create Account</h2>
        <p className="subtitle">Public Grievance Portal</p>

        {error && <p className="error">{error}</p>}

        <input
          placeholder="Full Name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />

        <input
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />

        <input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />

        <select
          value={form.role}
          onChange={(e) =>
            setForm({ ...form, role: e.target.value })
          }
        >
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>

        {form.role === "admin" && (
          <input
            placeholder="Department (e.g. WaterBoard)"
            value={form.department}
            onChange={(e) =>
              setForm({ ...form, department: e.target.value })
            }
          />
        )}

        <button onClick={handleSignup}>Sign Up</button>

        <p className="switch">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
