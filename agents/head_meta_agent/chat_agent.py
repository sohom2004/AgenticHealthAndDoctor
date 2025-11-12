from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.chat_tools import query_findings, get_patient_history
from config.settings import GOOGLE_API_KEY, LLM_MODEL


def create_chat_agent():
    """
    Creates a chat agent with vector query capabilities
    
    Returns:
        LangChain agent
    """
    tools = [
        Tool(
            name="QueryFindings",
            func=query_findings,
            description="Search patient findings using semantic search. Input: query string and patient_id as 'query|patient_id'"
        ),
        Tool(
            name="GetPatientHistory",
            func=get_patient_history,
            description="Get complete patient report history. Input: patient_id as string"
        )
    ]
    
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7
    )
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent


def run_chat(query: str, patient_id: str) -> str:
    """
    Runs the chat agent for general queries
    
    Args:
        query: User query
        patient_id: Patient identifier
        
    Returns:
        Agent response
    """
    agent = create_chat_agent()
    
    prompt = f"""
    You are a helpful medical assistant chatbot. Answer the user's question based on their medical history.
    
    User query: {query}
    Patient ID: {patient_id}
    
    If the query is about:
    - Medical history or past reports: Use GetPatientHistory tool
    - Specific medical findings or values: Use QueryFindings tool
    - General questions: Answer directly using your knowledge
    
    Be conversational, helpful, and empathetic. Always prioritize patient safety.
    """
    
    response = agent.invoke({"input": prompt})
    
    return response.get("output", "I'm sorry, I couldn't process that query.")