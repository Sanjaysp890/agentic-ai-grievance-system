from typing import Dict, Any
from datetime import datetime, timedelta

ESCALATION_TIME_LIMIT_HOURS = 48

def escalation_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Escalates unresolved or critical complaints to higher authority.
    """

    classification = state.get("classification", {})
    urgency = classification.get("urgency_score", 0)

    created_at = state.get("created_at")
    resolved = state.get("officer_response") is not None

    if created_at and not resolved:
        created_time = datetime.fromisoformat(created_at)
        if datetime.utcnow() - created_time > timedelta(hours=ESCALATION_TIME_LIMIT_HOURS):
            return {
                "escalated": True,
                "escalation_reason": "Complaint unresolved beyond time limit"
            }

    return {
        "escalated": False
    }
