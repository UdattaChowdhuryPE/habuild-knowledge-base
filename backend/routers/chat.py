from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from backend.models import ChatRequest
from backend.services.db import db
from backend.services.rag import get_relevant_context
from backend.services.llm import llm_service
from backend.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/start")
async def start_conversation(location: str, current_user: dict = Depends(get_current_user)):
    """Start a new conversation."""
    try:
        normalized_location = location.strip().title()
        conversation = db.create_conversation(current_user["id"], normalized_location)
        return {"conversation_id": conversation["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message")
async def send_message(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Send a message and get a streaming response from Claude.
    """
    try:
        # Verify conversation belongs to current user
        conversation = db.get_conversation(request.conversation_id)
        if not conversation or conversation["user_id"] != current_user["id"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Fetch history before saving the new message so the current question
        # isn't duplicated (llm.py appends it again when building messages)
        history = db.get_conversation_messages(request.conversation_id, limit=10)
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]

        # Store user message after fetching history
        db.add_message(request.conversation_id, "user", request.question)

        # Get relevant context from RAG
        normalized_location = request.location.strip().title()
        context = get_relevant_context(request.question, normalized_location, top_k=5)

        # Stream response from Claude
        def response_generator():
            full_response = ""
            try:
                for token in llm_service.stream_chat(request.question, context, conversation_history):
                    full_response += token
                    yield f"data: {token}\n\n"

                # Store assistant message after streaming completes
                db.add_message(request.conversation_id, "assistant", full_response)
                yield "data: [DONE]\n\n"

            except Exception as e:
                yield f"data: [ERROR] {str(e)}\n\n"

        return StreamingResponse(
            response_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str, limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Get message history for a conversation."""
    try:
        conversation = db.get_conversation(conversation_id)
        if not conversation or conversation["user_id"] != current_user["id"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
        messages = db.get_conversation_messages(conversation_id, limit=limit)
        return {"messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
