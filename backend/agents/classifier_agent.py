import os
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    print("[Warning] GROQ_API_KEY not found in environment variables.")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

class GrievanceClassification(BaseModel):
    """
    Strict schema for classification output.
    Used by the Main Agent to determine routing logic.
    """
    urgency_score: str = Field(
        ...,
        description="Urgency level: LOW, MEDIUM, or HIGH"
    )
    departments: List[str] = Field(
        ...,
        description="List of relevant departments (e.g. Police, Health, WaterBoard)"
    )
    sentiment: str = Field(
        ...,
        description="The emotional tone of the complaint (e.g. Angry, Desperate, Neutral)"
    )
    reasoning: str = Field(
        ...,
        description="A brief explanation for the urgency level and department selection"
    )

    @validator("urgency_score", pre=True)
    def map_urgency(cls, v):
        if isinstance(v, int):
            if v <= 3:
                return "LOW"
            elif v <= 6:
                return "MEDIUM"
            else:
                return "HIGH"
        return v

    @validator('departments')
    def remove_duplicates(cls, v):
        return list(set(v))

parser = PydanticOutputParser(pydantic_object=GrievanceClassification)

classification_prompt = ChatPromptTemplate.from_template(
    """
    You are an AI Classifier for a Public Grievance System.
    Task: Analyze the input text and output strictly structured JSON data.

    COMPLAINT: "{text}"

    RULES:
    1. Urgency: Rate 1-10.
       - 1–3 → LOW
       - 4–6 → MEDIUM
       - 7–10 → HIGH
    2. Departments: Select from [Police, Health, WaterBoard, Electricity, Municipal, RoadTransport, Fire, CyberCrime].
    3. Sentiment: Detect the user's emotion.
    4. Output: JSON ONLY. Do not wrap in markdown blocks. Do not add conversational text.

    {format_instructions}
    """
)

def classifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes English text and returns structured classification data.
    """
    english_text = state.get("english_output")

    if not english_text:
        return {"error": "Classifier Error: No english_output found in state."}

    try:
        chain = classification_prompt | llm
        response = chain.invoke({
            "text": english_text,
            "format_instructions": parser.get_format_instructions()
        })

        raw_content = response.content.strip()

        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[1].split("```")[0].strip()

        parsed_data = parser.parse(raw_content)

        return {"classification": parsed_data.dict()}

    except Exception as e:
        return {"error": f"Classification Failed: {str(e)}"}

if __name__ == "__main__":
    test_inputs = [
        "There is a massive fire in the garbage dump! Kids are coughing.",
        "My street light is flickering.",
        "The water supply is dirty and smells like sewage.",
        "Jaynagar 4th block has been experiencing power outages since 8:00 am yesterday."
    ]

    print("\n--- CLASSIFIER AGENT TEST ---")

    for text in test_inputs:
        print(f"\n[Input] {text}")

        dummy_state = {"english_output": text}

        result = classifier_node(dummy_state)

        if result.get("error"):
            print(f"[Error] {result['error']}")
        else:
            print(json.dumps(result["classification"], indent=2))
