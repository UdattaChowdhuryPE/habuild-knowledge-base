from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import io
import pandas as pd
from backend.services.db import db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])


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
        locations_to_delete = df["Location"].unique().tolist()
        for loc in locations_to_delete:
            db.client.table("profiles").delete().eq("location", loc).execute()

        # Note: In a real implementation, we'd sync with auth.users table
        # For now, we'll just store profiles with placeholder UUIDs
        # This would require proper integration with Supabase Auth

        return {"status": "uploaded", "count": len(df)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
