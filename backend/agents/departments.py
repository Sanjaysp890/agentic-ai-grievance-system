import time
from typing import Dict, Any

def run_department_qa(dept_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic handler for department-level resolution.
    Displays ticket details and accepts a resolution string from the operator.
    Captures timestamp for SLA monitoring.
    """
    english_text = state.get("english_output", "")
    classification = state.get("classification", {})
    urgency = classification.get("urgency_score", 0)
    
    print(f"\n[Ticket Assigned] Department: {dept_name.upper()}")
    print(f"[Details] Urgency: {urgency}/10 | Classification: {classification.get('departments', [])}")
    print(f"[Complaint] {english_text}")
    print("-" * 60)
    
    while True:
        response = input(f"Enter resolution ({dept_name}): ").strip()
        if response:
            break
        print("Error: Resolution cannot be empty.")
    
    resolution_time = time.time()
    
    print(f"[System] Ticket resolved by {dept_name} at {time.ctime(resolution_time)}.\n")
    
    return {
        "department_name": dept_name,
        "officer_response": response,
        "response_timestamp": resolution_time
    }


def water_dept_node(state: Dict[str, Any]):
    return run_department_qa("Water Board", state)

def police_dept_node(state: Dict[str, Any]):
    return run_department_qa("Police Department", state)

def electricity_dept_node(state: Dict[str, Any]):
    return run_department_qa("Electricity Board", state)

def general_dept_node(state: Dict[str, Any]):
    return run_department_qa("General Administration", state)
