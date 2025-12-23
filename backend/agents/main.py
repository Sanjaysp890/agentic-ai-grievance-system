import sys
import os
import time
from typing import TypedDict, Optional, Dict, Any, Literal, List
from langgraph.graph import StateGraph, END

# ---------------- DB IMPORTS (ONLY ADDITIONS) ----------------
from ..databases.db import (
    save_complaint,
    update_complaint_classification,
    save_department_response
)

# ------------------------------------------------------------

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


def capture_audio_from_mic(filename="live_input.wav", duration=5):
    try:
        import sounddevice as sd
        import numpy as np
        from scipy.io.wavfile import write

        print(f"\n[Mic] Recording for {duration} seconds... Speak now!")
        fs = 44100

        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()

        write(filename, fs, (recording * 32767).astype(np.int16))
        print("[Mic] Recording saved successfully.")
        return filename

    except Exception as e:
        print(f"[Error] Microphone recording failed: {e}")
        return None


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


def intake_wrapper(state: MasterState):
    print("[System] Initializing Intake Agent...")
    result = intake_agent.invoke(state)

    if result.get("error"):
        return {"error": result["error"]}

    complaint_id = save_complaint(
        state["input_content"],
        result.get("english_output"),
        state["input_type"],
        result.get("detected_language", "en")
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

    print("[System] Querying Knowledge Base for similar past issues...")
    state["task_mode"] = "retrieve"
    return learning_agent_node(state)


def classifier_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    print("[System] Classifying grievance for routing...")
    result = classifier_node(state)

    classification = result.get("classification", {})
    depts = classification.get("departments", [])
    priority = classification.get("priority", "medium")

    if depts:
        update_complaint_classification(
            state["complaint_id"],
            depts[0],
            priority
        )

    return result


def learning_ingestion_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    if not state.get("officer_response"):
        return {}

    print("[System] Indexing new resolution into Knowledge Base...")
    state["task_mode"] = "ingest"
    return learning_agent_node(state)


def escalation_wrapper(state: MasterState):
    if state.get("error"):
        return {"error": state["error"]}

    print("[System] Running Escalation Checks...")
    return escalation_agent_node(state)


def route_complaint(state: MasterState) -> Literal["water", "police", "electric", "general"]:
    if state.get("error"):
        return END

    classification = state.get("classification", {})
    depts = classification.get("departments", [])

    if not depts:
        return "general"

    primary = depts[0].lower()

    if "water" in primary:
        return "water"
    elif any(k in primary for k in ["police", "crime", "theft"]):
        return "police"
    elif any(k in primary for k in ["electric", "power", "energy"]):
        return "electric"
    else:
        return "general"


workflow = StateGraph(MasterState)

workflow.add_node("intake", intake_wrapper)
workflow.add_node("learning_retrieval", learning_retrieval_wrapper)
workflow.add_node("classifier", classifier_wrapper)

workflow.add_node("water_node", water_dept_node)
workflow.add_node("police_node", police_dept_node)
workflow.add_node("electric_node", electricity_dept_node)
workflow.add_node("general_node", general_dept_node)

workflow.add_node("learning_ingestion", learning_ingestion_wrapper)
workflow.add_node("escalation", escalation_wrapper)

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
    workflow.add_edge(node, "learning_ingestion")

workflow.add_edge("learning_ingestion", "escalation")
workflow.add_edge("escalation", END)

app = workflow.compile()


if __name__ == "__main__":
    print("\n" + "▓"*60)
    print("   🏛️  PUBLIC GRIEVANCE REDRESSAL AI SYSTEM v1.0")
    print("▓"*60)

    while True:
        print("\nSelect Input Mode:")
        print("1. Text Complaint")
        print("2. Audio File Upload")
        print("3. Live Recording (Microphone)")
        print("q. Quit")

        mode = input("\n> Choice: ").strip().lower()

        if mode == 'q':
            print("Exiting system. Goodbye!")
            break

        if mode == '1':
            user_input = {
                "input_type": "text",
                "input_content": input(" Enter your grievance: ").strip(),
                "metadata": {"source": "cli_text", "user_id": "citizen_cli"}
            }
        elif mode == '2':
            path = input(" Enter path to audio file: ").strip()
            if not os.path.exists(path):
                print("File not found.")
                continue
            user_input = {
                "input_type": "audio",
                "input_content": path,
                "metadata": {"source": "cli_file", "user_id": "citizen_cli"}
            }
        elif mode == '3':
            audio = capture_audio_from_mic()
            if not audio:
                continue
            user_input = {
                "input_type": "audio",
                "input_content": audio,
                "metadata": {"source": "cli_mic", "user_id": "citizen_cli"}
            }
        else:
            print("Invalid choice.")
            continue

        print("\nProcessing Ticket...\n")
        final_state = app.invoke(user_input)

        try:
            if final_state.get("complaint_id") and final_state.get("department_name") and final_state.get("officer_response"):
                save_department_response(
                    final_state["complaint_id"],
                    final_state["department_name"],
                    final_state["officer_response"]
                )
        except Exception as db_err:
            print(f"[Warning] DB save failed: {db_err}")

        print("\n" + "="*60)
        print(" FINAL CITIZEN DISPLAY")
        print("="*60)
        print(f"\n RESPONSE FROM {final_state.get('department_name','SYSTEM').upper()}:")
        print(f"\"{final_state.get('officer_response','No response available.')}\"")
