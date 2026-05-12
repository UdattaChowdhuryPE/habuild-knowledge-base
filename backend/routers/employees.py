from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import io
import traceback
import pandas as pd
from backend.services.db import db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])

def _cell(val, default=""):
    """Convert pandas cell to string, treating NaN/None as default."""
    if pd.isna(val):
        return default
    return str(val).strip()


@router.get("/")
async def get_employees(current_user: dict = Depends(get_current_user)):
    """Get all employees."""
    try:
        employees = db.get_all_employees()
        return {"employees": employees}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_employees(
    file: UploadFile = File(...),
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
            loc_normalized = _cell(loc)
            if loc_normalized == "Gurgaon":
                loc_normalized = "Gurugram"
            if loc_normalized:
                locations_to_delete.add(loc_normalized)

        for loc in locations_to_delete:
            db.delete_employees_by_location(loc)

        # Build list of employee records for bulk insert
        employees_to_insert = []
        for _, row in df.iterrows():
            name = _cell(row["Name"])
            email = _cell(row["Email"]).lower()
            location = _cell(row["Location"])
            role = _cell(row["Role"]).lower() or "employee"

            # Skip blank rows
            if not name or not email:
                continue

            if location == "Gurgaon":
                location = "Gurugram"

            employees_to_insert.append({
                "name": name,
                "email": email,
                "location": location,
                "role": role,
            })

        # Bulk insert all employees in one API call
        count = db.bulk_create_employees(employees_to_insert)
        return {"status": "uploaded", "count": count}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
