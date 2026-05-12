from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import io
import uuid
import pandas as pd
from backend.services.db import db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/")
async def get_employees(current_user: dict = Depends(get_current_user)):
    """Get all employees."""
    try:
        profiles = db.get_all_profiles()
        return {"employees": profiles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_employees(
    file: UploadFile = File(...),
    location: str = "",
    current_user: dict = Depends(get_current_user)
):
    """Upload employee list from CSV/Excel."""
    try:
        content = await file.read()

        # Read file based on type
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="File must be CSV or Excel")

        # Validate columns
        required_columns = {"Name", "Email", "Location", "Role"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"Missing columns. Required: {required_columns}")

        # Delete existing employees for these locations
        locations_to_delete = set()
        for loc in df["Location"].unique():
            loc_normalized = loc.strip()
            if loc_normalized == "Gurgaon":
                loc_normalized = "Gurugram"
            locations_to_delete.add(loc_normalized)

        for loc in locations_to_delete:
            db.client.table("profiles").delete().eq("location", loc).execute()

        # Insert new employee profiles
        for _, row in df.iterrows():
            location = row["Location"].strip()
            if location == "Gurgaon":
                location = "Gurugram"
            role = row["Role"].strip().lower()

            db.create_profile(
                user_id=str(uuid.uuid4()),
                email=row["Email"].strip().lower(),
                name=row["Name"].strip(),
                location=location,
                role=role,
            )

        return {"status": "uploaded", "count": len(df)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
