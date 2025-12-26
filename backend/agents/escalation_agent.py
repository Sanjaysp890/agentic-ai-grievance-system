from typing import List, Dict, Any
from datetime import datetime, timedelta

# ============================================================================
# ESCALATION LOGIC (Original functionality)
# ============================================================================

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


# ============================================================================
# PRIORITY QUEUE SYSTEM (New functionality)
# ============================================================================

def get_prioritized_complaints(complaints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Returns complaints sorted by priority:
    1. Escalated complaints first (sorted by urgency score, highest first)
    2. Non-escalated complaints (sorted by urgency score, highest first)
    
    Args:
        complaints: List of complaint dictionaries with keys:
            - escalated (bool)
            - classification (dict with urgency_score)
            - created_at (datetime string)
            - id, english_output, etc.
    
    Returns:
        Sorted list of complaints
    """
    
    def get_priority_key(complaint: Dict[str, Any]) -> tuple:
        """
        Returns a tuple for sorting:
        - First element: 0 if escalated, 1 if not (so escalated comes first)
        - Second element: negative urgency score (so higher scores come first)
        - Third element: created_at timestamp (older complaints first as tiebreaker)
        """
        is_escalated = complaint.get("escalated", False)
        classification = complaint.get("classification", {})
        urgency_score = classification.get("urgency_score", 0)
        created_at = complaint.get("created_at", datetime.now().isoformat())
        
        # Convert to sortable tuple
        return (
            0 if is_escalated else 1,  # Escalated first
            -urgency_score,             # Higher urgency first (negative for descending)
            created_at                  # Older first (ascending)
        )
    
    # Sort complaints using the priority key
    sorted_complaints = sorted(complaints, key=get_priority_key)
    
    return sorted_complaints


def display_complaint_queue(complaints: List[Dict[str, Any]]) -> None:
    """
    Display complaints in priority order with visual indicators
    """
    prioritized = get_prioritized_complaints(complaints)
    
    print("\n" + "="*80)
    print("COMPLAINT PRIORITY QUEUE")
    print("="*80)
    
    for idx, complaint in enumerate(prioritized, 1):
        escalated = complaint.get("escalated", False)
        classification = complaint.get("classification", {})
        urgency = classification.get("urgency_score", 0)
        departments = classification.get("departments", [])
        text = complaint.get("english_output", "")[:60] + "..."
        
        # Visual indicators
        status_icon = "🚨 ESCALATED" if escalated else "📋 Active"
        urgency_bar = "█" * urgency + "░" * (10 - urgency)
        
        print(f"\n#{idx} | {status_icon}")
        print(f"    Urgency: [{urgency_bar}] {urgency}/10")
        print(f"    Departments: {', '.join(departments)}")
        print(f"    Complaint: {text}")
        print(f"    ID: {complaint.get('id', 'N/A')}")
        print("-" * 80)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("TEST: PRIORITY QUEUE SYSTEM")
    print("="*80)
    
    # Sample complaints for testing
    test_complaints = [
        {
            "id": "C001",
            "english_output": "Street light flickering on Main Street",
            "escalated": False,
            "classification": {
                "urgency_score": 3,
                "departments": ["Electricity"],
                "sentiment": "neutral"
            },
            "created_at": "2024-12-23T10:00:00"
        },
        {
            "id": "C002",
            "english_output": "Major fire at garbage dump, children affected",
            "escalated": True,
            "classification": {
                "urgency_score": 9,
                "departments": ["Fire", "Health"],
                "sentiment": "urgent"
            },
            "created_at": "2024-12-21T08:00:00"
        },
        {
            "id": "C003",
            "english_output": "Water supply contaminated with dirt and debris",
            "escalated": True,
            "classification": {
                "urgency_score": 7,
                "departments": ["WaterBoard", "Health"],
                "sentiment": "concerned"
            },
            "created_at": "2024-12-20T15:30:00"
        },
        {
            "id": "C004",
            "english_output": "Pothole on highway causing accidents",
            "escalated": False,
            "classification": {
                "urgency_score": 6,
                "departments": ["RoadTransport"],
                "sentiment": "worried"
            },
            "created_at": "2024-12-22T12:00:00"
        },
        {
            "id": "C005",
            "english_output": "Cybercrime - identity theft reported",
            "escalated": True,
            "classification": {
                "urgency_score": 8,
                "departments": ["CyberCrime", "Police"],
                "sentiment": "distressed"
            },
            "created_at": "2024-12-21T09:00:00"
        }
    ]
    
    print("\nBEFORE PRIORITIZATION (original order):")
    for i, c in enumerate(test_complaints, 1):
        esc = "🚨" if c["escalated"] else "📋"
        print(f"{i}. {esc} [{c['classification']['urgency_score']}/10] {c['id']}: {c['english_output'][:50]}...")
    
    # Display prioritized queue
    display_complaint_queue(test_complaints)
    
    print("\n\nPRIORITY ORDER SUMMARY:")
    prioritized = get_prioritized_complaints(test_complaints)
    for i, c in enumerate(prioritized, 1):
        esc = "🚨 ESCALATED" if c["escalated"] else "📋 Active   "
        print(f"{i}. {esc} | Urgency: {c['classification']['urgency_score']}/10 | {c['id']}")