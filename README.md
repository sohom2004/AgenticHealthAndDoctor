# 🏥 Agentic Health & Doctor System

A sophisticated AI-powered medical assistant built using **LangGraph**, **LangChain**, and **Google Gemini**. This system acts as an autonomous agent that can ingest medical reports (PDF, Images, Audio), extract clinical findings, maintain patient history via a vector database, and intelligently search for relevant medical specialists using Google Maps.

## ✨ Features

  * **Multi-Modal Input Processing:**
      * **📄 Documents:** OCR support for PDFs and Images (JPG, PNG) using `EasyOCR` and `pdf2image`.
      * **🎙️ Audio:** Transcription of voice notes or medical dictations using `OpenAI Whisper`.
      * **💬 Text:** Direct conversational interface for queries and symptoms.
  * **Agentic Workflow (LangGraph):**
      * **Head Agent:** Orchestrates intent detection and routing.
      * **Clinical Meta Agent:** Extracts specific medical findings and generates clinical summaries.
      * **Search Meta Agent:** Determines the necessary doctor specialization based on the analysis.
  * **RAG (Retrieval Augmented Generation):** Stores patient history and medical findings in **ChromaDB** for context-aware Q\&A.
  * **Automated Doctor Search:** Scrapes and ranks real-world doctors from Google Maps based on location and specialization using **Selenium**.
  * **Continuous CLI:** A terminal-based interface for continuous interaction.

-----

## 🛠️ Architecture

The system is designed as a graph of specialized agents:

1.  **Input Node:** Accepts file paths or text.
2.  **Head Meta Agent:** Routes to OCR, STT, or Chat workflows.
3.  **Document Save Node:** Vectors and stores raw content in ChromaDB.
4.  **Extraction Node:** Extracts structured `findings` and `values` (e.g., "Blood Pressure: 120/80").
5.  **Summarization Node:** Generates a patient status summary and compares it with history.
6.  **Search Workflow:** If requested, infers the required specialist (e.g., "Cardiologist") and scrapes Google Maps for top-rated local doctors.

-----

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

  * **Python 3.9+**
  * **Poppler:** Required for `pdf2image` to process PDFs.
      * *Windows:* Download binary and add to PATH.
      * *Mac:* `brew install poppler`
      * *Linux:* `sudo apt-get install poppler-utils`
  * **Google Chrome:** Required for Selenium web scraping.
  * **FFmpeg:** Required for OpenAI Whisper audio processing.

-----

## ⚙️ Installation

1.  **Clone the Repository**

    ```bash
    git clone <repository-url>
    cd AgenticHealthAndDoctor
    ```

2.  **Create a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

    *Note: Ensure you have `selenium` installed if it is not in the core requirements.*

-----

## 🔑 Configuration

Create a `.env` file in the root directory and add your API keys:

```env
# Google Gemini API Key (Required for LLM)
GOOGLE_API_KEY=your_google_gemini_api_key

# IP Geolocation API Key (Required for location detection)
# Get one at https://ipgeolocation.io/
IPGEOLOCATION_API_KEY=your_ipgeolocation_api_key
```

-----

## 🚀 How to Run

The system interacts through a continuous terminal interface.

### 1\. Start the Application

Run the main entry point:

```bash
python main.py
```

### 2\. Interactive Commands

Once the system is running, you will see a prompt like `[pt-001] >`. You can use the following commands:

#### **A. Process Medical Files**

Upload reports, scans, or audio notes.

```bash
# Process a PDF Report
--file /path/to/blood_report.pdf

# Process an Image Scan
--file /path/to/xray_scan.jpg

# Process an Audio Note
--file /path/to/doctor_voice_note.mp3
```

#### **B. Chat & Query History**

Ask questions about the patient's medical history or current status.

```bash
# Ask specific questions
--text "What is my cholesterol level based on the last report?"

# Ask for a summary
--text "Give me a summary of my condition."
```

#### **C. Find Doctors**

The agent analyzes your uploaded reports to decide what kind of doctor you need, detects your location, and finds top-rated specialists.

```bash
# Initiate search
--search

# Or use natural language
find me a doctor
```

#### **D. Manage Patients**

Switch between different patient profiles (data is stored separately in the vector DB).

```bash
# Switch patient context
--patient pt-002
```

#### **E. Help & Exit**

```bash
--help   # Show available commands
exit     # Close the application
```

-----

## 📂 Project Structure

```text
AgenticHealthAndDoctor/
├── agents/                 # specialized agents
│   ├── clinical_meta_agent/  # Extraction & Summarization
│   ├── head_meta_agent/      # OCR, STT, Chat, Routing
│   └── search_meta_agent/    # Location & Doctor Search
├── config/                 # Configuration & Settings
├── graph/                  # LangGraph State & Node definitions
├── storage/                # ChromaDB storage (created on runtime)
├── tools/                  # Atomic tools (OCR, Search, DB ops)
├── main.py                 # Entry point (CLI)
└── requirements.txt        # Python dependencies
```

## ⚠️ Troubleshooting

  * **Selenium Errors:** Ensure your Google Chrome version matches the installed `selenium` driver behavior. The tool uses standard Chrome options for scraping.
  * **Poppler not found:** If PDF conversion fails, verify `poppler` is installed and added to your system's PATH.
  * **ChromaDB Errors:** Ensure you have the necessary system libraries for SQLite if you encounter database errors.
