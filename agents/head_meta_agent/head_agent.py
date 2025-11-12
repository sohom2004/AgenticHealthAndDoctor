from agents.head_meta_agent.ocr_agent import run_ocr_extraction
from agents.head_meta_agent.stt_agent import run_stt_extraction
from agents.head_meta_agent.document_save_agent import run_document_save
from agents.head_meta_agent.chat_agent import run_chat
from graph.state import AgentState


def determine_intent(text_input: str) -> str:
    """
    Determines if text input is a report or a conversational query
    
    Args:
        text_input: User's text input
        
    Returns:
        "report" or "chat"
    """
    report_keywords = [
        "blood test", "lab result", "scan", "x-ray", "mri", 
        "diagnosis", "prescription", "medical report", "test result"
    ]
    
    chat_keywords = [
        "what is", "how is", "tell me", "explain", "show me",
        "history", "previous", "compare", "?", "when", "why"
    ]
    
    text_lower = text_input.lower()
    
    has_chat_keywords = any(keyword in text_lower for keyword in chat_keywords)
    has_report_keywords = any(keyword in text_lower for keyword in report_keywords)
    
    if "?" in text_input or has_chat_keywords and not has_report_keywords:
        return "chat"
    
    if has_report_keywords or len(text_input.split()) > 50:
        return "report"
    
    return "chat"


def process_input(state: AgentState) -> AgentState:
    """
    Head Meta Agent: Processes input based on type
    Routes to OCR, STT, Chat, or uses text directly
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with extracted text or chat response
    """
    print("\n=== HEAD META AGENT: Processing Input ===")
    
    input_type = state.get("input_type")
    file_path = state.get("file_path")
    text_input = state.get("text_input")
    
    try:
        if input_type in ["pdf", "image"]:
            print(f"Processing {input_type} file: {file_path}")
            result = run_ocr_extraction(file_path)
            state["extracted_text"] = result.get("content", "")
            state["confidence"] = result.get("confidence", 0.0)
            state["next_step"] = "save_document"
            
        elif input_type == "audio":
            print(f"Processing audio file: {file_path}")
            transcribed_text = run_stt_extraction(file_path)
            state["extracted_text"] = transcribed_text
            state["confidence"] = 1.0
            state["next_step"] = "save_document"
            
        elif input_type == "text":
            intent = determine_intent(text_input)
            
            if intent == "chat":
                print("Processing as conversational query")
                patient_id = state.get("patient_id", "pt-001")
                chat_response = run_chat(text_input, patient_id)
                state["final_response"] = chat_response
                state["next_step"] = "end"
            else:
                print("Processing as medical report text")
                state["extracted_text"] = text_input
                state["confidence"] = 1.0
                state["next_step"] = "save_document"
            
        else:
            raise ValueError(f"Unknown input type: {input_type}")
        
    except Exception as e:
        print(f"Error in Head Meta Agent: {e}")
        state["error"] = str(e)
        state["next_step"] = "error"
    
    return state


def save_document(state: AgentState) -> AgentState:
    """
    Saves the extracted document to ChromaDB
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with metadata
    """
    print("\n=== HEAD META AGENT: Saving Document ===")
    
    try:
        text_data = {
            "content": state.get("extracted_text", ""),
            "confidence": state.get("confidence", 0.0)
        }
        
        patient_id = state.get("patient_id", "pt-1")
        
        metadata = run_document_save(text_data, patient_id)
        state["report_metadata"] = metadata
        
        print(f"Document saved with metadata: {metadata}")
        state["next_step"] = "extract_findings"
        
    except Exception as e:
        print(f"Error saving document: {e}")
        state["error"] = str(e)
        state["next_step"] = "error"
    
    return state