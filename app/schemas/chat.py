from pydantic import BaseModel
from typing import List

class Message(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    history: List[Message]
    message: str
    
class ChatResponse(BaseModel):
    response: str
