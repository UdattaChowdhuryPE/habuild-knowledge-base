# Habuild Knowledge Base

An internal knowledge base and Q&A assistant for Habuild — covering company policies, HR, operations, and more. Built with FastAPI, Next.js, and Claude AI using semantic search over company documents, with automatic location-based access control to ensure employees only access policies relevant to their location.

## Features

- **Location-aware Q&A**: Automatic location assignment from employee directory; employees can only access HR policies for their assigned location
- **Semantic Search (RAG)**: Vector embeddings (Voyage AI) index all policies and documents by location; documents are chunked at 500 tokens with 100-token overlap; search retrieves only location-relevant content
- **Cross-location Guard**: LLM system prompt enforces a refusal rule — if an employee asks about policies from a different location, Claude returns a standard HR redirect message
- **Real-time Streaming**: Chat responses stream via Server-Sent Events (SSE) for responsive UX
- **Admin Panel**: Upload and manage HR policies and documents; manage employee directory
- **Conversation History**: Last 10 messages included in context for coherent multi-turn conversations

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- `uv` package manager (`pip install uv` or `brew install uv`)
- Supabase account with a project created
- API keys: Anthropic (Claude), Voyage AI, and Supabase credentials

### Install Dependencies

```bash
# Python dependencies
uv sync

# Frontend dependencies
cd frontend-next && npm install
```

### Configure Environment

Copy `.env.example` to `.env` and fill in:

```bash
# Backend
ANTHROPIC_API_KEY=sk-...              # Claude API key from Anthropic
VOYAGE_API_KEY=...                    # Voyage AI API key
SUPABASE_URL=https://...              # Your Supabase project URL
SUPABASE_ANON_KEY=...                 # Supabase anonymous key
SUPABASE_SERVICE_ROLE_KEY=...         # Supabase service role key (for migrations)
ALLOWED_EMAIL_DOMAINS=habuild.in      # Comma-separated allowed email domains (e.g., @company.com)

# Frontend
NEXT_PUBLIC_SUPABASE_URL=https://...  # Supabase URL for frontend client
NEXT_PUBLIC_SUPABASE_ANON_KEY=...     # Supabase anon key for frontend client
BACKEND_URL=http://localhost:8000     # Backend API URL (optional, defaults to localhost:8000)
```

### Run Locally

```bash
# Terminal 1: Backend (port 8000)
uv run python -m backend.main

# Terminal 2: Frontend (port 3000)
cd frontend-next && npm run dev
```

Visit http://localhost:3000 in your browser.

## Architecture

### Backend (`backend/`)

- **`main.py`** — FastAPI application entry point
- **`routers/`** — API endpoints:
  - `auth.py` — Login, profile completion with auto-location assignment
  - `chat.py` — Start conversation, stream chat messages with location-based context
  - `documents.py` — CRUD for documents
  - `employees.py` — Employee directory management
- **`services/`**:
  - `db.py` — Supabase client for database operations
  - `llm.py` — Claude streaming with location-aware system prompts
  - `rag.py` — Document chunking (500 tokens, 100 overlap) and retrieval
  - `embeddings.py` — Voyage AI embedding wrapper
  - `tools.py` — Claude tool-use definitions for employee and policy lookups
- **`dependencies.py`** — FastAPI dependency injection helpers (e.g., `get_current_user`)
- **`models.py`** — Pydantic request/response schemas

### Frontend (`frontend-next/`)

- **`app/page.tsx`** — Main chat interface; conversation management
- **`components/`**:
  - `sign-in-view.tsx` — Google OAuth login
  - `complete-profile-view.tsx` — Auto-submit profile setup (location assigned server-side)
  - `admin-panel.tsx` — Policy and document management
  - `documents-view.tsx` — View uploaded documents
  - `sidebar.tsx` — Navigation between views
- **`lib/api.ts`** — TypeScript client for backend API
- **`lib/supabase.ts`** — Supabase browser client for frontend auth
- **`next.config.mjs`** — Proxy `/api/*` to backend

### Database Schema (`supabase/migrations/`)

- **`001_initial.sql`**:
  - `profiles` — User account data including auto-assigned `location`
  - `conversations` — Chat sessions, scoped by `location`
  - `messages` — Chat history (last 10 included in context)
  - `chunks` — Document chunks with embedding vector and `locations` array for filtering
  - `pgvector` RPC `match_chunks_by_location()` — Vector search filtered by location

- **`002_add_documents.sql`**:
  - `documents` — Uploaded company documents

- **`003_normalize_gurugram.sql`**:
  - Normalizes location name spelling for Gurugram

- **`004_add_employees_table.sql`**:
  - `employees` — Employee directory for location assignment

- **`005_update_chunks_vector_dim.sql`**:
  - Updates vector dimension for `chunks` embeddings

## How Location-Based Access Control Works

### 1. **Automatic Location Assignment on Profile Setup**

When a new employee signs in with their Habuild email (e.g., `john@habuild.in`):

1. **Backend** validates that their email exists in the `employees` table (auto-populated via admin upload)
2. **Backend** extracts the employee's `location` from the directory
3. **Backend** creates the user profile with this location — **the user is never asked to choose**
4. If the email is not in the directory, the backend returns a 404 with: `"Your email is not in the employee directory. Please contact HR."`

