from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.services.db import db
from backend.dependencies import get_current_user
import os

router = APIRouter(prefix="/auth", tags=["auth"])
ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "habuild.in")


class CompleteProfileRequest(BaseModel):
    location: str


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile. Returns 404 if profile doesn't exist yet."""
    profile = db.get_profile_by_id(current_user["id"])
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/complete-profile")
async def complete_profile(
    body: CompleteProfileRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Create or update the user's profile with their chosen location.
    Called once after first Google login to set the office location.
    """
    if not current_user["email"].endswith(f"@{ALLOWED_EMAIL_DOMAIN}"):
        raise HTTPException(status_code=403, detail="Email domain not allowed")

    existing = db.get_profile_by_id(current_user["id"])

    if existing:
        profile = db.update_profile_location(
            user_id=current_user["id"],
            location=body.location,
        )
    else:
        profile = db.create_profile(
            user_id=current_user["id"],
            email=current_user["email"],
            name=current_user["name"],
            location=body.location,
            role="employee",
        )

    return profile
