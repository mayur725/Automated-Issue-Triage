# Automated Issue Triage & Categorization — Prototype

This repository contains a deployable prototype for Automated Issue Triage & Categorization.  
It is designed for hackathon use: an end-to-end pipeline that ingests ServiceNow-style tickets,  
classifies them, retrieves relevant Confluence-like documents, links similar resolved JIRA-like incidents,  
and returns a JSON payload with suggested priority and routing.

---

## Key Features
- FastAPI HTTP server for ingesting tickets (`/triage` endpoint)
- Pluggable classifier:
  - OpenAI / Azure LLM-based classification (if API key is provided), OR  
  - Local TF-IDF fallback classifier
- Pluggable retriever:
  - OpenAI embeddings-based semantic search (if API key is provided), OR  
  - Local TF-IDF similarity fallback
- Mocked Confluence document corpus (`data/confluence_docs/`)
- Mocked resolved JIRA dataset (`data/resolved_jira.json`)
- Prometheus instrumentation endpoint (`/metrics`) for basic metrics
- Dockerfile for containerized deployment
- **Mock Confluence & JIRA used for demo purposes (can be replaced with real APIs in production)**

---

## Quick Start (Local)

### 1. Clone or download this project.

### 2. Create a virtual environment and install dependencies:
```
python -m venv venv
# Windows PowerShell:
.env\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy `.env.example` → create a file named `.env` and update.

```
# Only required if using OpenAI (optional)
OPENAI_API_KEY=your_key_here

# Set true to enable OpenAI classification + embeddings
USE_OPENAI=true

# If no API key is available, set:
# USE_OPENAI=false
```

*Do NOT commit `.env` or share API keys.*

---

### 4. Run the app:
```
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open the demo UI:
http://localhost:8000/

Paste any ticket and click "Run Triage".

---

## Precompute Embeddings (optional)
If `USE_OPENAI=true` and `OPENAI_API_KEY` is set:

```
python precompute_embeddings.py
```

This computes embeddings for the mock Confluence docs and mock JIRA summaries  
and saves them to `data/embeddings.json`.

---

## Output Format
The API returns JSON with:

- `ticket_id`
- `category`
- `priority`
- `confidence`
- `matched_doc`
- `matched_jira` (list)
- `explanation`

---

## Notes
- This prototype uses *mock* Confluence and JIRA data for demonstration.  
  These files can be replaced with **real APIs** for production integration.
- Classification and retrieval fully support LLM-based enhancements if API credentials are provided.
