from fastapi import APIRouter, HTTPException, Request
import os
from backend.services.db import db

router = APIRouter(prefix="/auth", tags=["auth"])

ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "habuild.in")


@router.post("/callback")
async def auth_callback(request: Request):
    """
    Handle OAuth callback from Supabase.
    This would be called after user authenticates with Google.
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")
        email = data.get("email")
        name = data.get("name", "")

        # Verify email domain
        if not email.endswith(f"@{ALLOWED_EMAIL_DOMAIN}"):
            raise HTTPException(status_code=403, detail="Email domain not allowed")

        # Check if profile exists
        profile = db.get_profile_by_email(email)

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found. Please complete onboarding."
            )

        return {
            "id": profile["id"],
            "name": profile["name"],
            "email": profile["email"],
            "location": profile["location"],
            "role": profile["role"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete-profile")
async def complete_profile(
    user_id: str,
    email: str,
    name: str,
    location: str
):
    """
    Complete profile after first login (location selection).
    """
    try:
        # Verify email domain
        if not email.endswith(f"@{ALLOWED_EMAIL_DOMAIN}"):
            raise HTTPException(status_code=403, detail="Email domain not allowed")

        # Create profile
        profile = db.create_profile(
            user_id=user_id,
            email=email,
            name=name,
            location=location,
            role="employee"
        )

        return {"profile": profile}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
