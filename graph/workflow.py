"""
LangGraph workflow definition for the Medical Agentic System
"""
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import (
    input_node,
    document_save_node,
    extraction_node,
    summarization_node,
    error_node,
    route_next_step
)


def create_workflow():
    """
    Creates the LangGraph workflow for the medical agentic system
    
    Returns:
        Compiled LangGraph workflow
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("input_processing", input_node)
    workflow.add_node("save_document", document_save_node)
    workflow.add_node("extract_findings", extraction_node)
    workflow.add_node("summarize", summarization_node)
    workflow.add_node("error", error_node)
    
    # Set entry point
    workflow.set_entry_point("input_processing")
    
    # Add conditional edges from input_processing
    workflow.add_conditional_edges(
        "input_processing",
        route_next_step,
        {
            "save_document": "save_document",
            "error": "error",
            "end": END
        }
    )
    
    # Add conditional edges from save_document
    workflow.add_conditional_edges(
        "save_document",
        route_next_step,
        {
            "extract_findings": "extract_findings",
            "error": "error",
            "end": END
        }
    )
    
    # Add conditional edges from extract_findings
    workflow.add_conditional_edges(
        "extract_findings",
        route_next_step,
        {
            "summarize": "summarize",
            "error": "error",
            "end": END
        }
    )
    
    # Add conditional edges from summarize
    workflow.add_conditional_edges(
        "summarize",
        route_next_step,
        {
            "end": END,
            "error": "error"
        }
    )
    
    # Error node always goes to END
    workflow.add_edge("error", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def run_workflow(
    input_type: str,
    file_path: str = None,
    text_input: str = None,
    patient_id: str = "pt-001"  # Changed default for consistency
) -> dict:
    """
    Runs the complete workflow
    
    Args:
        input_type: Type of input ("pdf", "image", "audio", "text")
        file_path: Path to file (for pdf, image, audio)
        text_input: Text input (for text type)
        patient_id: Patient identifier
        
    Returns:
        Final state dictionary
    """
    # Create initial state
    initial_state = {
        "input_type": input_type,
        "file_path": file_path,
        "text_input": text_input,
        "patient_id": patient_id,
        "extracted_text": None,
        "confidence": None,
        "report_metadata": None,
        "findings": None,
        "values": None,
        "summary": None,
        "key_changes": None,
        "current_values": None,
        "final_response": None,
        "error": None,
        "next_step": None
    }
    
    # Create and run workflow
    app = create_workflow()
    result = app.invoke(initial_state)
    
    return result