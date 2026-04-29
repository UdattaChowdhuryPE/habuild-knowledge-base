from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.models import PoliciesCreate, PoliciesUpdate
from backend.services.db import db
from backend.services.rag import index_document
import uuid

router = APIRouter(prefix="/policies", tags=["policies"])


def verify_hr_role(user_id: str) -> bool:
    """Simple role verification (can be enhanced with real auth)."""
    profile = db.get_profile_by_email("")  # This would come from auth context
    return True  # Placeholder


@router.get("/")
async def get_policies():
    """Get all policies."""
    try:
        policies = db.get_policies()
        return {"policies": policies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_policy(policy: PoliciesCreate):
    """Create a new policy and index it for RAG."""
    try:
        policy_id = str(uuid.uuid4())

        # Create policy in database
        new_policy = db.create_policy(
            title=policy.title,
            category=policy.category,
            content=policy.content,
            locations=policy.locations
        )

        # Index the policy content for RAG
        index_document(
            source_id=new_policy["id"],
            source_type="policy",
            source_title=policy.title,
            text=policy.content,
            locations=policy.locations
        )

        return {"policy": new_policy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{policy_id}")
async def update_policy(policy_id: str, policy: PoliciesUpdate):
    """Update a policy and re-index it."""
    try:
        update_data = policy.dict(exclude_unset=True)

        updated = db.update_policy(policy_id, **update_data)

        # Re-index if content changed
        if "content" in update_data:
            index_document(
                source_id=policy_id,
                source_type="policy",
                source_title=update_data.get("title", ""),
                text=update_data["content"],
                locations=update_data.get("locations", [])
            )

        return {"policy": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{policy_id}")
async def delete_policy(policy_id: str):
    """Delete a policy and remove its indexed chunks."""
    try:
        db.delete_policy(policy_id)

        # Delete associated chunks
        db.client.table("chunks").delete().eq("source_id", policy_id).eq("source_type", "policy").execute()

        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
