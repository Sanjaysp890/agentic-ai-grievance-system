import os
import sys
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from faster_whisper import WhisperModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

print("[System] Loading Whisper Model (CPU/Int8)...")
asr_model = WhisperModel("small", device="cpu", compute_type="int8")

print("[System] Connecting to LLM Provider...")
if not os.getenv("GROQ_API_KEY"):
    print("[Error] GROQ_API_KEY not found in environment variables.")
    
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

class AgentState(TypedDict):
    input_type: str
    input_content: str
    metadata: Dict[str, Any]

    detected_language: Optional[str]
    original_transcript: Optional[str]
    english_output: Optional[str]
    error: Optional[str]


def audio_transcriber_node(state: AgentState):
    """
    Node 1: Converts Audio File -> Native Text Transcript
    """
    try:
        audio_path = state["input_content"]
        
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found at path: {audio_path}"}

        print(f"[Intake] Transcribing audio: {audio_path}")
        segments, info = asr_model.transcribe(audio_path)
        
        full_transcript = " ".join([s.text for s in segments])
        
        print(f"[Intake] Detected Language: {info.language}")
        
        return {
            "original_transcript": full_transcript, 
            "detected_language": info.language
        }
    except Exception as e:
        return {"error": f"ASR Processing Failed: {str(e)}"}

def translation_node(state: AgentState):
    """
    Node 2: Converts Native Text -> Standard English
    """
    if state.get("error"):
        return {"english_output": None}

    try:
        text = state.get("original_transcript") or state["input_content"]
        
        if not text:
            return {"error": "No text content found to translate."}

        print(f"[Intake] Normalizing and translating text...")

        prompt = ChatPromptTemplate.from_template(
            """
            You are a strict data normalizer for a Grievance System.
            
            Input Text: "{text}"
            
            Instructions:
            1. Translate the text into clear, objective English.
            2. Remove conversational filler (e.g., "Umm", "Hello sir").
            3. Do not summarize; keep all factual details (dates, locations, names).
            4. Output ONLY the final English text.
            """
        )
        
        chain = prompt | llm
        result = chain.invoke({"text": text})
        
        return {"english_output": result.content.strip()}
    
    except Exception as e:
        return {"error": f"Translation/Normalization Failed: {str(e)}"}

def input_router(state: AgentState):
    """
    Determines entry point based on input modality.
    """
    if state.get("error"):
        return END
    
    if state["input_type"] == "audio":
        return "transcribe"
    return "translate"


workflow = StateGraph(AgentState)

workflow.add_node("transcribe", audio_transcriber_node)
workflow.add_node("translate", translation_node)

workflow.set_conditional_entry_point(
    input_router,
    {
        "transcribe": "transcribe", 
        "translate": "translate",
        END: END
    }
)

workflow.add_edge("transcribe", "translate")
workflow.add_edge("translate", END)

intake_agent = workflow.compile()

if __name__ == "__main__":
    try:
        import sounddevice as sd
        import numpy as np
        from scipy.io.wavfile import write
        
        def record_audio(filename="live_input.wav", duration=5):
            print(f"\n[Test] Recording for {duration} seconds...")
            fs = 44100 
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()
            write(filename, fs, (recording * 32767).astype(np.int16))
            print("[Test] Recording saved.")
            return filename
            
    except ImportError:
        print("[Warning] 'sounddevice' not installed. Live recording disabled.")
        def record_audio(*args):
            return None

    print("\n--- INTAKE AGENT TEST INTERFACE ---")
    
    while True:
        user_input = input("\n[Input] Type text, filename, 'rec', or 'quit': ").strip()
        
        if user_input.lower() in ["quit", "exit"]:
            break
            
        inputs = {}
        
        if user_input.lower() == "rec":
            audio_file = record_audio()
            if audio_file:
                inputs = {
                    "input_type": "audio", 
                    "input_content": audio_file, 
                    "metadata": {}
                }
            else:
                continue

        elif user_input.endswith((".mp3", ".wav", ".m4a")):
             inputs = {
                "input_type": "audio", 
                "input_content": user_input, 
                "metadata": {}
            }
            
        else:
            inputs = {
                "input_type": "text", 
                "input_content": user_input, 
                "metadata": {}
            }

        result = intake_agent.invoke(inputs)

        if result.get("error"):
            print(f"[Error] {result['error']}")
        else:
            if result.get('original_transcript'):
                print(f"[Transcript] {result['original_transcript']}")
            print(f"[English Output] {result['english_output']}")