**Frontend behavior**: The `CompleteProfileView` component shows a loading spinner (`"Setting up your profile…"`) and auto-submits on mount with no form fields. This ensures location cannot be manually overridden.

### 2. **Server-Side Location Enforcement**

Every chat request flow:

1. **API layer** (`backend/routers/chat.py`) reads the user's profile from the authenticated session
2. Extracts the user's `location` from the database — **location is never trusted from the client**
3. Passes `user_location` to both the RAG pipeline and the LLM service
4. Returns HTTP 400 if profile location is not set (edge case)

**Client sends**: Only `question` and `conversation_id` — no location field in request body or query params.

### 3. **Dual-Layer Cross-Location Guard**

**Layer 1 — RAG Filtering**:
- Document chunks are tagged with a `locations` array (e.g., `["Gurugram", "Delhi"]`)
- Vector search in `get_relevant_context()` filters results to only chunks matching `user_location`
- If an employee from Gurugram asks a question, only Gurugram policies are retrieved

**Layer 2 — LLM System Prompt Rule**:
```
LOCATION RULE (HIGHEST PRIORITY):
If the user asks about HR policies, leave, benefits, or any information that pertains 
to a location OTHER than {user_location}, do NOT provide that information.
Instead respond exactly:
"I can only provide HR information relevant to your location ({user_location}). 
For policies at other locations, please reach out to HR directly."
```

**Example**: Employee from Gurugram asks *"What is the leave policy in Bangalore?"*
- RAG retrieval returns no Bangalore chunks (only Gurugram chunks available)
- LLM system prompt also explicitly refuses to answer cross-location questions
- Claude responds: `"I can only provide HR information relevant to your location (Gurugram). For policies at other locations, please reach out to HR directly."`

## Core Workflows

### 1. Ingestion

1. Admin uploads HR policies or documents (CSV, PDF, TXT)
2. **Backend** extracts text and splits into chunks (500 tokens, split at paragraph/sentence boundaries, with 100-token tail overlap for context continuity)
3. **Voyage AI** embeds each chunk (512-dimensional vector)
4. Chunks stored in Supabase with metadata: `location`, `document_id`, `embedding`

### 2. Chat Query

1. User types a question in the chat
2. **Frontend** sends question to `POST /chat/message`
3. **Backend** retrieves user's `location` from authenticated profile
4. **RAG pipeline** embeds question and retrieves top-5 chunks matching `location`
5. **LLM** streams response with context + last 10 messages
6. **Frontend** receives SSE stream (`data: <token>\n\n`) and renders tokens in real-time

### 3. Conversation History

- Conversations are scoped by user and location
- Last 10 messages included in next request for context
- Location is stored at conversation creation time (for audit trail)

## API Endpoints

### Authentication
- `GET /auth/me` — Get authenticated user's profile
- `POST /auth/complete-profile` — Create profile with location auto-assigned from employee directory (no body)

### Chat
- `POST /chat/start` — Create conversation (returns `conversation_id`)
- `POST /chat/message` — Stream chat message (SSE response)

### Admin
- `GET/POST /documents` — Upload and manage documents
- `GET/POST /employees` — Employee directory management

## Testing

### Manual Testing
1. Sign in with an employee email from the directory → profile auto-creates with correct location
2. Ask a question about your location's policies → get answer from RAG context
3. Ask "What is the leave policy in [other location]?" → get HR redirect message
4. Check Network tab in browser DevTools → `/chat/message` request body contains no `location` field

### Example Queries
- **Allowed**: "What is the leave policy?" (own location)
- **Cross-location block**: "What is the leave policy in Bangalore?" (from non-Bangalore account) → HR redirect
- **Not in directory**: Sign in with email not in employee directory → "Your email is not in the employee directory. Please contact HR."

## Development Notes

- **Claude model**: `claude-haiku-4-5-20251001`
- **Embeddings**: Voyage AI `voyage-3-lite` (512 dimensions)
- **Conversation context**: Last 10 messages per request
- **Chunk size**: 500 tokens with 100-token tail overlap between adjacent chunks (split at paragraph/sentence boundaries)
- **No automated tests yet** — testing is manual via UI or curl

## Security

- Location is the source of truth in the authenticated user's profile, read from Supabase
- Client cannot override or choose location in requests
- All document chunks are tagged by location; cross-location queries are blocked at RAG + LLM layers
- Employee directory (uploaded CSV) is the single source of truth for location assignment
- Row-level security (RLS) policies in Supabase prevent access to other users' conversations/profiles

## Troubleshooting

- **"Your email is not in the employee directory"** → Add your email to the employee directory in the admin panel
- **Profile setup stuck on loading** → Check backend logs; ensure database migrations ran
- **Location not auto-assigned** → Verify employee email matches exactly (case-sensitive in some cases)
- **Cross-location policy answers being returned** → Check that document chunks have correct `locations` array set in database

## Future Enhancements

- Audit logging for cross-location query attempts
- Admin dashboard showing query patterns by location
- Bulk employee directory import with validation
- Multi-location support for employees (e.g., hybrid roles)
