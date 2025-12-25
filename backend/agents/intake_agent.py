import os
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from pathlib import Path

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from faster_whisper import WhisperModel

# DB import (used only in CLI mode)
from ..databases.db import save_complaint


# ======================================================
# EXPLICIT .env LOADING (WINDOWS + UVICORN SAFE)
# ======================================================
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in environment variables")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


# ======================================================
# LAZY-LOADED MODELS (FASTAPI SAFE)
# ======================================================
_asr_model = None
_llm = None


def get_asr_model():
    global _asr_model
    if _asr_model is None:
        print(" Loading Whisper Model... (once)")
        _asr_model = WhisperModel("small", device="cpu", compute_type="int8")
    return _asr_model


def get_llm():
    global _llm
    if _llm is None:
        print(" Connecting to Groq... (once)")
        _llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0
        )
    return _llm


# ======================================================
# STATE
# ======================================================
class AgentState(TypedDict):
    input_type: str
    input_content: str
    metadata: Dict[str, Any]

    detected_language: Optional[str]
    original_transcript: Optional[str]
    english_output: Optional[str]
    error: Optional[str]


# ======================================================
# AGENT NODES
# ======================================================
def audio_transcriber_node(state: AgentState):
    try:
        audio_path = state["input_content"]

        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found: {audio_path}"}

        asr_model = get_asr_model()
        segments, info = asr_model.transcribe(audio_path)

        transcript = " ".join([s.text for s in segments])

        return {
            "original_transcript": transcript,
            "detected_language": info.language
        }

    except Exception as e:
        return {"error": f"ASR Failed: {str(e)}"}


def translation_node(state: AgentState):
    if state.get("error"):
        return {"english_output": None}

    try:
        text = state.get("original_transcript") or state["input_content"]

        prompt = ChatPromptTemplate.from_template(
            """
            Translate the input into professional English.
            Preserve the original meaning strictly.
            Output ONLY the translated text.

            INPUT: "{text}"
            """
        )

        llm = get_llm()
        chain = prompt | llm
        result = chain.invoke({"text": text})

        return {"english_output": result.content.strip()}

    except Exception as e:
        return {"error": f"Translation Failed: {str(e)}"}


# ======================================================
# ROUTER
# ======================================================
def input_router(state: AgentState):
    if state.get("error"):
        return END

    if state["input_type"] == "audio":
        return "transcribe"

    return "translate"


# ======================================================
# LANGGRAPH WORKFLOW
# ======================================================
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


# ======================================================
# OPTIONAL CLI MODE (SAFE)
# ======================================================
if __name__ == "__main__":
    print(" Intake Agent CLI Mode")

    while True:
        text = input("Enter complaint (or 'quit'): ").strip()
        if text.lower() == "quit":
            break

        state = {
            "input_type": "text",
            "input_content": text,
            "metadata": {"source": "cli"}
        }

        result = intake_agent.invoke(state)

        if result.get("english_output"):
            save_complaint(
                text,
                result["english_output"],
                "text",
                result.get("detected_language", "en")
            )

        print(result)
