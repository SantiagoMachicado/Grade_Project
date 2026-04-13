from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import get_gemini_response
from app.api.deps import get_current_user
from app.models.user import User
import logging

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        reply = get_gemini_response(request.history, request.message)
        return ChatResponse(response=reply)
    except Exception as e:
        logging.error(f"Error en chat: {str(e)}")
        # If credentials are not set, LangChain will throw an error
        raise HTTPException(status_code=500, detail=str(e))
