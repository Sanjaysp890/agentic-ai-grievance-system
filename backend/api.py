from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------
app = FastAPI(title="Public Grievance Redressal AI System")

# --------------------------------------------------
# IMPORT BACKEND LOGIC
# --------------------------------------------------
from backend.agents.main import (
    submit_complaint_api,
    submit_department_response_api
)

from backend.databases.db import (
    create_user,
    validate_login
)

# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"
    department: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class ComplaintRequest(BaseModel):
    input_type: str      # "text" | "audio"
    input_content: str
    user_id: int


class AdminResponseRequest(BaseModel):
    complaint_id: int
    department: str
    response: str


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/")
def health():
    return {"status": "Backend running successfully"}


# --------------------------------------------------
# AUTH APIs
# --------------------------------------------------
@app.post("/signup")
def signup(req: SignupRequest):
    try:
        user_id = create_user(
            req.name,
            req.email,
            req.password,
            req.role,
            req.department
        )
        return {"status": "success", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
def login(req: LoginRequest):
    user = validate_login(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


# --------------------------------------------------
# USER FLOW  ✅ (NO TRY/EXCEPT — FIXES __end__)
# --------------------------------------------------
@app.post("/submit-complaint")
def submit_complaint(req: ComplaintRequest):
    result = submit_complaint_api(
        req.input_type,
        req.input_content,
        req.user_id
    )

    # ✅ LangGraph END = SUCCESS
    if result == "__end__" or result is None:
        return {
            "status": "submitted"
        }

    # ✅ Return ONLY JSON-safe fields
    return {
        "complaint_id": result.get("complaint_id"),
        "department_name": result.get("department_name"),
        "classification": result.get("classification"),
        "previous_responses": result.get("previous_responses", []),
        "status": "submitted"
    }


# --------------------------------------------------
# ADMIN FLOW
# --------------------------------------------------
@app.post("/admin/respond")
def admin_respond(req: AdminResponseRequest):
    try:
        result = submit_department_response_api(
            req.complaint_id,
            req.department,
            req.response
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
