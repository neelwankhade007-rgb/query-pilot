# Query Pilot 🛸

Natural language data intelligence engine powered by **DuckDB** and a local **Ollama LLM** (`qwen2.5:3b`). 

Upload tabular datasets (CSV, JSON, Excel) and ask questions in plain English. Query Pilot dynamically analyzes schema context, synthesizes SQL, safely executes it with DuckDB in-memory, and provides both natural-language answers and interactive tabular results.

---

## Architecture & Flow

```text
User Question (Natural Language)
               ↓
    1. Schema Context Builder (Inspects column types, values, samples)
               ↓
    2. Ollama SQL Synthesis (Generates DuckDB-dialect SQL via qwen2.5:3b)
               ↓
    3. SQL Validator (Blocks dangerous DDL/DML, enforces safe read-only queries)
               ↓
    4. DuckDB In-Memory Execution (Fast columnar query execution)
               ↓
    5. Ollama Result Interpreter (Interprets raw result into executive summary)
               ↓
    Response (Natural Language Answer + Generated SQL + Data Table)
```

---

## Key Features

- **No Server Database Required**: Query execution runs in-memory via DuckDB.
- **SQLite Persistence**: Uploaded datasets are cataloged in `metadata.db` and automatically re-registered into DuckDB on startup.
- **Local Privacy**: Runs 100% locally with Ollama (`qwen2.5:3b`); no third-party APIs or cloud subscriptions needed.
- **Security Hardened**:
  - File upload size cap (100 MB).
  - Path traversal and filename sanitization with UUID collision avoidance.
  - SQL validation ensuring only read-only `SELECT` statements are executed.
- **Modern Web Interface**: Built-in responsive dark-mode UI with drag-and-drop upload, schema exploration, progress tracking, and tabular results.

---

## Prerequisites

1. **Python 3.10+**
2. **Ollama** installed and running locally:
   - Install from [ollama.com](https://ollama.com)
   - Pull the required model:
     ```bash
     ollama pull qwen2.5:3b
     ```
   - Ensure Ollama is running (`http://localhost:11434`).

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/neelwankhade007-rgb/query-pilot.git
cd query-pilot
```

### 2. Create and activate a virtual environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

---

## Running the Application

Start the FastAPI server from the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

The application will be accessible at:
- **Web UI**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the Query Pilot frontend UI |
| `POST` | `/upload` | Upload a dataset (`.csv`, `.json`, `.xlsx`, `.xls`) |
| `GET` | `/datasets` | List all persisted datasets |
| `GET` | `/datasets/{dataset_id}` | Fetch dataset metadata and schema details |
| `DELETE` | `/datasets/{dataset_id}` | Delete a dataset, its file, and metadata |
| `POST` | `/datasets/{dataset_id}/ask` | Full natural-language query pipeline (NL → SQL → Exec → Answer) |
| `POST` | `/datasets/{dataset_id}/generate-sql` | Generate SQL from a natural-language question |
| `POST` | `/datasets/{dataset_id}/query` | Directly execute a validated SQL query in DuckDB |

---

## Running Tests

From the `backend/` directory with the virtual environment activated:

```bash
# Test SQL Validator (valid SELECT queries vs dangerous statements)
python test_validator.py

# Test Ollama connection & LLM generation
python test_ollama.py

# Test SQLite persistence & reload lifecycle
python test_persistence.py

# Test upload hardening (file limits, filename sanitization, deletion)
python test_hardening.py

# Test end-to-end /ask pipeline
python test_ask.py
```

---

## Tech Stack

- **Backend**: FastAPI, DuckDB, Pandas, SQLite, Uvicorn
- **AI / LLM**: Ollama (`qwen2.5:3b`)
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism / Dark Mode), Modern JavaScript (Fetch API)
