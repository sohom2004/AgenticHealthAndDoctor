"""
Extraction Agent for extracting medical findings and values
"""
from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.extraction_tools import get_content, save_findings
from config.settings import GOOGLE_API_KEY, LLM_MODEL


def create_extraction_agent():
    """
    Creates an extraction agent for extracting medical findings
    
    Returns:
        LangChain agent
    """
    tools = [
        Tool(
            name="getContent",
            func=get_content,
            description="Fetch and return all report page contents as a string. Input: Metadata"
        ),
        Tool(
            name="saveFindings",
            func=save_findings,
            description="Save extracted findings and metadata. Input must be a dict with keys 'findings', 'values', and 'metadata'."
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


def run_extraction(metadata: dict) -> dict:
    """
    Runs the extraction agent to extract findings from a report
    
    Args:
        metadata: Report metadata containing report_id
        
    Returns:
        Dictionary with 'findings' and 'values'
    """
    agent = create_extraction_agent()
    
    prompt = f"""
    You are an information extraction agent. You will perform the following tasks:
    1. Pass the entire metadata to the getContent tool and get the complete report text.
    2. Analyse the report text and look for important information
    3. Return the output in strictly the following way:
    {{findings: list of only the important details from the text about the patient's condition
    values: key value pairs of critical data with their mentioned values}}
    4. Once the output is extracted, save it using the saveFindings by passing the output and the metadata strictly inside a dict to the saveFindings Tool.
    metadata: {metadata}
    """
    
    response = agent.invoke({"input": prompt})
    
    output = response.get("output", "")
    
    try:
        import ast
        result = ast.literal_eval(output)
        return result
    except:
        return {"findings": [], "values": {}}