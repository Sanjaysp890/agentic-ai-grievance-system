import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

/* ---------------- AUTH ---------------- */

export const signup = (data) => API.post("/signup", data);

export const login = (data) => API.post("/login", data);

/* ---------------- USER ---------------- */

export const submitComplaint = (data) =>
  API.post("/submit-complaint", data);

/* ---------------- ADMIN ---------------- */

export const getAdminComplaints = (department) =>
  API.get(`/admin/complaints/${department}`);

export const respondToComplaint = (data) =>
  API.post("/admin/respond", data);
