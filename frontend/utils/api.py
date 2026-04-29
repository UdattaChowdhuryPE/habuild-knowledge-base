import os
import requests
from typing import Optional, Generator
import json

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    def __init__(self):
        self.base_url = BACKEND_URL

    def start_conversation(self, location: str, user_id: str) -> dict:
        """Start a new conversation."""
        response = requests.post(
            f"{self.base_url}/chat/start",
            params={"location": location, "user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    def send_message(self, question: str, conversation_id: str, location: str) -> Generator[str, None, None]:
        """Send a message and stream the response."""
        payload = {
            "question": question,
            "conversation_id": conversation_id,
            "location": location
        }

        with requests.post(
            f"{self.base_url}/chat/message",
            json=payload,
            stream=True
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8") if isinstance(line, bytes) else line
                    if line_str.startswith("data: "):
                        data = line_str[6:]
                        if data and data != "[DONE]" and not data.startswith("[ERROR]"):
                            yield data

    def get_conversation_history(self, conversation_id: str, limit: int = 20) -> dict:
        """Get message history for a conversation."""
        response = requests.get(
            f"{self.base_url}/chat/history/{conversation_id}",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def get_policies(self) -> dict:
        """Get all policies."""
        response = requests.get(f"{self.base_url}/policies/")
        response.raise_for_status()
        return response.json()

    def create_policy(self, title: str, category: str, content: str, locations: list) -> dict:
        """Create a new policy."""
        payload = {
            "title": title,
            "category": category,
            "content": content,
            "locations": locations
        }
        response = requests.post(f"{self.base_url}/policies/", json=payload)
        response.raise_for_status()
        return response.json()

    def update_policy(self, policy_id: str, **kwargs) -> dict:
        """Update a policy."""
        response = requests.put(f"{self.base_url}/policies/{policy_id}", json=kwargs)
        response.raise_for_status()
        return response.json()

    def delete_policy(self, policy_id: str) -> dict:
        """Delete a policy."""
        response = requests.delete(f"{self.base_url}/policies/{policy_id}")
        response.raise_for_status()
        return response.json()

    def get_documents(self, location: Optional[str] = None) -> dict:
        """Get documents."""
        params = {}
        if location:
            params["location"] = location
        response = requests.get(f"{self.base_url}/documents/", params=params)
        response.raise_for_status()
        return response.json()

    def upload_document(self, file_path: str, title: str, category: str, locations: list) -> dict:
        """Upload a document."""
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "title": title,
                "category": category,
                "locations": ",".join(locations)
            }
            response = requests.post(
                f"{self.base_url}/documents/upload",
                files=files,
                data=data
            )
        response.raise_for_status()
        return response.json()

    def delete_document(self, document_id: str) -> dict:
        """Delete a document."""
        response = requests.delete(f"{self.base_url}/documents/{document_id}")
        response.raise_for_status()
        return response.json()

    def verify_employee(self, email: str) -> dict:
        """Verify an employee."""
        response = requests.post(
            f"{self.base_url}/employees/verify",
            params={"email": email}
        )
        response.raise_for_status()
        return response.json()

    def upload_employees(self, file_path: str, location: str) -> dict:
        """Upload employee list."""
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"location": location}
            response = requests.post(
                f"{self.base_url}/employees/upload",
                files=files,
                data=data
            )
        response.raise_for_status()
        return response.json()

    def complete_profile(self, user_id: str, email: str, name: str, location: str) -> dict:
        """Complete user profile after first login."""
        payload = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "location": location
        }
        response = requests.post(f"{self.base_url}/auth/complete-profile", json=payload)
        response.raise_for_status()
        return response.json()


client = APIClient()
