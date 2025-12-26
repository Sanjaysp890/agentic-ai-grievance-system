import json
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator

# --- 1. SETUP ---
# We use a lower temperature to reduce "creative" repetition
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# --- 2. DEFINE THE OUTPUT SCHEMA ---
class GrievanceClassification(BaseModel):
    urgency_score: int = Field(
        ..., 
        description="Score between 1 (Low) and 10 (Critical)"
    )
    departments: List[str] = Field(
        ..., 
        description="List of relevant departments"
    )
    sentiment: str = Field(
        ..., 
        description="User's emotional tone"
    )
    reasoning: str = Field(
        ..., 
        description="Brief reason for the score"
    )

    # FIX: Auto-remove duplicate departments if the AI repeats them
    @validator('departments')
    def remove_duplicates(cls, v):
        return list(set(v))

parser = PydanticOutputParser(pydantic_object=GrievanceClassification)

# --- 3. THE STRICT PROMPT ---
# We customized the format instructions to be cleaner for Llama 3
classification_prompt = ChatPromptTemplate.from_template(
    """
    You are an AI Classifier. Task: Analyze the complaint and output strictly structured JSON.
    
    COMPLAINT: "{text}"
    
    RULES:
    1. Urgency: 1-10 (10=Life Threatening).
    2. Departments: Choose from [Police, WaterBoard, Electricity].
    3. JSON ONLY. No markdown, no "Here is the JSON", no repeated text.
    
    {format_instructions}
    """
)

# --- 4. THE AGENT NODE ---
def classifier_node(state):
    english_text = state.get("english_output")
    if not english_text:
        return {"error": "No text to classify"}

    # print(f"🧐 Classifying...") # Commented out to reduce noise

    try:
        # Step 1: Generate Raw Text
        chain = classification_prompt | llm
        response = chain.invoke({
            "text": english_text,
            "format_instructions": parser.get_format_instructions()
        })
        
        raw_content = response.content.strip()
        
        # FIX: Manually clean markdown code blocks if the LLM adds them
        # (Llama 3 loves adding ```json ... ```)
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[1].split("```")[0].strip()

        # Step 2: Parse the cleaned text
        parsed_data = parser.parse(raw_content)
        
        return {"classification": parsed_data.dict()}
        
    except Exception as e:
        return {"error": f"Classification failed: {str(e)}"}

# --- 5. TEST RUNNER ---
if __name__ == "__main__":
    test_inputs = [
        "There is a massive fire in the garbage dump! Kids are coughing.",
        "My street light is flickering.",
        "The water supply is dirty."
    ]

    print("--- TESTING CLASSIFIER AGENT ---")
    
    for text in test_inputs:
        print(f"\n📝 Input: {text}")
        result = classifier_node({"english_output": text})
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            # Clean print of the JSON
            print(json.dumps(result["classification"], indent=2))
