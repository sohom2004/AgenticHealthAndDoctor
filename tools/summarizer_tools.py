"""
Summarizer tools for retrieving patient findings history
"""
import json
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from config.settings import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    FINDINGS_COLLECTION,
    SUMMARY_COLLECTION
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
    
def store_summaries(summary: str, user_id: str):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=SUMMARY_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_timestamp = datetime.now().isoformat()

    document = Document(
        page_content=summary,
        metadata={
            "user_id": user_id,
            "date": current_date,
            "timestamp": current_timestamp
        }
    )
    vector_store.add_documents(documents=[document])
    print(f"✅ Saved summary for user {user_id} on {current_date}")
    return "Summaries saved successfully"