"""
Search Meta Agent - Orchestrates Location/Search Term and Doctor Search agents
"""
from agents.search_meta_agent.location_and_search_term import run_search_term_and_location
from agents.search_meta_agent.search_agent import search_doctors
from graph.state import AgentState
import json


def get_search_parameters(state: AgentState) -> AgentState:
    """
    Search Meta Agent: Gets doctor type and location based on user's medical summary
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with doctor_type and location
    """
    print("\n=== SEARCH META AGENT: Getting Search Parameters ===")
    
    try:
        patient_id = state.get("patient_id")
        
        if not patient_id:
            raise ValueError("No patient_id found in state")
        
        result = run_search_term_and_location(patient_id)
        
        doctor_type = result.get("doctor_type", "Unknown")
        location = result.get("location", {})  
        
        if doctor_type == "Unknown" or doctor_type == "Unable to determine":
            raise ValueError("Could not determine appropriate doctor specialization")
        
        state["doctor_type"] = doctor_type
        state["location"] = location  
        state["search_params"] = result 
        
        print(f"✅ Search parameters determined:")
        print(f"   Doctor Type: {doctor_type}")
        print(f"   Location: {location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}")

        print("debug lines")
        print(f"state['location']: {state['location']}")
        print(f"state['doctor_type']: {state['doctor_type']}")
        print(f"state['search_params']: {state['search_params']}")
        
        state["next_step"] = "search_doctors"
        
    except Exception as e:
        print(f"❌ Error getting search parameters: {e}")
        state["error"] = str(e)
        state["next_step"] = "error"
    
    return state


def find_doctors(state: AgentState) -> AgentState:
    """
    Search Meta Agent: Searches for doctors based on determined parameters
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with doctor search results
    """
    print("\n=== SEARCH META AGENT: Finding Doctors ===")
    
    try:
        search_params = state.get("search_params")
        
        print(f"DEBUG: search_params from state: {search_params}")
        
        if not search_params:
            
            doctor_type = state.get("doctor_type")
            location = state.get("location")
            
            if doctor_type and location:
                search_params = {
                    "doctor_type": doctor_type,
                    "location": location
                }
                print(f"DEBUG: Reconstructed search_params: {search_params}")
            else:
                raise ValueError("No search parameters found in state and cannot reconstruct")
        
        doctor_type = search_params.get("doctor_type")
        location = search_params.get("location", {})
        
        if not doctor_type or not location:
            raise ValueError("Missing doctor_type or location in search parameters")
        
        print(f"🔍 Searching for {doctor_type} in {location.get('city', 'Unknown')}...")
        
        search_results = search_doctors(search_params, top_n=5)
        
        if isinstance(search_results, str):
            try:
                if '```json' in search_results:
                    search_results = search_results.split('```json')[1].split('```')[0].strip()
                elif '```' in search_results:
                    parts = search_results.split('```')
                    for part in parts:
                        if '{' in part and '}' in part:
                            search_results = part.strip()
                            break
                
                search_results = json.loads(search_results)
            except json.JSONDecodeError as e:
                print(f"⚠️ Warning: Could not parse search results as JSON: {e}")
                state["raw_search_output"] = search_results
        
        if isinstance(search_results, dict) and "error" in search_results:
            raise ValueError(f"Search failed: {search_results['error']}")
        
        state["search_results"] = search_results
        
        if isinstance(search_results, dict):
            top_results = search_results.get("top_results", [])
            total_results = search_results.get("total_results", 0)
        else:
            top_results = []
            total_results = 0
        
        state["top_doctors"] = top_results
        state["total_results"] = total_results
        
        print(f"✅ Found {total_results} doctors, returning top {len(top_results)}")
        
        final_response = format_search_results(
            doctor_type=doctor_type,
            location=location,
            top_results=top_results,
            total_results=total_results
        )
        
        state["final_response"] = final_response
        state["next_step"] = "end"
        
    except Exception as e:
        print(f"❌ Error searching for doctors: {e}")
        import traceback
        traceback.print_exc()
        state["error"] = str(e)
        state["next_step"] = "error"
    
    return state


def format_search_results(doctor_type: str, location: dict, top_results: list, total_results: int) -> str:
    """
    Formats search results into a readable string
    
    Args:
        doctor_type: Type of doctor searched
        location: Location dictionary
        top_results: List of top doctor results
        total_results: Total number of results found
        
    Returns:
        Formatted string with search results
    """
    city = location.get('city', 'Unknown')
    state = location.get('state', 'Unknown')
    country = location.get('country', 'Unknown')
    
    response = f"""
DOCTOR SEARCH RESULTS
{'='*50}

Search Query: {doctor_type} in {city}, {state}, {country}
Total Results Found: {total_results}
Top {len(top_results)} Recommendations:

"""
    
    if not top_results:
        response += "No doctors found matching your criteria.\n"
    else:
        for idx, doctor in enumerate(top_results, 1):
            name = doctor.get('name', 'N/A')
            address = doctor.get('address', 'N/A')
            phone = doctor.get('phone', 'N/A')
            rating = doctor.get('rating', 'N/A')
            reviews = doctor.get('reviews', 'N/A')
            score = doctor.get('score', 0)
            
            response += f"""
{idx}. {name}
   Address: {address}
   Phone: {phone}
   Rating: {rating} ⭐ ({reviews} reviews)
   Ranking Score: {score:.2f}
   {'-'*50}
"""
    
    return response


def handle_search_error(state: AgentState) -> AgentState:
    """
    Handles errors in the search meta agent workflow
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with error message
    """
    print("\n=== SEARCH META AGENT: Handling Error ===")
    
    error_message = state.get("error", "Unknown error occurred")
    
    final_response = f"""
DOCTOR SEARCH ERROR
{'='*50}

An error occurred during the doctor search process:
{error_message}

Please try again or contact support if the issue persists.
"""
    
    state["final_response"] = final_response
    state["next_step"] = "end"
    
    return state