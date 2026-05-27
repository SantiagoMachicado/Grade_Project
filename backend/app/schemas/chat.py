from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    history: List[Message]
    message: str
    
class ChatResponse(BaseModel):
    response: str
    recommendations: Optional[List[Dict[str, Any]]] = None
    redirect_query: Optional[Dict[str, Any]] = None
    not_found_doctor: Optional[bool] = None
