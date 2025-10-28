"""
Extraction tools for retrieving and saving medical findings
"""
import re
import ast
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from config.settings import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    REPORT_COLLECTION,
    FINDINGS_COLLECTION
)


def get_content(metadata: str) -> str:
    """
    Retrieves report content from ChromaDB using report_id
    
    Args:
        metadata: Metadata string or dict containing report_id
        
    Returns:
        Complete report text
    """
    # Extract report_id from metadata string
    pattern = r"'report_id':\s*'([^']+)'"
    match = re.search(pattern, str(metadata))
    
    if not match:
        # Try alternate pattern
        pattern = r'"report_id":\s*"([^"]+)"'
        match = re.search(pattern, str(metadata))
    
    if not match:
        raise ValueError("Could not extract report_id from metadata")
    
    report_id = match.group(1)
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=REPORT_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    results = vector_store.get(
        where={"report_id": report_id},
        include=["documents", "metadatas"]
    )
    
    txt = '\n'.join(results["documents"])
    print(f"Retrieved {len(results['documents'])} chunks for report {report_id}")
    
    return txt


def save_findings(action_input: dict) -> str:
    """
    Saves extracted findings and values to ChromaDB
    
    Args:
        action_input: Dict with 'findings', 'values', and 'metadata'
        
    Returns:
        Success message
    """
    # Parse if string
    if isinstance(action_input, str):
        action_input = ast.literal_eval(action_input)
    
    findings = action_input.get("findings")
    values = action_input.get("values")
    metadata = action_input.get("metadata")
    
    if not metadata:
        raise ValueError("Metadata is required")
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=FINDINGS_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    # Create document with findings
    document = Document(
        page_content=json.dumps(
            {"findings": findings, "values": values},
            ensure_ascii=False
        ),
        metadata=metadata
    )
    
    vector_store.add_documents(documents=[document])
    print(f"Saved findings for report {metadata.get('report_id')}")
    
    return "Findings saved successfully"