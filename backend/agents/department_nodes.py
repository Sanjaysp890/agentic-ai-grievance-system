import time
from typing import Dict, Any


def run_department_qa(dept_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Department assignment node.

    USER FLOW:
    - Assigns department
    - Does NOT expect officer response

    ADMIN FLOW:
    - If officer_response exists, records it with timestamp
    """

    response = state.get("officer_response")

    # ✅ USER FLOW (no admin response yet)
    if not response:
        return {
            "department_name": dept_name,
            "officer_response": None,
            "response_timestamp": None
        }

    # ✅ ADMIN FLOW (response provided)
    return {
        "department_name": dept_name,
        "officer_response": response,
        "response_timestamp": time.time()
    }


def water_dept_node(state: Dict[str, Any]):
    return run_department_qa("Water Board", state)


def police_dept_node(state: Dict[str, Any]):
    return run_department_qa("Police Department", state)


def electricity_dept_node(state: Dict[str, Any]):
    return run_department_qa("Electricity Board", state)


def general_dept_node(state: Dict[str, Any]):
    return run_department_qa("General Administration", state)
