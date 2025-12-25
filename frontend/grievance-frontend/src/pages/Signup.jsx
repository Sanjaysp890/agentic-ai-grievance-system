import { useState } from "react";
import { signup } from "../services/api";

export default function Signup() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const handleSubmit = async () => {
    await signup({
      ...form,
      role: "user",
      department: null,
    });
    alert("Signup successful. Please login.");
  };

  return (
    <div className="container">
      <h2>User Signup</h2>
      <input placeholder="Name" onChange={e => setForm({...form, name: e.target.value})} />
      <input placeholder="Email" onChange={e => setForm({...form, email: e.target.value})} />
      <input type="password" placeholder="Password" onChange={e => setForm({...form, password: e.target.value})} />
      <button onClick={handleSubmit}>Signup</button>
    </div>
  );
}
