import { useState } from "react";
import API from "../services/api";

function Signup() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "user",
    department: ""
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      const res = await API.post("/signup", form);
      alert("Signup successful. User ID: " + res.data.user_id);
    } catch (err) {
      alert(err.response?.data?.detail || "Signup failed");
    }
  };

  return (
    <div>
      <h2>Signup</h2>

      <input name="name" placeholder="Name" onChange={handleChange} /><br/><br/>
      <input name="email" placeholder="Email" onChange={handleChange} /><br/><br/>
      <input name="password" type="password" placeholder="Password" onChange={handleChange} /><br/><br/>

      <select name="role" onChange={handleChange}>
        <option value="user">User</option>
        <option value="admin">Admin</option>
      </select><br/><br/>

      <input
        name="department"
        placeholder="Department (only for admin)"
        onChange={handleChange}
      /><br/><br/>

      <button onClick={handleSubmit}>Signup</button>
    </div>
  );
}

export default Signup;
