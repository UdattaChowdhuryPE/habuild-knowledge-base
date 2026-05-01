from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from backend.services.db import db
import os

security = HTTPBearer()


def is_allowed_email(email: str) -> bool:
    return email.endswith("@habuild.in") or email.endswith(".habuild@gmail.com")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """
    Validate Supabase JWT and return the authenticated user.
    Raises 401 if token is invalid, 403 if email domain is not allowed.
    """
    token = credentials.credentials
    try:
        response = db.client.auth.get_user(token)
        user = response.user
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    email = user.email or ""
    if not is_allowed_email(email):
        raise HTTPException(status_code=403, detail="Email domain not allowed")

    return {
        "id": str(user.id),
        "email": email,
        "name": user.user_metadata.get("full_name", email.split("@")[0]),
    }
