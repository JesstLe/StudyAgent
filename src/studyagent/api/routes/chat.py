from __future__ import annotations

import json
import time
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from studyagent.agents.tutor.agent import TutorAgent
from studyagent.api.schemas.chat import ChatRequest, ConversationCreate, ConversationResponse, MessageResponse
from studyagent.db.engine import create_session_factory
from studyagent.db.models import Conversation, Message

router = APIRouter(prefix="/api/v1")


async def get_db() -> AsyncSession:
    factory = create_session_factory()
    async with factory() as session:
        yield session


async def _get_or_create_conversation(
    db: AsyncSession,
    conversation_id: str | None,
    user_id: str = "default",
) -> Conversation:
    if conversation_id:
        conv = await db.get(Conversation, conversation_id)
        if conv:
            return conv

    conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="New Conversation",
        session_type="teaching",
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


@router.post("/chat/stream")
async def stream_chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    from starlette.responses import StreamingResponse

    conv = await _get_or_create_conversation(db, request.conversation_id)

    user_content = request.messages[-1]["content"] if request.messages else ""
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="user",
        content=user_content,
    )
    db.add(user_msg)

    if not conv.title or conv.title == "New Conversation":
        conv.title = user_content[:50]
    conv.message_count += 1
    conv.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
    await db.commit()

    tutor = TutorAgent()
    start = time.time()
    collected = []

    async def event_stream():
        async for token in tutor.stream(
            messages=request.messages,
            session_type=request.session_type,
        ):
            collected.append(token)
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        full_response = "".join(collected)
        latency = int((time.time() - start) * 1000)

        assistant_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conv.id,
            role="assistant",
            content=full_response,
            model_used=tutor.llm.config.model,
            latency_ms=latency,
        )
        factory = create_session_factory()
        async with factory() as save_session:
            save_session.add(assistant_msg)
            conv_update = await save_session.get(Conversation, conv.id)
            if conv_update:
                conv_update.message_count += 1
            await save_session.commit()

        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conv.id})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    req: ConversationCreate,
    db: AsyncSession = Depends(get_db),
):
    conv = Conversation(
        id=str(uuid.uuid4()),
        user_id="default",
        title=req.title,
        session_type=req.session_type,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        session_type=conv.session_type,
        message_count=conv.message_count,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
    )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    stmt = select(Conversation).order_by(Conversation.updated_at.desc()).limit(50)
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            session_type=c.session_type,
            message_count=c.message_count,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=list[MessageResponse])
async def get_messages(conversation_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]
