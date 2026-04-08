from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from backend.agents.escalation_agent import run_escalation_check

scheduler = BackgroundScheduler()
scheduler.add_job(run_escalation_check, 'interval', hours=1)
scheduler.start()

# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------
app = FastAPI(title="Public Grievance Redressal AI System")

@app.get("/favicon.ico")
async def favicon():
    return {}

# --------------------------------------------------
# ✅ CORS (REQUIRED FOR FRONTEND)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# DATABASE IMPORTS (SAFE AT STARTUP)
# --------------------------------------------------
from backend.databases.db import (
    create_user,
    validate_login,
    get_complaints_by_department,
    get_complaint_department,
    get_complaints_by_user
)

# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"        # user | admin
    department: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class ComplaintRequest(BaseModel):
    input_type: str          # "text" | "audio"
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
# USER: SUBMIT COMPLAINT
# --------------------------------------------------
@app.post("/submit-complaint")
def submit_complaint(req: ComplaintRequest):
    # 🔑 LAZY IMPORT (CRITICAL FOR WINDOWS)
    from backend.agents.main import submit_complaint_api

    result = submit_complaint_api(
        req.input_type,
        req.input_content,
        req.user_id
    )

    if result is None or result == "__end__":
        return {"status": "PENDING"}

    return {
        "complaint_id": result.get("complaint_id"),
        "department_name": result.get("department_name"),
        "classification": result.get("classification"),
        # learning agent output (already computed internally)
        "previous_responses": result.get("previous_responses", []),
        "status": "PENDING"
    }


# --------------------------------------------------
# ✅ USER: COMPLAINT HISTORY
# --------------------------------------------------
@app.get("/user/complaints/{user_id}")
def user_complaints(user_id: int):
    """
    Returns stored complaint history:
    - complaint text
    - status
    - priority
    - admin_response (official)
    - previous_responses (reference-only, if stored)
    """
    try:
        return get_complaints_by_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------
# ADMIN: VIEW COMPLAINTS (DEPARTMENT RESTRICTED)
# --------------------------------------------------
@app.get("/admin/complaints/{department}")
def get_admin_complaints(department: str):
    try:
        return get_complaints_by_department(department)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------
# ADMIN: RESPOND TO COMPLAINT (DEPT RESTRICTED)
# --------------------------------------------------
@app.post("/admin/respond")
def admin_respond(req: AdminResponseRequest):
    # 🔑 LAZY IMPORT (CRITICAL FOR WINDOWS)
    from backend.agents.main import submit_department_response_api

    try:
        complaint_dept = get_complaint_department(req.complaint_id)

        if not complaint_dept:
            raise HTTPException(status_code=404, detail="Complaint not found")

        if complaint_dept != req.department:
            raise HTTPException(
                status_code=403,
                detail="Admin cannot respond to complaints outside their department"
            )

        result = submit_department_response_api(
            req.complaint_id,
            req.department,
            req.response
        )

        return {
            "status": "RESOLVED",
            "message": "Response submitted successfully",
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
