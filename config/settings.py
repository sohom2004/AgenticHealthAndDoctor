"""
Configuration settings for the Medical Agentic System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
TEMP_DIR = BASE_DIR / "temp"
CHROMA_DIR = STORAGE_DIR / "chroma"

# Create directories if they don't exist
STORAGE_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model configurations
LLM_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
WHISPER_MODEL = "base"

# ChromaDB collections
REPORT_COLLECTION = "patient-report-collection"
FINDINGS_COLLECTION = "patient-report-findings"

# OCR settings
OCR_LANGUAGES = ['en']
OCR_GPU = True

# Document processing settings
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

# Default patient ID (can be overridden)
DEFAULT_PATIENT_ID = "pt-001"  # Changed for consistency with main.py

# Validate required settings
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")