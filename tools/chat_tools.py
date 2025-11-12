import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config.settings import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    FINDINGS_COLLECTION,
    REPORT_COLLECTION
)


def query_findings(action_input: str) -> str:
    """
    Performs semantic search on patient findings
    
    Args:
        action_input: Query string in format "query|patient_id"
        
    Returns:
        Relevant findings as formatted string
    """
    try:
        if '|' in action_input:
            query, patient_id = action_input.split('|', 1)
        else:
            query = action_input
            patient_id = "pt-001"
        
        query = query.strip()
        patient_id = patient_id.strip()
        
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vector_store = Chroma(
            collection_name=FINDINGS_COLLECTION,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR)
        )
        
        results = vector_store.similarity_search(
            query,
            k=5,
            filter={"patient_id": patient_id}
        )
        
        if not results:
            return f"No findings found for patient {patient_id} matching query: {query}"
        
        formatted_results = []
        for i, doc in enumerate(results, 1):
            try:
                content = json.loads(doc.page_content)
                findings = content.get("findings", [])
                values = content.get("values", {})
                
                result_text = f"\n--- Result {i} ---\n"
                result_text += f"Report Date: {doc.metadata.get('report_date', 'Unknown')}\n"
                result_text += f"Findings: {', '.join(findings) if findings else 'None'}\n"
                result_text += f"Values: {values}\n"
                
                formatted_results.append(result_text)
            except:
                formatted_results.append(f"\n--- Result {i} ---\n{doc.page_content}\n")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error querying findings: {str(e)}"


def get_patient_history(patient_id: str) -> str:
    """
    Retrieves complete patient history
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        Formatted patient history
    """
    try:
        patient_id = patient_id.strip()
        
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        findings_store = Chroma(
            collection_name=FINDINGS_COLLECTION,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR)
        )
        
        findings_results = findings_store.get(
            where={"patient_id": patient_id},
            include=["documents", "metadatas"]
        )
        
        if not findings_results["documents"]:
            return f"No history found for patient {patient_id}"
        
        history = f"Patient History for {patient_id}\n"
        history += "=" * 60 + "\n\n"
        
        for i, (doc, metadata) in enumerate(zip(
            findings_results["documents"], 
            findings_results["metadatas"]
        ), 1):
            try:
                content = json.loads(doc)
                history += f"Report {i} - {metadata.get('report_date', 'Unknown Date')}\n"
                history += f"Report ID: {metadata.get('report_id', 'Unknown')}\n"
                history += f"Findings: {', '.join(content.get('findings', []))}\n"
                history += f"Values: {content.get('values', {})}\n"
                history += "-" * 60 + "\n\n"
            except:
                history += f"Report {i} - Raw data\n{doc}\n"
                history += "-" * 60 + "\n\n"
        
        return history
        
    except Exception as e:
        return f"Error retrieving patient history: {str(e)}"