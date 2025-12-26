import sys
import time
from typing import TypedDict, Optional, Dict, Any, Literal, List
from langgraph.graph import StateGraph, END

# ---------------- DB IMPORTS ----------------
from ..databases.db import (
    save_complaint,
    update_complaint_classification,
    save_department_response,
    save_previous_responses,
    get_complaint_text
)

# ---------------- AGENT IMPORTS ----------------
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

    english_output: Optional[str]
    previous_responses: Optional[List[str]]
    classification: Optional[Dict[str, Any]]
    department_name: Optional[str]
    officer_response: Optional[str]

    task_mode: Optional[str]
    error: Optional[str]

# ======================================================
# WRAPPERS
# ======================================================
def intake_wrapper(state: MasterState):
    result = intake_agent.invoke(state)

    if result.get("error"):
        return {"error": result["error"]}

    user_id = state.get("metadata", {}).get("user_id")

    complaint_id = save_complaint(
        state["input_content"],
        result.get("english_output"),
        state["input_type"],
        result.get("detected_language", "en"),
        user_id
    )

    return {
        "complaint_id": complaint_id,
        "english_output": result.get("english_output"),
        "metadata": state.get("metadata", {})
    }


def learning_retrieval_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    state["task_mode"] = "retrieve"
    result = learning_agent_node(state)

    # ✅ SAVE RETRIEVED SIMILAR RESPONSES INTO POSTGRES
    previous = result.get("previous_responses", [])
    if previous and state.get("complaint_id"):
        save_previous_responses(state["complaint_id"], previous)

    return result


def classifier_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    result = classifier_node(state)
    classification = result.get("classification")

    if not classification:
        return {"error": "Classifier returned no classification"}

    departments = classification.get("departments", [])
    priority = classification.get("urgency_score")

    if not departments or priority is None:
        return {"error": "Classifier output incomplete"}

    primary = departments[0].lower()

    if "water" in primary:
        final_department = "WaterBoard"
    elif "electric" in primary:
        final_department = "Electricity"
    elif "police" in primary or "crime" in primary:
        final_department = "Police"
    else:
        final_department = "General"

    update_complaint_classification(
        state["complaint_id"],
        final_department,
        priority
    )

    return {
        "classification": classification,
        "department_name": final_department
    }

# ======================================================
# ROUTING LOGIC
# ======================================================
def route_complaint(state: MasterState) -> Literal["water", "police", "electric", "general"]:
    classification = state.get("classification", {})
    depts = classification.get("departments", [])

    if not depts:
        return "general"

    text = " ".join(d.lower() for d in depts)

    if "water" in text:
        return "water"
    if "electric" in text or "power" in text:
        return "electric"
    if "police" in text or "crime" in text:
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
    return app.invoke({
        "input_type": input_type,
        "input_content": input_content,
        "metadata": {
            "source": "frontend",
            "user_id": user_id
        }
    })


def submit_department_response_api(complaint_id: int, department: str, response: str):
    # 1️⃣ Save admin response to PostgreSQL
    save_department_response(complaint_id, department, response)

    # 2️⃣ Fetch complaint text
    complaint_text = get_complaint_text(complaint_id)

    # 3️⃣ Ingest complaint + response into ChromaDB
    if complaint_text:
        learning_agent_node({
            "task_mode": "ingest",
            "english_output": complaint_text,
            "officer_response": response
        })

    # 4️⃣ Escalation logic
    escalation_agent_node({
        "complaint_id": complaint_id,
        "officer_response": response
    })

    return {"status": "success"}
