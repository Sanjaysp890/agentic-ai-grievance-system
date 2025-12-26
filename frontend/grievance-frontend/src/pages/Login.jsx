import { useState } from "react";
import { loginUser } from "../services/api";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError("");

    if (!email || !password) {
      setError("Please fill all fields");
      return;
    }

    try {
      const res = await loginUser({ email, password });
      localStorage.setItem("user", JSON.stringify(res.data));

      // Role-based redirect
      if (res.data.role === "admin") {
        navigate("/admin/dashboard");
      } else {
        navigate("/user/dashboard");
      }
    } catch (err) {
      setError("Invalid email or password");
    }
  };

  return (
    <div className="center-container">
      <div className="card auth-card">
        <h2>Public Grievance Portal</h2>
        <p className="subtitle">Login to continue</p>

        {error && <p className="error">{error}</p>}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={handleLogin}>Login</button>

        <p className="switch">
          Don’t have an account? <Link to="/signup">Sign up</Link>
        </p>
      </div>
    </div>
  );
}
