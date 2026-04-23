from pydantic import BaseModel


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]
    conversation_id: str | None = None
    session_type: str = "teaching"


class ConversationCreate(BaseModel):
    title: str | None = None
    session_type: str = "teaching"


class ConversationResponse(BaseModel):
    id: str
    title: str | None
    session_type: str
    message_count: int
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str
