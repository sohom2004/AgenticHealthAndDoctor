import requests
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from config.settings import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    SUMMARY_COLLECTION
)

def get_user_location(api_key):
    try:
        ip_response = requests.get("https://api.ipify.org?format=json")
        ip_response.raise_for_status()
        ip = ip_response.json().get("ip")

        geo_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={ip}"
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        data = geo_response.json()

        location_info = {
            "ip": ip,
            "city": data.get("city"),
            "state_prov": data.get("state_prov"),
            "country": data.get("country_name"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude")
        }

        return location_info

    except Exception as e:
        print("Error fetching location:", e)
        return None


def get_user_summaries(user_id: str):
    print("user_id: " + user_id)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_store = Chroma(
        collection_name=SUMMARY_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    results = vector_store.get(
        where={"user_id": user_id},
        include=["metadatas", "documents"]
    )
    if not results or not results.get('documents') or len(results['documents']) == 0:
        print(f"❌ No summaries found for user {user_id}")
        return None
    documents_with_metadata = list(zip(
        results['documents'],
        results['metadatas']
    ))
    sorted_results = sorted(
        documents_with_metadata,
        key=lambda x: x[1].get('timestamp', ''),
        reverse=True
    )
    most_recent_summary = sorted_results[0][0]
    return most_recent_summary