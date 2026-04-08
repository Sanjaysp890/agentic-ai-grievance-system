from typing import List, Dict, Any
from datetime import datetime, timedelta
from backend.databases.db import get_connection

# ============================================================================
# CONFIG
# ============================================================================

ESCALATION_TIME_LIMIT_HOURS = 48


# ============================================================================
# ESCALATION LOGIC
# ============================================================================

def escalation_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Escalates a single complaint if unresolved beyond 48 hours.
    Used as a LangGraph node — reads from state dict.
    """

    created_at = state.get("created_at")
    resolved = state.get("officer_response") is not None

    if created_at and not resolved:
        created_time = datetime.fromisoformat(str(created_at))
        if datetime.utcnow() - created_time > timedelta(hours=ESCALATION_TIME_LIMIT_HOURS):
            return {
                "escalated": True,
                "escalation_reason": f"Complaint unresolved for more than {ESCALATION_TIME_LIMIT_HOURS} hours"
            }

    return {
        "escalated": False,
        "escalation_reason": None
    }


# ============================================================================
# DB-LEVEL ESCALATION CHECK (for existing complaints in database)
# ============================================================================

def get_unresolved_escalated_complaints() -> List[Dict[str, Any]]:
    """
    Queries the database for all complaints that:
    - Are NOT resolved (status != 'RESOLVED')
    - Were created more than 48 hours ago
    
    Returns a list of complaint dicts with escalated=True.
    """
    conn = get_connection()
    cur = conn.cursor()

    cutoff_time = datetime.utcnow() - timedelta(hours=ESCALATION_TIME_LIMIT_HOURS)

    cur.execute(
        """
        SELECT
            complaint_id,
            english_text,
            original_input,
            department,
            priority,
            status,
            created_at,
            user_id
        FROM complaints
        WHERE status != 'RESOLVED'
          AND created_at <= %s
        ORDER BY created_at ASC;
        """,
        (cutoff_time,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    complaints = []
    for row in rows:
        complaints.append({
            "complaint_id": row[0],
            "english_text": row[1],
            "original_input": row[2],
            "department": row[3],
            "priority": row[4],
            "status": row[5],
            "created_at": row[6],
            "user_id": row[7],
            "escalated": True,
            "escalation_reason": f"Unresolved for more than {ESCALATION_TIME_LIMIT_HOURS} hours"
        })

    return complaints


def mark_complaint_escalated(complaint_id: int) -> None:
    """
    Updates the complaint status to 'ESCALATED' in the database.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE complaints
        SET status = 'ESCALATED'
        WHERE complaint_id = %s
          AND status != 'RESOLVED';
        """,
        (complaint_id,)
    )

    conn.commit()
    cur.close()
    conn.close()


def run_escalation_check() -> List[Dict[str, Any]]:
    """
    Main function to:
    1. Find all unresolved complaints older than 48 hours
    2. Mark them as ESCALATED in the DB
    3. Return the list for display/logging

    Call this on a schedule (e.g. every hour via cron or APScheduler).
    """
    escalated = get_unresolved_escalated_complaints()

    for complaint in escalated:
        mark_complaint_escalated(complaint["complaint_id"])
        print(f"[Escalation] 🚨 Complaint #{complaint['complaint_id']} escalated — "
              f"unresolved since {complaint['created_at']}")

    if not escalated:
        print("[Escalation] ✅ No complaints require escalation.")

    return escalated


# ============================================================================
# PRIORITY QUEUE SYSTEM
# ============================================================================

def get_prioritized_complaints(complaints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Returns complaints sorted by priority:
    1. Escalated complaints first (highest urgency first)
    2. Non-escalated complaints (highest urgency first)
    3. Tiebreaker: older complaints first
    """

    def get_priority_key(complaint: Dict[str, Any]) -> tuple:
        is_escalated = complaint.get("escalated", False)
        classification = complaint.get("classification", {})
        urgency_score = classification.get("urgency_score", 0)
        created_at = complaint.get("created_at", datetime.now().isoformat())
        return (
            0 if is_escalated else 1,
            -urgency_score,
            str(created_at)
        )

    return sorted(complaints, key=get_priority_key)


def display_complaint_queue(complaints: List[Dict[str, Any]]) -> None:
    """
    Display complaints in priority order with visual indicators.
    """
    prioritized = get_prioritized_complaints(complaints)

    print("\n" + "=" * 80)
    print("COMPLAINT PRIORITY QUEUE")
    print("=" * 80)

    for idx, complaint in enumerate(prioritized, 1):
        escalated = complaint.get("escalated", False)
        classification = complaint.get("classification", {})
        urgency = classification.get("urgency_score", 0)
        departments = classification.get("departments", [])
        text = complaint.get("english_text", complaint.get("english_output", ""))[:60] + "..."

        status_icon = "🚨 ESCALATED" if escalated else "📋 Active"
        urgency_bar = "█" * urgency + "░" * (10 - urgency)

        print(f"\n#{idx} | {status_icon}")
        print(f"    Urgency:     [{urgency_bar}] {urgency}/10")
        print(f"    Departments: {', '.join(departments) if departments else complaint.get('department', 'N/A')}")
        print(f"    Complaint:   {text}")
        print(f"    ID:          {complaint.get('complaint_id', complaint.get('id', 'N/A'))}")
        print(f"    Created:     {complaint.get('created_at', 'N/A')}")
        print("-" * 80)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Running escalation check on existing DB complaints...\n")
    escalated_complaints = run_escalation_check()
    print(f"\nTotal escalated: {len(escalated_complaints)}")