import os
from pathlib import Path
from dotenv import load_dotenv

# Must load env before any service imports that read os.getenv at module level
load_dotenv(Path(__file__).parent / ".env")

from backend.observability import configure_logging, configure_tracing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.routers import chat, documents, employees, auth

app = FastAPI(
    title="HR Policy Assistant API",
    description="Backend API for the Habuild HR Policy Assistant",
    version="1.0.0"
)

# Configure observability
configure_logging(os.getenv("LOG_LEVEL", "INFO"))
configure_tracing(app)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register request logging middleware (runs after CORS due to reverse order)
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(employees.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "HR Policy Assistant API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
