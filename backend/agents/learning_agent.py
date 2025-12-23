import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

import chromadb
from chromadb.utils import embedding_functions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
DB_DIR = os.path.join(BASE_DIR, "database")
CHROMA_PATH = os.path.join(DB_DIR, "chromadb")
METADATA_PATH = os.path.join(DB_DIR, "metadata")

os.makedirs(CHROMA_PATH, exist_ok=True)
os.makedirs(METADATA_PATH, exist_ok=True)

print(f"[System] Loading Knowledge Base from: {CHROMA_PATH}")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="grievance_memory",
    embedding_function=embedding_fn
)

SIMILARITY_THRESHOLD = 0.5
MAX_RESULTS = 3

def save_metadata_log(record_id: str, complaint: str, response: str):
    """
    Saves a human-readable JSON log for audit trails.
    """
    record_data = {
        "id": record_id,
        "timestamp": datetime.now().isoformat(),
        "complaint": complaint,
        "response": response
    }

    file_path = os.path.join(METADATA_PATH, f"{record_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(record_data, f, indent=2)

def retrieve_similar(complaint_text: str) -> List[str]:
    """
    Query Vector DB for semantically similar past grievances.
    """
    if not complaint_text:
        return []

    results = collection.query(
        query_texts=[complaint_text],
        n_results=MAX_RESULTS
    )

    found_responses = []

    if results and results.get("distances") and results.get("metadatas"):
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        
        for dist, meta in zip(distances, metadatas):
            if dist < (1 - SIMILARITY_THRESHOLD):  
                if meta and "response" in meta:
                    found_responses.append(meta["response"])
    
    return found_responses

def ingest_record(complaint_text: str, response_text: str):
    """
    Save new Q&A pair to Vector DB.
    """
    unique_id = f"ticket_{int(time.time())}"
    
    collection.add(
        documents=[complaint_text],
        metadatas=[{
            "response": response_text,
            "timestamp": datetime.now().isoformat()
        }],
        ids=[unique_id]
    )
    
    save_metadata_log(unique_id, complaint_text, response_text)
    return unique_id


def learning_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dual-Mode Agent:
    - Mode 'retrieve': Fetches history (Phase 1)
    - Mode 'ingest': Saves new data (Phase 2)
    """
    mode = state.get("task_mode", "retrieve")
    complaint = state.get("english_output")
    
    if not complaint:
        return {"error": "Learning Agent: No complaint text found."}

    if mode == "retrieve":
        print(f"[Learning] Searching Knowledge Base for: '{complaint[:30]}...'")
        past_responses = retrieve_similar(complaint)
        print(f"[Learning] Found {len(past_responses)} similar past cases.")
        
        return {
            "previous_responses": past_responses,
            "learning_agent_status": "Retrieved"
        }

    elif mode == "ingest":
        response = state.get("officer_response")
        
        if not response:
            print("[Learning] Skipping ingestion (No officer response to save).")
            return {"learning_ingestion_status": "Skipped"}
            
        print(f"[Learning] Indexing new solution into Vector DB...")
        rec_id = ingest_record(complaint, response)
        print(f"[Learning] Knowledge Base Updated. Total Records: {collection.count()}")
        
        return {
            "learning_ingestion_status": f"Indexed ({rec_id})"
        }

    return {}

if __name__ == "__main__":
    print("--- LEARNING AGENT TEST ---")
    
    test_state_1 = {
        "task_mode": "ingest",
        "english_output": "The tap water is brown.",
        "officer_response": " flushed the main line."
    }
    learning_agent_node(test_state_1)
    
    test_state_2 = {
        "task_mode": "retrieve",
        "english_output": "Water coming from tap is dirty."
    }
    res = learning_agent_node(test_state_2)
    print("\nRetrieval Result:", res.get("previous_responses"))
