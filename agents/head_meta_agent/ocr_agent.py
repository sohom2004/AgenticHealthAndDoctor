"""
OCR Agent for extracting text from documents
"""
from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.ocr_tools import get_file_type, convert_to_jpg, get_ocr
from config.settings import GOOGLE_API_KEY, LLM_MODEL


def create_ocr_agent():
    """
    Creates an OCR agent with file type detection, PDF conversion, and OCR tools
    
    Returns:
        LangChain agent
    """
    tools = [
        Tool(
            name="FileTypeDetector",
            func=get_file_type,
            description="Detects if a given file path is a PDF or an image. Input: file path (string)."
        ),
        Tool(
            name="PDFtoImage",
            func=convert_to_jpg,
            description="Converts PDF into a list of image paths. Input: file path (string)."
        ),
        Tool(
            name="OCRTool",
            func=get_ocr,
            description="Runs OCR on a list of image paths. Input: list of image paths."
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


def run_ocr_extraction(file_path: str) -> dict:
    """
    Runs the OCR agent on a file
    
    Args:
        file_path: Path to file (PDF or image)
        
    Returns:
        Dictionary with 'content' and 'confidence'
    """
    agent = create_ocr_agent()
    
    prompt = f"""
    You are an OCR extraction assistant.
    Steps you MUST follow:
    1. Detect file type using FileTypeDetector.
    2. If PDF, convert to images using PDFtoImage.
    3. Run OCRTool on the image paths.
    4. Return the content and confidence from the OCRTool.
    File: {file_path}
    """
    
    response = agent.invoke({"input": prompt})
    
    # Extract the result from the response
    output = response.get("output", "")
    
    # Parse output to extract content and confidence
    # The agent should return a dict-like string
    try:
        import ast
        result = ast.literal_eval(output)
        return result
    except:
        # Fallback: return as is
        return {"content": output, "confidence": 0.0}