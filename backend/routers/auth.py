from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.services.db import db
from backend.dependencies import get_current_user, is_allowed_email

router = APIRouter(prefix="/auth", tags=["auth"])


class CompleteProfileRequest(BaseModel):
    pass


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
    Create or update the user's profile with location from employee directory.
    Called once after first Google login.
    """
    if not is_allowed_email(current_user["email"]):
        raise HTTPException(status_code=403, detail="Email domain not allowed")

    existing = db.get_profile_by_id(current_user["id"])

    if existing:
        return existing
    
    employee_record = db.get_employee_by_email(current_user["email"])
    if not employee_record:
        raise HTTPException(status_code=404, detail="Your email is not in the employee directory. Please contact HR.")
    
    location = employee_record.get("location")
    if not location:
        raise HTTPException(status_code=404, detail="Location not found for your email. Please contact HR.")
    
    role = "employee"
    if employee_record.get("role") in ("employee", "hr"):
        role = employee_record["role"]

    profile = db.create_profile(
        user_id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        location=location,
        role=role,
    )

    return profile
