from typing import Dict, Any, List
import os
import json
from datetime import datetime

import chromadb
from chromadb.utils import embedding_functions

# -------------------------------------------------
# Persistent ChromaDB Configuration
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
CHROMA_PATH = os.path.join(BASE_DIR, "database", "chromadb")
METADATA_PATH = os.path.join(BASE_DIR, "database", "metadata")

os.makedirs(CHROMA_PATH, exist_ok=True)
os.makedirs(METADATA_PATH, exist_ok=True)

# Use PersistentClient instead of Client with Settings
chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="grievance_memory",
    embedding_function=embedding_function
)

SIMILARITY_THRESHOLD = 0.75
MAX_PREVIOUS_RESPONSES = 3


def save_metadata_to_file(record_id: str, complaint: str, response: str, timestamp: str):
    """
    Save a human-readable metadata file for each complaint-response pair.
    Creates both individual JSON files and appends to a master log.
    """
    
    # 1. Individual record file (JSON)
    record_filename = f"{record_id}.json"
    record_filepath = os.path.join(METADATA_PATH, record_filename)
    
    record_data = {
        "id": record_id,
        "timestamp": timestamp,
        "complaint": complaint,
        "response": response
    }
    
    with open(record_filepath, 'w', encoding='utf-8') as f:
        json.dump(record_data, f, indent=2, ensure_ascii=False)
    
    # 2. Master log file (append mode)
    master_log = os.path.join(METADATA_PATH, "master_log.jsonl")
    
    with open(master_log, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record_data, ensure_ascii=False) + '\n')
    
    print(f"[Metadata] Saved to: {record_filename}")


def learning_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stores complaint-response pairs persistently in ChromaDB
    and retrieves previous responses for semantically similar complaints.
    Also saves human-readable metadata files for reference.
    """

    complaint_text = state.get("english_output")
    officer_response = state.get("officer_response")

    if not complaint_text or not officer_response:
        return {
            "learning_agent_status": "Skipped (missing complaint or response)"
        }

    # 1. Retrieve similar past complaints
    results = collection.query(
        query_texts=[complaint_text],
        n_results=MAX_PREVIOUS_RESPONSES
    )

    previous_responses: List[str] = []

    if results and results.get("distances"):
        for idx, distance in enumerate(results["distances"][0]):
            similarity = 1 - distance
            if similarity >= SIMILARITY_THRESHOLD:
                metadata = results["metadatas"][0][idx]
                if metadata and "response" in metadata:
                    previous_responses.append(metadata["response"])

    # 2. Store current complaint + response
    import time
    
    unique_id = f"complaint_{int(time.time() * 1000000)}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Store in ChromaDB
    collection.add(
        documents=[complaint_text],
        metadatas=[{
            "complaint": complaint_text,
            "response": officer_response,
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d")
        }],
        ids=[unique_id]
    )
    
    # Save human-readable metadata
    save_metadata_to_file(
        record_id=unique_id,
        complaint=complaint_text,
        response=officer_response,
        timestamp=timestamp
    )

    print("[Learning Agent] Complaint & response stored in ChromaDB")
    print(f"[Learning Agent] Total stored records: {collection.count()}")
    print(f"[Learning Agent] ChromaDB path: {CHROMA_PATH}")
    print(f"[Learning Agent] Metadata path: {METADATA_PATH}")

    return {
        "learning_agent_status": "Stored",
        "previous_responses": previous_responses
    }