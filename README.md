# Habuild Knowledge Base

An internal knowledge base and Q&A assistant for Habuild — covering company policies, HR, operations, and more. Built with FastAPI, Next.js, and Claude AI using semantic search over company documents.

> **Work in progress** — setup and contribution docs coming once core features stabilize.

## Run Locally

```bash
# Install Python dependencies
uv sync

# Backend (port 8000)
uv run python -m backend.main

# Frontend (port 3000)
cd frontend-next && npm install && npm run dev
```

Copy `.env.example` to `.env` and fill in your API keys before running.
