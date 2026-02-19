from pydantic import BaseModel
from typing import Optional

class ChatMessageRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    response: str

class ErrorDetail(BaseModel):
    code: str
    message: str

class GlobalError(BaseModel):
    detail: ErrorDetail
