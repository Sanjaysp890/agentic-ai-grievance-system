import time
from typing import Dict, Any

SLA_CRITICAL_THRESHOLD_SEC = 15 
SLA_STANDARD_THRESHOLD_SEC = 30

def escalation_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Monitors Department performance against SLAs.
    Escalates if:
    1. Urgency is extremely high (Immediate Supervisor Alert).
    2. Response time exceeded the allowed threshold.
    """

    classification = state.get("classification", {})
    urgency = classification.get("urgency_score", 0)

    meta = state.get("metadata", {})
    start_time = meta.get("intake_time", time.time())
    end_time = state.get("response_timestamp", time.time())

    time_taken = end_time - start_time
    
    print(f"[Escalation] Analyzing SLA Compliance... (Time Taken: {time_taken:.2f}s)")

    if urgency >= 9:
        reason = f"Critical Severity Score ({urgency}/10) requires Supervisor oversight."
        print(f"[Escalation] ⚠ FLAG RAISED: {reason}")
        return {
            "escalation_status": "escalated",
            "escalation_reason": reason
        }

    allowed_limit = SLA_CRITICAL_THRESHOLD_SEC if urgency > 6 else SLA_STANDARD_THRESHOLD_SEC
    
    if time_taken > allowed_limit:
        reason = f"SLA Breach. Response took {time_taken:.2f}s (Limit: {allowed_limit}s)."
        print(f"[Escalation] ⚠ FLAG RAISED: {reason}")
        return {
            "escalation_status": "escalated",
            "escalation_reason": reason
        }

    return {
        "escalation_status": "normal",
        "escalation_reason": None
    }
