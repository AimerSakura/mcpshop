# app/schemas/chat.py
from pydantic import BaseModel
from datetime import datetime
from typing import Literal, List

class MessageIn(BaseModel):
    content: str

class MessageOut(BaseModel):
    message_id: int
    sender: Literal['user','bot']
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class ConversationOut(BaseModel):
    conv_id: int
    session_id: str
    messages: List[MessageOut]

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    text: str