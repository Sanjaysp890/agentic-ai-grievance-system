import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json"
  }
});

/* ---------------- AUTH ---------------- */

export const signupUser = (data) => API.post("/signup", data);

export const loginUser = (data) => API.post("/login", data);

/* ---------------- USER ---------------- */

export const submitComplaint = (data) =>
  API.post("/submit-complaint", data);

export const getUserComplaints = (userId) =>
  API.get(`/user/complaints/${userId}`);

/* ---------------- ADMIN ---------------- */

export const getAdminComplaints = (department) =>
  API.get(`/admin/complaints/${department}`);

export const respondToComplaint = (data) =>
  API.post("/admin/respond", data);
