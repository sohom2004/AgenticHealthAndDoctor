from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.search import scrape_google_maps, perform_ranking
import os
from dotenv import load_dotenv
import json
import traceback

load_dotenv()


def scraper_wrapper(input_str: str):
    """
    Wrapper function for LangChain tool.
    Input format: "doc_type, location"
    """
    try:
        parts = [part.strip() for part in input_str.split(',')]
        if len(parts) != 2:
            return json.dumps({
                "error": "Invalid input format. Expected: 'doc_type, location'. Example: 'cardiologist, kolkata'"
            })
        
        doc_type, location = parts
        results = scrape_google_maps(doc_type, location)

        ranked = perform_ranking(results)
        top_results = ranked[:5]

        response = {
            "searched_for": doc_type,
            "location": location,
            "total_results": len(results),
            "top_results": top_results
        }

        return json.dumps(response, ensure_ascii=False)
    
    except Exception as e:
        traceback.print_exc()
        return json.dumps({"error": str(e)})

def create_search_agent():
    """Initialize the LangChain agent with Google Gemini"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )

    tools = [
        Tool(
            name="GoogleMapsDoctorScraper",
            func=scraper_wrapper,
            description=(
                "Scrapes and ranks doctor or hospital data from Google Maps. "
                "Input format: 'doc_type, location' (comma separated). "
                "Example: 'cardiologist, kolkata' or 'dentist, mumbai'. "
                "Returns a JSON string containing the top 5 ranked doctors with name, address, phone, rating, reviews, and score."
            )
        )
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )

    return agent


def search_doctors(search_params: str, top_n: int = 5):
    """
    Searches for doctors using LangChain Agent (with ranking).
    """
    doc_type = search_params.get('doctor_type', '')
    location_data = search_params.get('location', {})
    location = location_data.get('city', '')
    if not doc_type or not location:
            return {
                "error": "Missing required fields: doctor_type or location",
                "received": search_params
            }
        
    print(f"🔍 Searching for {doc_type} in {location}...")
    agent = create_search_agent()

    prompt = f"""
Use the GoogleMapsDoctorScraper tool to find {doc_type} in {location}.

IMPORTANT: The tool input must be in this format: "{doc_type}, {location}"

After getting the results:
1. Parse the JSON response.
2. Return only the top {top_n} results (already ranked).
3. Return the data in JSON format.
    """

    response = agent.invoke({"input": prompt})
    output = response.get("output", "")
    return output
