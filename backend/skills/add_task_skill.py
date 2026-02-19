from sqlmodel import Session
from db import get_session
from models import Task # Assuming Task model is in backend/models.py
from datetime import datetime
from typing import Optional

async def add_task(user_id: str, title: str, description: Optional[str] = None, due_date: Optional[str] = None, priority: Optional[int] = None):
    """
    Adds a new task for the specified user.
    """
    if not user_id or not title:
        return {"status": "error", "message": "Validation Error: 'user_id' and 'title' are required."}

    # Basic validation for priority and due_date
    if priority is not None and (priority < 1 or priority > 5):
        return {"status": "error", "message": "Validation Error: 'priority' must be between 1 and 5."}
    
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            return {"status": "error", "message": "Validation Error: 'due_date' must be in YYYY-MM-DD format."}

    try:
        with Session(get_session()) as session:
            new_task = Task(
                user_id=user_id,
                title=title,
                description=description,
                due_date=parsed_due_date,
                priority=priority,
                status="pending" # Default status
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)
            return {
                "status": "success",
                "message": f"Task '{title}' created successfully for user {user_id}.",
                "task": new_task.dict()
            }
    except Exception as e:
        # Log the exception for debugging
        print(f"Error adding task for user {user_id}: {e}")
        return {"status": "error", "message": f"Database Error: Failed to add task. {e}"}
