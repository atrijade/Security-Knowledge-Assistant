# Vulnerability Management RAG Assistant

A modular Retrieval-Augmented Generation (RAG) assistant designed for analyzing cybersecurity and vulnerability management documents (such as DBIR reports, security briefs, and guides). It combines local semantic vector retrieval with Google's Gemini LLM.

The project features a lightweight **FastAPI** backend and a modern **React (Vite)** dashboard with an interactive chat and retrieved-sources sidebar.

---

## Key Features

* 📄 **Multi-Format Ingestion**: Automatically scans and parses both plaintext (`.txt`) and PDF (`.pdf`) documents.
* ⚡ **Incremental Builds**: Uses a hash-based manifest system to skip unchanged files, minimizing indexing times.
* 🧠 **Local Semantic Search**: Generates vector embeddings using the `all-MiniLM-L6-v2` transformer and indexes them in a persistent local **ChromaDB** store.
* 🤖 **Gemini LLM Integration**: Generates natural language answers based solely on retrieved context using the official `google-genai` SDK (`gemini-2.0-flash` or custom models).
* 💻 **Premium Web UI**: Features a beautiful dark-mode React chat console showcasing query inputs, generation status, and retrieved document cards with Euclidean distance metrics.

---

## Directory Structure

```text
├── data/                  # Source security documents (.txt, .pdf)
├── vector_db/              # Persistent ChromaDB store and build manifests
├── frontend/              # React (Vite 5) frontend application
│   ├── src/
│   │   ├── App.jsx        # Chat and Sidebar UI layout
│   │   ├── App.css        # Premium UI styles
│   │   └── index.css      # Core HSL design tokens & animations
│   └── index.html         # HTML template
├── src/                   # Python modular source code
│   ├── chunking/          # Document splitters
│   ├── embeddings/        # Embedding model interfaces
│   ├── loaders/           # Custom PDF and TXT loaders
│   ├── retrieval/         # Retrieval orchestrator
│   ├── vectordb/          # ChromaDB integration wrapper
│   └── llm/               # Gemini client and context builder
├── app.py                 # FastAPI backend entrypoint
├── ingest.py              # CLI script to parse & index documents
├── query.py               # CLI script to test queries in the terminal
├── config.py              # Environment settings manager
├── .env                   # Local configuration variables
└── requirements.txt       # Python package dependencies
```

---

## Setup & Installation

### 1. Backend Setup
1. Create a Python virtual environment (e.g., Python 3.10+):
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate    # macOS/Linux
   ```
2. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory (based on `.env.example`):
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   RAG_LLM_MODEL=gemini-2.0-flash
   ```

> [!IMPORTANT]
> **API Key Setup**: Ensure you generate your Gemini API key in **Google AI Studio** by clicking **"Create API key"** ➔ **"Create API key in new project"** to ensure your key has active free tier quota.

---

## Usage Instructions

### Command Line Interface (CLI)

#### 1. Ingest Documents
Put your `.txt` and `.pdf` documents in the `data/` folder, then run:
```bash
python ingest.py
```

#### 2. Run Terminal Queries
To test retrieval and LLM answering directly in your command line:
```bash
python query.py --question "What is SQL Injection?"
```

---

### Running the Web Application

To launch the full web interface, run the backend and frontend servers in separate terminal sessions:

#### 1. Start the Backend API (FastAPI)
```bash
uvicorn app:app --port 8080 --reload
```
The API documentation will be available at [http://localhost:8080/docs](http://localhost:8080/docs).

#### 2. Start the Frontend Dev Server (React)
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your web browser to start asking questions!
