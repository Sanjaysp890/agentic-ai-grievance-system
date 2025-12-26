import sys
from typing import TypedDict, Optional, Dict, Any, Literal, List
from langgraph.graph import StateGraph, END

# -------------------------------
# Imports (Package-safe)
# -------------------------------
try:
    from .intake_agent import intake_agent
    from .classifier_agent import classifier_node
    from .departments import (
        water_dept_node,
        police_dept_node,
        electricity_dept_node
    )
    from .escalation_agent import escalation_agent_node
    from .learning_agent import learning_agent_node
except ImportError as e:
    print(f"System Error: Failed to import required modules. {e}")
    sys.exit(1)

# -------------------------------
# Master State Definition
# -------------------------------
class MasterState(TypedDict):
    # Input
    input_type: str
    input_content: str
    metadata: Dict[str, Any]

    # Intake outputs
    detected_language: Optional[str]
    original_transcript: Optional[str]
    english_output: Optional[str]

    # Classification output
    classification: Optional[Dict[str, Any]]

    # Department output
    department_name: Optional[str]
    officer_response: Optional[str]

    # Escalation output
    escalated: Optional[bool]
    escalation_reason: Optional[str]

    # Learning output
    previous_responses: Optional[List[str]]
    learning_agent_status: Optional[str]

    # Error handling
    error: Optional[str]

# -------------------------------
# Wrapper Nodes
# -------------------------------
def intake_wrapper(state: MasterState):
    print("[System] Initializing Intake Agent...")
    result = intake_agent.invoke(state)

    if result.get("error"):
        return {"error": result["error"]}

    return {
        "english_output": result.get("english_output"),
        "original_transcript": result.get("original_transcript"),
        "detected_language": result.get("detected_language")
    }

def classifier_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    print("[System] Analyzing Content and Determining Routing...")
    return classifier_node(state)

# -------------------------------
# Routing Logic
# -------------------------------
def route_complaint(state: MasterState) -> Literal["water", "police", "electric"]:
    if state.get("error"):
        return END

    classification = state.get("classification", {})
    departments = classification.get("departments", [])

    if not departments:
        return "police"  # default fallback
    
    primary = departments[0].lower()

    if "water" in primary:
        return "water"
    elif any(x in primary for x in ["police", "crime", "theft"]):
        return "police"
    elif any(x in primary for x in ["electric", "power", "energy"]):
        return "electric"
    else:
        return "police"

# -------------------------------
# LangGraph Workflow
# -------------------------------
workflow = StateGraph(MasterState)

# Core nodes
workflow.add_node("intake", intake_wrapper)
workflow.add_node("classifier", classifier_wrapper)

# Department nodes
workflow.add_node("water_node", water_dept_node)
workflow.add_node("police_node", police_dept_node)
workflow.add_node("electric_node", electricity_dept_node)

# Post-processing agents
workflow.add_node("escalation", escalation_agent_node)
workflow.add_node("learning", learning_agent_node)

# Entry
workflow.set_entry_point("intake")

# Flow
workflow.add_edge("intake", "classifier")

workflow.add_conditional_edges(
    "classifier",
    route_complaint,
    {
        "water": "water_node",
        "police": "police_node",
        "electric": "electric_node"
    }
)

# Department → Escalation → Learning → END
for dept in ["water_node", "police_node", "electric_node"]:
    workflow.add_edge(dept, "escalation")

workflow.add_edge("escalation", "learning")
workflow.add_edge("learning", END)

# Compile app
app = workflow.compile()

# -------------------------------
# Execution Entry Point
# -------------------------------
if __name__ == "__main__":
    user_input = {
        "input_type": "text",
        "input_content": "Water supply is contaminated and smells bad.",
        "metadata": {"source": "cli_test"}
    }

    print("\n--- Starting Grievance Redressal Workflow ---")
    print(f"[Input] {user_input['input_content']}")

    try:
        final_state = app.invoke(user_input)

        if final_state.get("error"):
            print(f"[Error] {final_state['error']}")
        else:
            print("\n--- Workflow Completed ---")
            print(f"Department Response: {final_state.get('officer_response')}")
            
            if final_state.get("previous_responses"):
                print("\nPrevious Similar Responses:")
                for idx, resp in enumerate(final_state["previous_responses"], 1):
                    print(f"{idx}. {resp}")

            if final_state.get("escalated"):
                print(f"\n⚠ Escalated: {final_state.get('escalation_reason')}")

    except Exception as e:
        print(f"[Critical Error] {e}")
