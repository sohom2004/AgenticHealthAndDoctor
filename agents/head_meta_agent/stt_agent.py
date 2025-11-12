from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.stt_tools import transcribe
from config.settings import GOOGLE_API_KEY, LLM_MODEL


def create_stt_agent():
    """
    Creates an STT agent with transcription capability
    
    Returns:
        LangChain agent
    """
    tools = [
        Tool(
            name="SpeechToText",
            func=transcribe,
            description="Transcribes audio into text. Input: file path (string)"
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


def run_stt_extraction(file_path: str) -> str:
    """
    Runs the STT agent on an audio file
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Transcribed text
    """
    agent = create_stt_agent()
    
    prompt = f"""
    You are a text extraction agent. You will perform text transcription on the audio file and return the text content.
    File: {file_path}
    """
    
    response = agent.invoke({"input": prompt})
    
    output = response.get("output", "")
    
    return output