"""
Node functions for LangGraph workflow
"""
from graph.state import AgentState
from agents.head_meta_agent.head_agent import process_input, save_document
from agents.clinical_meta_agent.clinical_agent import extract_findings, summarize_report


def input_node(state: AgentState) -> AgentState:
    """
    Initial node: Processes input through Head Meta Agent
    """
    return process_input(state)


def document_save_node(state: AgentState) -> AgentState:
    """
    Saves document to ChromaDB
    """
    return save_document(state)


def extraction_node(state: AgentState) -> AgentState:
    """
    Extracts findings through Clinical Meta Agent
    """
    return extract_findings(state)


def summarization_node(state: AgentState) -> AgentState:
    """
    Generates summary through Clinical Meta Agent
    """
    return summarize_report(state)


def error_node(state: AgentState) -> AgentState:
    """
    Handles errors
    """
    error_msg = state.get("error", "Unknown error occurred")
    state["final_response"] = f"ERROR: {error_msg}"
    state["next_step"] = "end"
    return state


def route_next_step(state: AgentState) -> str:
    """
    Routes to the next node based on state
    """
    next_step = state.get("next_step", "end")
    return next_step