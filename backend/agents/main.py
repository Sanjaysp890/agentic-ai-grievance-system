import sys
from typing import TypedDict, Optional, Dict, Any, Literal
from langgraph.graph import StateGraph, END

# Conditional Imports
try:
    from intake_agent import intake_agent
    from classifier_agent import classifier_node
    from departments import (
        water_dept_node, 
        police_dept_node, 
        electricity_dept_node, 
        general_dept_node
    )
except ImportError as e:
    print(f"System Error: Failed to import required modules. {e}")
    sys.exit(1)

# --- State Definition ---
class MasterState(TypedDict):
    # Input Data
    input_type: str
    input_content: str
    metadata: Dict[str, Any]

    # Agent Outputs
    detected_language: Optional[str]
    original_transcript: Optional[str]
    english_output: Optional[str]
    classification: Optional[Dict[str, Any]]
    
    # Department Outputs
    department_name: Optional[str]
    officer_response: Optional[str]
    
    # System Status
    error: Optional[str]

# --- Workflow Wrappers ---

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

# --- Routing Logic ---

def route_complaint(state: MasterState) -> Literal["water", "police", "electric", "general"]:
    """
    Determines the next node based on classification tags.
    Returns the key of the target node.
    """
    if state.get("error"):
        return END

    classification = state.get("classification", {})
    depts = classification.get("departments", [])
    
    if not depts:
        return "general"
        
    # Normalize input for routing comparison
    primary_dept = depts[0].lower()
    
    if "water" in primary_dept:
        return "water"
    elif any(x in primary_dept for x in ["police", "crime", "theft"]):
        return "police"
    elif any(x in primary_dept for x in ["electric", "power", "energy"]):
        return "electric"
    else:
        return "general"

# --- Graph Construction ---

workflow = StateGraph(MasterState)

# Add Nodes
workflow.add_node("intake", intake_wrapper)
workflow.add_node("classifier", classifier_wrapper)
workflow.add_node("water_node", water_dept_node)
workflow.add_node("police_node", police_dept_node)
workflow.add_node("electric_node", electricity_dept_node)
workflow.add_node("general_node", general_dept_node)

# Define Logic Flow
workflow.set_entry_point("intake")
workflow.add_edge("intake", "classifier")

# Conditional Edges
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

# Termination Edges
for node in ["water_node", "police_node", "electric_node", "general_node"]:
    workflow.add_edge(node, END)

# Compile Application
app = workflow.compile()

# --- Execution Entry Point ---

if __name__ == "__main__":
    # Test Payload
    user_input = {
        "input_type": "text",
        "input_content": "Someone stole my bike from M.G. Road!",
        "metadata": {"source": "api_v1"}
    }
    
    print(f"--- Starting Grievance Redressal Workflow ---")
    print(f"[Input] {user_input['input_content']}")
    
    try:
        final_state = app.invoke(user_input)
        
        if final_state.get("error"):
            print(f"[Error] Workflow terminated: {final_state['error']}")
        else:
            print("--- Workflow Completed Successfully ---")
            print(f"Department: {final_state['department_name']}")
            print(f"Resolution: {final_state['officer_response']}")
            
    except Exception as e:
        print(f"[Critical Error] {e}")
