import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser, signupUser } from "../services/api";

export default function Auth() {
  const navigate = useNavigate();

  // login | signup
  const [mode, setMode] = useState("login");
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: ""
  });

  const handleSubmit = async () => {
    setError("");

    if (!form.email || !form.password || (mode === "signup" && !form.name)) {
      setError("Please fill all required fields");
      return;
    }

    try {
      if (mode === "login") {
        // LOGIN (user + admin)
        const res = await loginUser({
          email: form.email,
          password: form.password
        });

        localStorage.setItem("user", JSON.stringify(res.data));

        // Role-based redirect
        if (res.data.role === "admin") {
          navigate("/admin/dashboard");
        } else {
          navigate("/user/dashboard");
        }
      } else {
        // SIGNUP (USER ONLY)
        await signupUser({
          name: form.name,
          email: form.email,
          password: form.password,
          role: "user"
        });

        // After signup → switch to login
        setMode("login");
      }
    } catch (err) {
      setError("Authentication failed. Please try again.");
    }
  };

  return (
    <div className="center-container">
      <div className="card auth-card">
        <h2>Public Grievance Portal</h2>

        {/* Tabs */}
        <div className="tabs">
          <button
            className={mode === "login" ? "active" : ""}
            onClick={() => setMode("login")}
          >
            Login
          </button>
          <button
            className={mode === "signup" ? "active" : ""}
            onClick={() => setMode("signup")}
          >
            Sign Up
          </button>
        </div>

        {error && <p className="error">{error}</p>}

        {/* Signup-only */}
        {mode === "signup" && (
          <input
            placeholder="Full Name"
            value={form.name}
            onChange={(e) =>
              setForm({ ...form, name: e.target.value })
            }
          />
        )}

        <input
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={(e) =>
            setForm({ ...form, email: e.target.value })
          }
        />

        <input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={(e) =>
            setForm({ ...form, password: e.target.value })
          }
        />

        <button onClick={handleSubmit}>
          {mode === "login" ? "Login" : "Create Account"}
        </button>

        {mode === "signup" && (
          <p style={{ marginTop: "10px", fontSize: "13px", color: "#6b7280" }}>
            * Admin accounts are created by the system
          </p>
        )}
      </div>
    </div>
  );
}
