from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import io
import traceback
import pandas as pd
from backend.services.db import db
from backend.dependencies import get_current_user, require_hr_role

router = APIRouter(prefix="/employees", tags=["employees"])

def _cell(val, default=""):
    """Convert pandas cell to string, treating NaN/None as default."""
    if pd.isna(val):
        return default
    return str(val).strip()


@router.get("")
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
    current_user: dict = Depends(require_hr_role)
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

        # Build list of employee records for bulk insert, tracking skipped rows
        employees_to_insert = []
        skipped_rows = []
        for idx, row in df.iterrows():
            name = _cell(row["Name"])
            email = _cell(row["Email"]).lower()
            location = _cell(row["Location"])
            role = _cell(row["Role"]).lower() or "employee"

            # Skip blank rows, but track them
            if not name or not email:
                skipped_rows.append({
                    "row": int(idx) + 2,  # +1 for 0-index, +1 for header
                    "reason": "missing name" if not name else "missing email",
                    "partial_data": name or email or "(blank)"
                })
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

        # Try to propagate role changes to existing profiles, but don't fail the upload if this times out
        profiles_updated = 0
        try:
            profiles_updated = db.update_profiles_role_for_employees(employees_to_insert)
        except Exception as e:
            # Profile updates are nice-to-have, not critical. Log and continue.
            import traceback
            traceback.print_exc()
            print(f"Warning: Profile role updates failed (non-critical): {e}")

        return {
            "status": "uploaded",
            "count": count,
            "profiles_updated": profiles_updated,
            "skipped": len(skipped_rows),
            "skipped_rows": skipped_rows[:20] if skipped_rows else []
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
