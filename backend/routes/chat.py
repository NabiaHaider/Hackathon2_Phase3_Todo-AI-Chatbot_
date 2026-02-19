from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
import asyncio
from typing import AsyncGenerator
from auth.jwt import get_current_user # Corrected import
from main import agent_runner # Import the globally initialized agent_runner

router = APIRouter()

@router.post("/v1/chat")
async def chat_endpoint(request: Request, user_id: str = Depends(get_current_user)) -> StreamingResponse:
    # Read the incoming message body
    body = await request.json()
    user_message = body.get("message")

    if not user_message:
        return StreamingResponse(
            (f"data: {{ \"type\": \"error\", \"message\": \"User message is required.\" }}\n\n",),
            media_type="text/event-stream"
        )

    # Use the globally initialized agent_runner to process the chat
    return StreamingResponse(agent_runner.run_chat_completion(user_id, user_message), media_type="text/event-stream")