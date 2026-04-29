from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import uuid
from io import BytesIO
import PyPDF2
from docx import Document
from backend.services.db import db
from backend.services.rag import index_document

router = APIRouter(prefix="/documents", tags=["documents"])


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF."""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX."""
    try:
        doc = Document(BytesIO(file_bytes))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse DOCX: {str(e)}")


def extract_text_from_file(file: UploadFile, file_bytes: bytes) -> str:
    """Extract text based on file type."""
    filename_lower = file.filename.lower()

    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(".docx") or filename_lower.endswith(".doc"):
        return extract_text_from_docx(file_bytes)
    elif filename_lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT.")


@router.get("/")
async def get_documents(location: Optional[str] = None):
    """Get documents, optionally filtered by location."""
    try:
        documents = db.get_documents(location=location)
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(...),
    locations: str = Form(...)  # JSON string or comma-separated
):
    """Upload a document and index it for RAG."""
    try:
        # Parse locations
        if isinstance(locations, str):
            location_list = [loc.strip() for loc in locations.split(",")]
        else:
            location_list = locations

        # Read file
        file_bytes = await file.read()

        # Extract text
        text_content = extract_text_from_file(file, file_bytes)

        # Upload to Supabase Storage
        document_id = str(uuid.uuid4())
        file_path = f"documents/{document_id}/{file.filename}"

        storage_response = db.client.storage.from_("documents").upload(
            file_path,
            file_bytes,
            {"contentType": file.content_type or "application/octet-stream"}
        )

        # Get public URL
        file_url = db.client.storage.from_("documents").get_public_url(file_path)

        # Store document metadata
        document = db.create_document(
            title=title,
            category=category,
            file_name=file.filename,
            file_url=file_url,
            locations=location_list
        )

        # Index document content for RAG
        index_document(
            source_id=document["id"],
            source_type="document",
            source_title=title,
            text=text_content,
            locations=location_list
        )

        return {"document": document}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and remove its indexed chunks."""
    try:
        # Get document to find file path
        documents = db.get_documents()
        document = next((d for d in documents if d["id"] == document_id), None)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete from storage
        file_path = f"documents/{document_id}/{document['file_name']}"
        db.client.storage.from_("documents").remove([file_path])

        # Delete from database
        db.delete_document(document_id)

        # Delete chunks
        db.client.table("chunks").delete().eq("source_id", document_id).eq("source_type", "document").execute()

        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
