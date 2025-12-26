import sys
import time
from typing import TypedDict, Optional, Dict, Any, Literal, List
from langgraph.graph import StateGraph, END

# ---------------- DB IMPORTS ----------------
from ..databases.db import (
    save_complaint,
    update_complaint_classification,
    save_department_response
)
# -------------------------------------------

try:
    from .intake_agent import intake_agent
    from .classifier_agent import classifier_node
    from .department_nodes import (
        water_dept_node,
        police_dept_node,
        electricity_dept_node,
        general_dept_node
    )
    from .escalation_agent import escalation_agent_node
    from .learning_agent import learning_agent_node
except ImportError as e:
    print(f"System Error: Failed to import required agent modules. {e}")
    sys.exit(1)

# ======================================================
# MASTER STATE
# ======================================================
class MasterState(TypedDict):
    input_type: str
    input_content: str
    metadata: Dict[str, Any]

    complaint_id: Optional[int]

    detected_language: Optional[str]
    original_transcript: Optional[str]
    english_output: Optional[str]

    previous_responses: Optional[List[str]]
    classification: Optional[Dict[str, Any]]

    department_name: Optional[str]
    officer_response: Optional[str]
    response_timestamp: Optional[float]

    escalation_status: Optional[str]
    escalation_reason: Optional[str]

    learning_ingestion_status: Optional[str]
    task_mode: Optional[str]
    error: Optional[str]

# ======================================================
# WRAPPERS
# ======================================================
def intake_wrapper(state: MasterState):
    result = intake_agent.invoke(state)

    if result.get("error"):
        return {"error": result["error"]}

    # ✅ FIX: extract user_id from metadata
    user_id = state.get("metadata", {}).get("user_id")

    complaint_id = save_complaint(
        state["input_content"],
        result.get("english_output"),
        state["input_type"],
        result.get("detected_language", "en"),
        user_id                     # ✅ PASS USER ID
    )

    return {
        "complaint_id": complaint_id,
        "english_output": result.get("english_output"),
        "original_transcript": result.get("original_transcript"),
        "detected_language": result.get("detected_language"),
        "metadata": {**state.get("metadata", {}), "intake_time": time.time()}
    }


def learning_retrieval_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    state["task_mode"] = "retrieve"
    return learning_agent_node(state)


def classifier_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    result = classifier_node(state)

    if result.get("error"):
        return {"error": result["error"]}

    classification = result.get("classification")

    if not classification:
        return {"error": "Classifier returned no classification"}

    departments = classification.get("departments")
    priority = classification.get("urgency_score")

    if not departments or priority is None:
        return {"error": "Classifier output missing departments or urgency_score"}

    # ✅ DETERMINE FINAL ROUTED DEPARTMENT
    primary = departments[0].lower()

    if "water" in primary:
        final_department = "WaterBoard"
    elif "health" in primary:
        final_department = "Health"
    elif "electric" in primary:
        final_department = "Electricity"
    elif "police" in primary or "crime" in primary:
        final_department = "Police"
    else:
        final_department = "General"

    # ✅ SAVE ROUTED DEPARTMENT + PRIORITY
    update_complaint_classification(
        state["complaint_id"],
        final_department,
        priority
    )

    return {
        "classification": classification,
        "department_name": final_department
    }


def escalation_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    return escalation_agent_node(state)

# ======================================================
# ROUTING LOGIC
# ======================================================
def route_complaint(state: MasterState) -> Literal["water", "police", "electric", "general"]:
    if state.get("error"):
        return "general"

    classification = state.get("classification", {})
    depts = classification.get("departments", [])

    if not depts:
        return "general"

    dept_text = " ".join(d.lower() for d in depts)

    if "water" in dept_text:
        return "water"
    if "electric" in dept_text or "power" in dept_text:
        return "electric"
    if "police" in dept_text or "crime" in dept_text:
        return "police"

    return "general"

# ======================================================
# LANGGRAPH WORKFLOW
# ======================================================
workflow = StateGraph(MasterState)

workflow.add_node("intake", intake_wrapper)
workflow.add_node("learning_retrieval", learning_retrieval_wrapper)
workflow.add_node("classifier", classifier_wrapper)

workflow.add_node("water_node", water_dept_node)
workflow.add_node("police_node", police_dept_node)
workflow.add_node("electric_node", electricity_dept_node)
workflow.add_node("general_node", general_dept_node)

workflow.set_entry_point("intake")

workflow.add_edge("intake", "learning_retrieval")
workflow.add_edge("learning_retrieval", "classifier")

workflow.add_conditional_edges(
    "classifier",
    route_complaint,
    {
        "water": "water_node",
        "police": "police_node",
        "electric": "electric_node",
        "general": "general_node"
    }
)

for node in ["water_node", "police_node", "electric_node", "general_node"]:
    workflow.add_edge(node, END)

app = workflow.compile()

# ======================================================
# API-CALLABLE FUNCTIONS
# ======================================================
def submit_complaint_api(input_type: str, input_content: str, user_id: int):
    state = {
        "input_type": input_type,
        "input_content": input_content,
        "metadata": {
            "source": "frontend",
            "user_id": user_id     # ✅ USER ID ENTERS SYSTEM HERE
        }
    }
    return app.invoke(state)


def submit_department_response_api(complaint_id: int, department: str, response: str):
    save_department_response(complaint_id, department, response)

    state = {
        "complaint_id": complaint_id,
        "officer_response": response,
        "metadata": {
            "intake_time": time.time()
        }
    }

    learning_agent_node({
        **state,
        "task_mode": "ingest",
        "english_output": None
    })

    escalation_agent_node(state)

    return {"status": "success"}
