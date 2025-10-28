"""
Summarizer tools for retrieving patient findings history
"""
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config.settings import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    FINDINGS_COLLECTION
)


def get_all_findings(user_id: str) -> list:
    """
    Retrieves all findings for a specific patient
    
    Args:
        user_id: Patient ID
        
    Returns:
        List of finding documents
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=FINDINGS_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    results = vector_store.get(
        where={"patient_id": user_id},
        include=["documents", "metadatas"]
    )
    
    docs = []
    for doc in results.get("documents", []):
        try:
            docs.append(json.loads(doc))
        except Exception:
            continue
    
    print(f"Retrieved {len(docs)} finding documents for patient {user_id}")
    return docs


def get_recent_findings(user_id: str) -> dict:
    """
    Retrieves the most recent findings for a patient
    
    Args:
        user_id: Patient ID
        
    Returns:
        Most recent finding document
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=FINDINGS_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    results = vector_store.get(
        where={"patient_id": user_id},
        include=["documents", "metadatas"]
    )
    
    if not results.get("documents"):
        return {}
    
    last_doc = results["documents"][-1]
    try:
        return json.loads(last_doc)
    except Exception:
        return {}