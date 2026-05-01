import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any


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

    def update_profile_location(self, user_id: str, location: str) -> Optional[Dict[str, Any]]:
        """Update only the location field for an existing profile."""
        response = self.client.table("profiles").update({"location": location}).eq("id", user_id).execute()
        return response.data[0] if response.data else None

    def get_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for a user."""
        response = self.client.table("conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return response.data if response.data else []

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
        response = self.client.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).limit(limit).execute()
        return response.data if response.data else []

    def add_message(self, conversation_id: str, role: str, content: str) -> Dict[str, Any]:
        """Add a message to a conversation."""
        response = self.client.table("messages").insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
        }).execute()
        return response.data[0] if response.data else None

    def store_chunks(self, source_id: str, source_type: str, source_title: str, chunks_data: List[Dict[str, Any]]) -> None:
        """Store chunks with embeddings."""
        # Delete old chunks for this source
        self.client.table("chunks").delete().eq("source_id", source_id).eq("source_type", source_type).execute()

        # Insert new chunks
        if chunks_data:
            self.client.table("chunks").insert(chunks_data).execute()

    def search_chunks_by_location(self, query_embedding: List[float], location: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant chunks using vector similarity filtered by location."""
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
        return response.data if response.data else []

    def get_policies(self) -> List[Dict[str, Any]]:
        """Get all policies."""
        response = self.client.table("policies").select("*").order("created_at", desc=True).execute()
        return response.data if response.data else []

    def create_policy(self, title: str, category: str, content: str, locations: List[str]) -> Dict[str, Any]:
        """Create a new policy."""
        response = self.client.table("policies").insert({
            "title": title,
            "category": category,
            "content": content,
            "locations": locations,
        }).execute()
        return response.data[0] if response.data else None

    def update_policy(self, policy_id: str, **kwargs) -> Dict[str, Any]:
        """Update a policy."""
        response = self.client.table("policies").update(kwargs).eq("id", policy_id).execute()
        return response.data[0] if response.data else None

    def delete_policy(self, policy_id: str) -> None:
        """Delete a policy."""
        self.client.table("policies").delete().eq("id", policy_id).execute()

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


# Global instance
db = SupabaseDB()
