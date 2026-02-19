from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, Column, DateTime # Import Column and DateTime


class Task(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False) # Renamed from is_completed to completed
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field( # Added updated_at field
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)
    )

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="tasks")