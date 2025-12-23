import sys
import os
import time
from typing import TypedDict, Optional, Dict, Any, Literal, List
from langgraph.graph import StateGraph, END

try:
    from intake_agent import intake_agent
    from classifier_agent import classifier_node
    from department_nodes import (
        water_dept_node,
        police_dept_node,
        electricity_dept_node,
        general_dept_node
    )
    from escalation_agent import escalation_agent_node
    from learning_agent import learning_agent_node
except ImportError as e:
    print(f"System Error: Failed to import required agent modules. {e}")
    sys.exit(1)

def capture_audio_from_mic(filename="live_input.wav", duration=5):
    """
    Captures audio from the default microphone and saves it to a WAV file.
    """
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
        
    except ImportError:
        print("[Error] Libraries 'sounddevice', 'numpy', or 'scipy' not found.")
        print("Please install them using: pip install sounddevice numpy scipy")
        return None
    except Exception as e:
        print(f"[Error] Microphone recording failed: {e}")
        return None

class MasterState(TypedDict):
    """
    Central hub state that aggregates data from all agents.
    """
    input_type: str
    input_content: str
    metadata: Dict[str, Any]

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
        
    return {
        "english_output": result.get("english_output"),
        "original_transcript": result.get("original_transcript"),
        "detected_language": result.get("detected_language"),
        "metadata": {**state.get("metadata", {}), "intake_time": time.time()}
    }

def learning_retrieval_wrapper(state: MasterState):
    if state.get("error"): return {"error": state["error"]}
    
    print("[System] Querying Knowledge Base for similar past issues...")
    state["task_mode"] = "retrieve"
    return learning_agent_node(state)

def classifier_wrapper(state: MasterState):
    if state.get("error"): return {"error": state["error"]}
    
    print("[System] Classifying grievance for routing...")
    return classifier_node(state)

def learning_ingestion_wrapper(state: MasterState):
    if state.get("error"): return {"error": state["error"]}
    
    if not state.get("officer_response"):
        return {}

    print("[System] Indexing new resolution into Knowledge Base...")
    state["task_mode"] = "ingest"
    return learning_agent_node(state)

def escalation_wrapper(state: MasterState):
    if state.get("error"): return {"error": state["error"]}
    
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
    elif any(keyword in primary for keyword in ["police", "crime", "theft"]):
        return "police"
    elif any(keyword in primary for keyword in ["electric", "power", "energy"]):
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

for dept_node in ["water_node", "police_node", "electric_node", "general_node"]:
    workflow.add_edge(dept_node, "learning_ingestion")

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

        user_input = {}
        
        if mode == '1':
            text_in = input(" Enter your grievance: ").strip()
            if not text_in: continue
            
            user_input = {
                "input_type": "text",
                "input_content": text_in,
                "metadata": {"source": "cli_text", "user_id": "citizen_cli"}
            }
            
        elif mode == '2':
            file_path = input(" Enter path to audio file: ").strip()
            file_path = file_path.replace('"', '').replace("'", "") 
            
            if not os.path.exists(file_path):
                print(" Error: File not found.")
                continue
                
            user_input = {
                "input_type": "audio",
                "input_content": file_path,
                "metadata": {"source": "cli_file", "user_id": "citizen_cli"}
            }
            
        elif mode == '3':
            audio_path = capture_audio_from_mic()
            if not audio_path:
                continue
                
            user_input = {
                "input_type": "audio",
                "input_content": audio_path,
                "metadata": {"source": "cli_mic", "user_id": "citizen_cli"}
            }
            
        else:
            print("Invalid choice.")
            continue

        print("\n" + "-"*40)
        print("  Processing Ticket...")
        print("-"*40)

        try:
            final_state = app.invoke(user_input)
            
            if final_state.get("error"):
                print(f"\n SYSTEM ERROR: {final_state['error']}")
            else:
                print("\n" + "="*60)
                print(" FINAL CITIZEN DISPLAY")
                print("="*60)
                
                dept = final_state.get('department_name', 'System')
                resp = final_state.get('officer_response', 'No resolution provided.')
                print(f"\n RESPONSE FROM {dept.upper()}:")
                print(f"\"{resp}\"")
                
                if final_state.get("escalation_status") == "escalated":
                    reason = final_state.get("escalation_reason", "Unknown")
                    print(f"\n  ALERT: Ticket ESCALATED to Supervisor.")
                    print(f"    Reason: {reason}")
                
                history = final_state.get('previous_responses', [])
                if history:
                    print(f"\n SIMILAR PAST RESOLUTIONS:")
                    for idx, item in enumerate(history, 1):
                        print(f"   {idx}. {item}")
                else:
                    print("\n KNOWLEDGE BASE: No similar past cases found.")
                    
        except Exception as e:
            print(f"\n CRITICAL FAILURE: {e}")
            import traceback
            traceback.print_exc()
