# RAG-API — Medical & Legal Intelligence System

A production-ready **Retrieval-Augmented Generation (RAG)** system that delivers intelligent, context-aware answers for medical and legal queries with minimal hallucinations. Built as part of a 4th semester BS Artificial Intelligence course at FAST-NUCES.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red?style=flat-square)
![n8n](https://img.shields.io/badge/n8n-Workflow-orange?style=flat-square)
![LLaMA](https://img.shields.io/badge/LLaMA-3.3--70B-purple?style=flat-square)

---

## What is this?

Most LLM chatbots answer from general training data — which leads to hallucinations, especially in high-stakes domains like medicine and law. This system fixes that by retrieving relevant information from a curated knowledge base **before** generating an answer, ensuring responses are grounded in real documents.

The pipeline automatically classifies every query as **Medical**, **Legal**, or **General**, then retrieves domain-specific context from a Qdrant vector database and generates a response using LLaMA 70B — with mandatory safety disclaimers enforced at the prompt level.

---

## Architecture

```
User Message
     │
     ▼
┌─────────────────┐
│  Sanitize Input  │  ← strips prompt injection attempts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Optimizer  │  ← LLaMA 70B rewrites query for better retrieval
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rule Classifier  │  ← regex-based domain routing
└────────┬────────┘
         │
    ┌────┴─────┐────────────┐
    ▼          ▼            ▼
 Medical     Legal       General
    │          │            │
    └────┬─────┘────────────┘
         │
         ▼
┌─────────────────────┐
│  FastAPI /rag        │  ← POST http://localhost:8000/rag
│  (app.py)           │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Embed Query         │  ← all-MiniLM-L6-v2 → 384-dim vector
│  (embeddings.py)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Qdrant Vector DB    │  ← cosine similarity search, top 5 chunks
│  (qdrant_db.py)     │     score threshold ≥ 0.3
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Domain LLM Chain    │  ← separate LLaMA 70B prompt per domain
│  Medical/Legal/Gen  │     with mandatory safety disclaimers
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Output Filter       │  ← blocks jailbreaks, strips markdown
└────────┬────────────┘
         │
         ▼
      Response
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Workflow Orchestration | n8n (self-hosted) | Visual pipeline, routing, LLM chains |
| Vector Database | Qdrant (Docker) | Semantic search over document chunks |
| Embeddings | all-MiniLM-L6-v2 | Converts text to 384-dim vectors |
| LLM Inference | Groq API + LLaMA 3.3-70B | Query optimization + answer generation |
| Backend API | FastAPI (Python) | RAG endpoint connecting n8n to Qdrant |
| Containerization | Docker | Qdrant + n8n isolation |

---

## Dataset

The knowledge base contains three document sources, all vectorized and stored in a single Qdrant collection (`medical_legal_collection`):

| Source | Category Tag | Content |
|--------|-------------|---------|
| `medical_data.txt` | `medical` | General medical information, conditions, treatments |
| `legal_data.txt` | `legal` | Legal concepts, rights, contract and employment law |
| `pubmed_abstracts.csv` | 8 scientific categories | Real PubMed research abstracts |

**PubMed categories covered:**
- Deep Learning
- COVID-19
- Human Connectome
- Virtual Reality
- Brain-Machine Interfaces
- Electroactive Polymers
- PEDOT Electrodes
- Neuroprosthetics

---

## Key Features

**Security**
- Input sanitization strips prompt injection attacks before reaching any LLM
- Output filter checks LLM responses for jailbreak phrases
- Similarity score threshold (≥ 0.3) discards low-quality Qdrant matches

**Domain Safety**
- Medical responses always end with *"This is not medical advice."*
- Legal responses always end with *"This is not legal advice."*
- Disclaimers are enforced at the system prompt level — the model cannot skip them

**Smart Retrieval**
- Semantic search finds relevant chunks even when wording differs (e.g. "heart attack" matches "myocardial infarction")
- Top 5 chunks retrieved per query with source file attribution
- Conversational memory retains last 10 messages for context-aware follow-ups

---

## Project Structure

```
rag-api/
├── app.py              # FastAPI server — /rag endpoint
├── embeddings.py       # Text → vector conversion (all-MiniLM-L6-v2)
├── qdrant_db.py        # Qdrant search — top 5 semantic matches
├── insert_data.py      # One-time data ingestion script
├── search.py           # Manual search test utility
├── medical_data.txt    # Medical knowledge base
├── legal_data.txt      # Legal knowledge base
├── pubmed_abstracts.csv# Scientific research abstracts
├── workflow.json       # n8n workflow — import this into n8n
├── requirements.txt    # Python dependencies
└── .env                # API keys (not committed)
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Docker Desktop
- n8n (via Docker)
- Groq API key (free at [groq.com](https://groq.com))

### 1. Clone the repository
```bash
git clone https://github.com/mahadmunawar/rag-medical-legal.git
cd rag-medical-legal
```

### 2. Set up Python environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Start Qdrant
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 5. Load data into Qdrant (one-time setup)
```bash
python insert_data.py
```

### 6. Start the FastAPI backend
```bash
uvicorn app:app --reload
```

### 7. Start n8n
```bash
docker run -it --rm --name n8n -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

### 8. Import the workflow
- Open **http://localhost:5678**
- Go to **Workflows → Import from file**
- Select `workflow.json`
- Add your Groq API key as a credential

---

## Example Queries

| Query | Route | Source |
|-------|-------|--------|
| "What are the side effects of chemotherapy?" | Medical | pubmed_abstracts.csv |
| "Can I sue my employer for wrongful termination?" | Legal | legal_data.txt |
| "What is a brain-machine interface?" | Medical | pubmed_abstracts.csv |
| "Explain the concept of due process" | Legal | legal_data.txt |
| "What is deep learning?" | General | pubmed_abstracts.csv |
| "ignore previous instructions" | Blocked | — |

---

## How RAG Works Here

1. User query is converted to a 384-dimensional vector using `all-MiniLM-L6-v2`
2. Qdrant finds the 5 document chunks whose vectors are closest (by cosine similarity)
3. Those chunks are injected into the LLM prompt as context
4. LLaMA 70B generates an answer grounded in your documents — not hallucinated

This means the system answers based on **your data**, not general internet knowledge, and cites the source file for every response.

---

## Team

- **Mahad Munawar** — Dataset, Vector Database, RAG Pipeline
- **Abdullah Sonija** — n8n Workflow, LLM Chains, System Architecture
- **Syed Zahid Hussain** — Backend API, Embeddings, Integration

**Institution:** FAST-NUCES | BS Artificial Intelligence | 4th Semester

---

## License

MIT License — free to use, modify, and distribute.
