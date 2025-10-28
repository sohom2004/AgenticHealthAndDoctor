"""
Document storage and retrieval tools for ChromaDB
"""
import re
from datetime import datetime
from uuid import uuid4
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from config.settings import (
    CHROMA_DIR, 
    EMBEDDING_MODEL, 
    REPORT_COLLECTION,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DEFAULT_PATIENT_ID
)


def extract_report_data(text: str) -> tuple:
    """
    Extracts report date and confidence from text
    
    Args:
        text: Text containing report data
        
    Returns:
        Tuple of (report_date, confidence)
    """
    # Extract date
    match = (
        re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        or re.search(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b", text)
    )
    
    report_date = None
    if match:
        rep_date = match.group(1)
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
            try:
                report_date = datetime.strptime(rep_date, fmt).date().isoformat()
                break
            except ValueError:
                continue
    
    if not report_date:
        report_date = datetime.now().date().isoformat()

    # Extract confidence
    conf_match = re.search(r"'confidence'\s*:\s*([0-9]*\.?[0-9]+)", text)
    confidence = float(conf_match.group(1)) if conf_match else None

    return report_date, confidence


def get_next_report_id() -> str:
    """
    Generates next sequential report ID
    
    Returns:
        Report ID string (e.g., "RPT-1")
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=REPORT_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    results = vector_store.get(include=["metadatas"])
    
    if not results["metadatas"]:
        return "RPT-1"
    
    report_ids = [m["report_id"] for m in results["metadatas"] if "report_id" in m]
    
    if not report_ids:
        return "RPT-1"
    
    max_id = max(int(r.split("-")[1]) for r in report_ids)
    return f"RPT-{max_id + 1}"


def convert_text_to_document(
    report_date: str, 
    confidence: float, 
    content: str, 
    patient_id: str = DEFAULT_PATIENT_ID
) -> tuple:
    """
    Converts text to LangChain Document with metadata
    
    Args:
        report_date: Date of report
        confidence: OCR confidence score
        content: Report content
        patient_id: Patient identifier
        
    Returns:
        Tuple of (document, metadata)
    """
    report_id = get_next_report_id()
    
    metadata = {
        "report_id": report_id,
        "patient_id": patient_id,
        "report_date": report_date,
        "confidence": confidence,
    }
    
    document = Document(
        page_content=content,
        metadata=metadata
    )
    
    return document, metadata


def split_document(document: Document) -> list:
    """
    Splits document into chunks for embedding
    
    Args:
        document: LangChain Document
        
    Returns:
        List of document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=True,
    )
    
    chunks = text_splitter.split_documents([document])
    return chunks


def store_in_chroma(chunks: list) -> None:
    """
    Stores document chunks in ChromaDB
    
    Args:
        chunks: List of document chunks
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=REPORT_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    uuids = [str(uuid4()) for _ in range(len(chunks))]
    vector_store.add_documents(documents=chunks, ids=uuids)
    print(f"Stored {len(chunks)} document chunks in ChromaDB")


def store_content(text: str, patient_id: str = DEFAULT_PATIENT_ID) -> dict:
    """
    Complete pipeline to store content in ChromaDB
    
    Args:
        text: Text content to store
        patient_id: Patient identifier
        
    Returns:
        Metadata dictionary
    """
    report_date, confidence = extract_report_data(str(text))
    
    # Explicitly pass patient_id
    document, metadata = convert_text_to_document(
        report_date, 
        confidence, 
        text, 
        patient_id=patient_id  # ← Ensure patient_id is used
    )
    chunks = split_document(document)
    store_in_chroma(chunks)
    
    return metadata