import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.routers import chat, policies, documents, employees, auth

# Load environment variables
load_dotenv()

app = FastAPI(
    title="HR Policy Assistant API",
    description="Backend API for the Habuild HR Policy Assistant",
    version="1.0.0"
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8501")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(policies.router)
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
