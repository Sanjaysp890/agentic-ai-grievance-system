import os
import time
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from faster_whisper import WhisperModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

from ..databases.db import save_complaint



from dotenv import load_dotenv
load_dotenv()

print(" Loading Whisper Model... (This happens only once)")
asr_model = WhisperModel("small", device="cpu", compute_type="int8")

print(" Connecting to Groq...")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
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
    try:
        audio_path = state["input_content"]
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found: {audio_path}"}

        print(f" Transcribing audio: {audio_path}")
        segments, info = asr_model.transcribe(audio_path)
        full_transcript = " ".join([s.text for s in segments])
        
        return {
            "original_transcript": full_transcript, 
            "detected_language": info.language
        }
    except Exception as e:
        return {"error": f"ASR Failed: {str(e)}"}

def translation_node(state: AgentState):
    if state.get("error"):
        return {"english_output": None}

    try:
        text = state.get("original_transcript") or state["input_content"]
        print(f" Translating...")

        prompt = ChatPromptTemplate.from_template(
            """
            You are a strict translator for a Public Grievance System. 
            
            Input Text: "{text}"
            
            Instructions:
            1. Translate the input into standard, professional English.
            2. STRICTLY maintain the original meaning. **DO NOT** add words, emotions, or calls to action that are not in the source text.
            3. If the input is already in English, return it exactly as is (corrected for grammar only).
            4. Output ONLY the final text.
            """
        )
        
        chain = prompt | llm
        result = chain.invoke({"text": text})
        
        return {"english_output": result.content.strip()}
    
    except Exception as e:
        return {"error": f"Translation Failed: {str(e)}"}

def input_router(state: AgentState):
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

def record_audio(filename="live_input.wav", duration=5):
    print(f" Recording for {duration} seconds... Speak now!")
    fs = 44100 
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, (recording * 32767).astype(np.int16))
    print(" Recording saved.")
    return filename

if __name__ == "__main__":
    print("\n AGENT READY!")
    print("1. Type text to chat")
    print("2. Type 'rec' to record voice (5s)")
    print("---------------------------------------")

    while True:
        user_input = input("\nInput (or 'rec'/'quit'): ").strip()
        
        if user_input.lower() in ["quit", "exit"]:
            break
            
        if user_input.lower() == "rec":
            audio_file = record_audio()
            inputs = {
                "input_type": "audio",
                "input_content": audio_file,
                "metadata": {"source": "live_mic"}
            }
        
        elif user_input.endswith(".mp3") or user_input.endswith(".wav"):
             inputs = {
                "input_type": "audio",
                "input_content": user_input,
                "metadata": {"source": "file_upload"}
            }
            
        else:
            inputs = {
                "input_type": "text",
                "input_content": user_input,
                "metadata": {"source": "cli_text"}
            }

        print("Processing...")

        result = intake_agent.invoke(inputs)

        if result.get("english_output"):
            save_complaint(
                inputs["input_content"],
                result["english_output"],
                inputs["input_type"],
                result.get("detected_language", "en")
            )

        if result.get("error"):
            print(f"ERROR: {result['error']}")
        else:
            if result.get('original_transcript'):
                print(f"TRANSCRIPT: {result['original_transcript']}")
            print(f"ENGLISH OUTPUT: {result['english_output']}")
