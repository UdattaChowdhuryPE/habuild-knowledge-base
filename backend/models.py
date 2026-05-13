from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    question: str
    conversation_id: str


class ChatResponse(BaseModel):
    response: str


class DocumentUpload(BaseModel):
    title: str
    category: str
    file_name: str
    file_url: str
    locations: List[str]


class EmployeeVerify(BaseModel):
    email: str


class EmployeeUpload(BaseModel):
    employees: List[dict]
    location: str


class ConversationCreate(BaseModel):
    pass


class ProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    location: str
    role: str
    created_at: str


class MessageCreate(BaseModel):
    role: str
    content: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
