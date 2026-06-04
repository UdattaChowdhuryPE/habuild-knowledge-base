import os
import time
from contextlib import contextmanager
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import structlog

log = structlog.get_logger(__name__)


@contextmanager
def _timed(operation: str, **log_kwargs):
    """Context manager to log operation timing at DEBUG level."""
    t = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = round((time.perf_counter() - t) * 1000, 1)
        log.debug("db.call", operation=operation, duration_ms=duration_ms, **log_kwargs)


class SupabaseDB:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not all([self.url, self.anon_key, self.service_key]):
            raise ValueError("Missing Supabase environment variables")

        self.client: Client = create_client(self.url, self.service_key)

    def get_profile_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile by email."""
        response = self.client.table("profiles").select("*").eq("email", email).limit(1).execute()
        return response.data[0] if response.data else None

    def get_profile_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile by UUID."""
        response = self.client.table("profiles").select("*").eq("id", user_id).limit(1).execute()
        return response.data[0] if response.data else None

    def create_profile(self, user_id: str, email: str, name: str, location: str, role: str = "employee") -> Dict[str, Any]:
        """Create a new user profile."""
        response = self.client.table("profiles").insert({
            "id": user_id,
            "email": email,
            "name": name,
            "location": location,
            "role": role,
        }).execute()
        return response.data[0] if response.data else None

    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Fetch all profiles, ordered by name."""
        response = self.client.table("profiles").select("*").order("name", desc=False).execute()
        return response.data if response.data else []

    def create_employee(self, email: str, name: str, location: str, role: str = "employee") -> Dict[str, Any]:
        """Create a new employee record (HR directory, no auth.users FK)."""
        response = self.client.table("employees").insert({
            "email": email,
            "name": name,
            "location": location,
            "role": role,
        }).execute()
        return response.data[0] if response.data else None

    def bulk_create_employees(self, employees: List[Dict[str, Any]]) -> int:
        """Bulk insert employee records. Returns count inserted."""
        if not employees:
            return 0
        response = self.client.table("employees").insert(employees).execute()
        return len(response.data) if response.data else 0

    def get_all_employees(self) -> List[Dict[str, Any]]:
        """Fetch all employees from the HR directory, ordered by name."""
        response = self.client.table("employees").select("*").order("name", desc=False).execute()
        return response.data if response.data else []

    def delete_employees_by_location(self, location: str) -> None:
        """Delete all employees for a given location (used before re-importing from CSV)."""
        self.client.table("employees").delete().eq("location", location).execute()

    def get_employee_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Look up a single employee record by email (case-insensitive)."""
        response = (
            self.client.table("employees")
            .select("email, name, location, role")
            .ilike("email", email)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    def update_profiles_role_for_employees(self, employees: List[Dict[str, Any]]) -> int:
        """For each employee record, update the matching profiles row's role if a profile exists for that email. Returns the number of profiles actually updated."""
        updated = 0
        for emp in employees:
            email = emp["email"]
            role = emp["role"]
            response = (
                self.client.table("profiles")
                .update({"role": role})
                .eq("email", email)
                .execute()
            )
            if response.data:
                updated += len(response.data)
        return updated

    def update_profile_location(self, user_id: str, location: str) -> Optional[Dict[str, Any]]:
        """Update only the location field for an existing profile."""
        response = self.client.table("profiles").update({"location": location}).eq("id", user_id).execute()
        return response.data[0] if response.data else None

    def get_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for a user."""
        response = self.client.table("conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return response.data if response.data else []


    def get_user_conversations(self, user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Get recent conversations for a user with preview titles (first message)."""
        convos = self.client.table("conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        if not convos.data:
            return []
        
        result = []
        for convo in convos.data:
            # Get first message as title preview
            messages = self.client.table("messages").select("content").eq("conversation_id", convo["id"]).order("created_at", desc=False).limit(1).execute()
            # Skip empty conversations (no messages yet)
            if not messages.data:
                continue
            title = messages.data[0]["content"][:60] + ("..." if len(messages.data[0]["content"]) > 60 else "")
            result.append({
                "id": convo["id"],
                "title": title,
                "created_at": convo["created_at"]
            })
        return result

    def create_conversation(self, user_id: str, location: str) -> Dict[str, Any]:
        """Create a new conversation."""
        response = self.client.table("conversations").insert({
            "user_id": user_id,
            "location": location,
        }).execute()
        return response.data[0] if response.data else None

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a single conversation by ID."""
        response = self.client.table("conversations").select("*").eq("id", conversation_id).limit(1).execute()
        return response.data[0] if response.data else None

    def get_conversation_messages(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get messages for a conversation."""
        with _timed("get_conversation_messages", conversation_id=conversation_id, limit=limit):
            response = self.client.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).limit(limit).execute()
            rows_returned = len(response.data) if response.data else 0
            log.debug("get_conversation_messages.result", rows=rows_returned)
        return response.data if response.data else []

    def add_message(self, conversation_id: str, role: str, content: str) -> Dict[str, Any]:
        """Add a message to a conversation."""
        with _timed("add_message", conversation_id=conversation_id, role=role):
            response = self.client.table("messages").insert({
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            }).execute()
        return response.data[0] if response.data else None

    def store_chunks(self, source_id: str, source_type: str, source_title: str, chunks_data: List[Dict[str, Any]]) -> None:
        """Store chunks with embeddings."""
        with _timed("store_chunks", source_id=source_id, chunk_count=len(chunks_data)):
            # Delete old chunks for this source
            self.client.table("chunks").delete().eq("source_id", source_id).eq("source_type", source_type).execute()

            # Insert new chunks, formatting embeddings as pgvector
            if chunks_data:
                formatted_chunks = []
                for chunk in chunks_data:
                    formatted_chunk = chunk.copy()
                    # Format embedding as pgvector string [a,b,c,...]
                    if isinstance(formatted_chunk.get('embedding'), list):
                        formatted_chunk['embedding'] = f"[{','.join(str(float(x)) for x in formatted_chunk['embedding'])}]"
                    formatted_chunks.append(formatted_chunk)
                self.client.table("chunks").insert(formatted_chunks).execute()

    def search_chunks_by_location(self, query_embedding: List[float], location: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant chunks using vector similarity filtered by location."""
        with _timed("search_chunks_by_location", location=location, top_k=top_k):
            # Use Supabase's vector similarity search
            # We'll use the direct SQL RPC approach with pgvector
            response = self.client.rpc(
                "match_chunks_by_location",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "location_filter": location,
                }
            ).execute()
            rows_returned = len(response.data) if response.data else 0
            log.info(
                "search_chunks_by_location.result",
                location=location,
                top_k=top_k,
                rows_returned=rows_returned,
            )
        return response.data if response.data else []

    def get_documents(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get documents, optionally filtered by location."""
        query = self.client.table("documents").select("*")
        if location:
            query = query.contains("locations", [location])
        response = query.order("created_at", desc=True).execute()
        return response.data if response.data else []

    def create_document(self, title: str, category: str, file_name: str, file_url: str, locations: List[str]) -> Dict[str, Any]:
        """Create a new document metadata entry."""
        response = self.client.table("documents").insert({
            "title": title,
            "category": category,
            "file_name": file_name,
            "file_url": file_url,
            "locations": locations,
        }).execute()
        return response.data[0] if response.data else None

    def delete_document(self, document_id: str) -> None:
        """Delete a document."""
        self.client.table("documents").delete().eq("id", document_id).execute()

    def count_employees(self, location: Optional[str] = None) -> int:
        """Count employees, optionally filtered by location."""
        query = self.client.table("employees").select("id", count="exact")
        if location:
            query = query.eq("location", location)
        response = query.execute()
        return response.count if hasattr(response, 'count') else len(response.data) if response.data else 0

    def find_employee_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Find employees by name (partial match, case-insensitive)."""
        response = (
            self.client.table("employees")
            .select("name, email, location, role")
            .ilike("name", f"%{name}%")
            .order("name", desc=False)
            .execute()
        )
        return response.data if response.data else []

    def list_employees_by_location(self, location: str) -> List[Dict[str, Any]]:
        """List all employees at a given location."""
        response = (
            self.client.table("employees")
            .select("name, email, location, role")
            .eq("location", location)
            .order("name", desc=False)
            .execute()
        )
        return response.data if response.data else []


# Global instance
db = SupabaseDB()
