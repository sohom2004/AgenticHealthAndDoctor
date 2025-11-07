"""
Configuration settings for the Medical Agentic System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
TEMP_DIR = BASE_DIR / "temp"
CHROMA_DIR = STORAGE_DIR / "chroma"

STORAGE_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
IPGEOLOCATION_API_KEY = os.getenv("IPGEOLOCATION_API_KEY")

LLM_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
WHISPER_MODEL = "base"

REPORT_COLLECTION = "patient-report-collection"
FINDINGS_COLLECTION = "patient-report-findings"
SUMMARY_COLLECTION = "patient-report-summaries"

OCR_LANGUAGES = ['en']
OCR_GPU = True

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

DEFAULT_PATIENT_ID = "pt-001"

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")