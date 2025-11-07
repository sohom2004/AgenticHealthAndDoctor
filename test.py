from agents.search_meta_agent.location_and_search_term import run_search_term_and_location
from tools.search_and_location import get_user_summaries
from agents.search_meta_agent.search_agent import search_doctors
param = {'doctor_type': 'Cardiologist', 'location': {'city': 'Asansol', 'state': 'West Bengal', 'country': 'India'}}
res = search_doctors(param)
print(res)