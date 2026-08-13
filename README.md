# QueryPilot 🚀

> **Natural Language to SQL Assistant** powered by FastAPI, PostgreSQL, SQLGlot validation, and a local LLM via Ollama.

QueryPilot enables users to query SQL databases using plain English. It inspects the database schema dynamically, generates safe read-only SQL queries using a local LLM, validates query syntax and table references, executes queries against PostgreSQL, and formats the output.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **SQL Security & Parsing:** SQLGlot
- **LLM Runtime:** Ollama (`qwen2.5-coder:7b`)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript

---

## ⚡ Quick Start & Installation

### 1. Prerequisites

Ensure you have the following installed on your machine:
- **Python 3.10+**
- **PostgreSQL**
- **Ollama** ([https://ollama.com](https://ollama.com))

### 2. Ollama Setup

Start Ollama and pull the recommended coding model:
```bash
ollama pull qwen2.5-coder:7b
```

### 3. Database Setup

1. Create a PostgreSQL database (e.g., `querypilot`).
2. Run the provided schema and seed SQL scripts:
```bash
psql -U postgres -d querypilot -f sql/schema.sql
psql -U postgres -d querypilot -f sql/seed.sql
```

### 4. Backend Setup

1. Navigate to the `backend` directory:
```bash
cd backend
```
2. Create and activate a Python virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Create a `.env` file in the `backend/` root directory:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/querypilot
```
5. Run the FastAPI development server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. API documentation can be accessed at `http://127.0.0.1:8000/docs`.

### 5. Frontend Setup

Open `frontend/index.html` directly in your browser, or serve it using any HTTP server:
```bash
# Example using Python http.server
cd frontend
python -m http.server 3000
```

---

## 📋 Feature Roadmap & Implementation Status

Below is the roadmap tracking implemented core features versus components that are currently sample/mock code or planned for future development:

### Core Engine & Backend
- [x] **PostgreSQL Database Schema & Seed Data:** Sample e-commerce tables (`customers`, `products`, `orders`).
- [x] **Schema Introspection:** Dynamic schema metadata extraction via SQLAlchemy (`GET /schema`).
- [x] **Local LLM Integration:** SQL generation using Ollama (`qwen2.5-coder:7b`).
- [x] **SQL Safety Layer:** Query parsing & validation using `sqlglot` (restricts execution to single, read-only `SELECT` queries on known schema tables).
- [x] **Query Execution Pipeline:** Safe SQL execution returning structured column & row results (`POST /query`).
- [ ] **Structured LLM Output:** Return JSON containing generated SQL, plain English explanations, and referenced tables.
- [ ] **SQL Auto-Correction Loop:** Self-correcting loop when query execution or validation fails.

### Frontend & UI
- [x] **UI Mockup Layout:** Static dashboard interface with search bar, table layout, and stats widgets (`index.html`, `styles.css`, `script.js`).
- [ ] **API Connection:** Fully wire up frontend form submit to the backend `POST /query` endpoint.
- [ ] **Data Visualization:** Support dynamic charts & graph views for query results (e.g. Chart.js / Recharts).

### Advanced Features (Planned)
- [ ] **Conversational History:** Support multi-turn questions and follow-ups.
- [ ] **Schema Vector Search:** Embedding & RAG for large, complex database schemas.
- [ ] **Containerization:** One-command setup via Docker & `docker-compose`.

---

## 🧪 Testing the API

Once the backend is running, you can test the primary text-to-SQL endpoint via `curl` or Postman:

```bash
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "Which customers bought a Laptop?"}'
```

Sample Response:
```json
{
  "question": "Which customers bought a Laptop?",
  "sql": "SELECT DISTINCT customers.name, customers.email FROM customers JOIN orders ON customers.customer_id = orders.customer_id JOIN products ON orders.product_id = products.product_id WHERE products.name = 'Laptop'",
  "result": {
    "columns": ["name", "email"],
    "rows": [
      ["Alice Smith", "alice@example.com"]
    ]
  }
}
```
