"""
Configuration module for the Medical Agentic System
"""
from config.settings import *

"""
Tools module containing utility functions for agents
"""
from tools.ocr_tools import get_file_type, convert_to_jpg, get_ocr, cleanup_temp_files
from tools.stt_tools import transcribe
from tools.document_tools import store_content, extract_report_data, get_next_report_id
from tools.extraction_tools import get_content, save_findings
from tools.summarizer_tools import get_all_findings, get_recent_findings
from tools.chat_tools import query_findings, get_patient_history

"""
Agents module containing all agent implementations
"""

"""
Head Meta Agent module
"""
from agents.head_meta_agent.ocr_agent import create_ocr_agent, run_ocr_extraction
from agents.head_meta_agent.stt_agent import create_stt_agent, run_stt_extraction
from agents.head_meta_agent.document_save_agent import create_document_save_agent, run_document_save
from agents.head_meta_agent.chat_agent import create_chat_agent, run_chat
from agents.head_meta_agent.head_agent import process_input, save_document

"""
Clinical Meta Agent module
"""
from agents.clinical_meta_agent.extraction_agent import create_extraction_agent, run_extraction
from agents.clinical_meta_agent.summarizer_agent import create_summarizer_agent, run_summarization
from agents.clinical_meta_agent.clinical_agent import extract_findings, summarize_report

"""
Graph module containing LangGraph workflow definitions
"""
from graph.state import AgentState
from graph.nodes import (
    input_node,
    document_save_node,
    extraction_node,
    summarization_node,
    error_node,
    route_next_step
)
from graph.workflow import create_workflow, run_workflow

"""
Storage module for ChromaDB
"""