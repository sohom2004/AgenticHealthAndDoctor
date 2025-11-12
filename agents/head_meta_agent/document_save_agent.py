from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.document_tools import store_content
from config.settings import GOOGLE_API_KEY, LLM_MODEL


def create_document_save_agent():
    """
    Creates a document save agent for storing content in ChromaDB
    
    Returns:
        LangChain agent
    """
    tools = [
        Tool(
            name="StoreContent",
            func=store_content,
            description="Stores input dict into ChromaDB with metadata. Returns metadata"
        )
    ]
    
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY
    )
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent


def run_document_save(text_data: dict, patient_id: str) -> dict:
    """
    Runs the document save agent to store content
    
    Args:
        text_data: Dictionary with 'content' and 'confidence'
        patient_id: Patient identifier
        
    Returns:
        Metadata dictionary
    """
    from tools.document_tools import store_content
    content = text_data.get("content", "")
    
    return store_content(content, patient_id=patient_id)