from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
import datetime

class Conversation(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: Optional[int] = Field(default=None, foreign_key="conversation.id")
    user_id: str = Field(index=True)
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
