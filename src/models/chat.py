from pydantic import BaseModel
from typing import Optional
from enum import StrEnum

class RoleType(StrEnum):
    USER = 'user'
    ASSISTANT = 'assistant'

class CommandModel(BaseModel):
    name: str
    arguments: dict
    result: str
    cache_hit: bool

class MessageModel(BaseModel):
    id: str
    role: RoleType
    text: Optional[str] = None
    reasoning: Optional[str] = None
    command: Optional[CommandModel] = None

class LLMType(StrEnum):
    GEMINI = 'gemini'
    DEEPSEEK = 'deepseek'

class ChatModel(BaseModel):
    id: str = None
    llm_type: LLMType
    title: Optional[str] = None
    messages: list[MessageModel] = []

class ChatIdModel(BaseModel):
    id: str
