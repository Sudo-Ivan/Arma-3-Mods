from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "meta-llama/llama-3.1-70b-instruct:free"
    temperature: Optional[float] = 0.7
    provider: Optional[str] = "openrouter"  # or "ollama"


class ChatResponse(BaseModel):
    response: str
    provider: str
