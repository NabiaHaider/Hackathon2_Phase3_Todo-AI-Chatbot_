from sqlmodel import Session, select
from db import get_session
from models import Task
from typing import Optional, List

async def list_tasks(user_id: str, status: Optional[str] = None, priority: Optional[int] = None, limit: int = 10, offset: int = 0):
    """
    Lists tasks for the specified user, with optional filters.
    """
    if not user_id:
        return {"status": "error", "message": "Validation Error: 'user_id' is required."}

    # Validate status
    if status and status not in ["pending", "completed", "all"]:
        return {"status": "error", "message": "Validation Error: 'status' must be 'pending', 'completed', or 'all'."}
    
    # Validate priority
    if priority is not None and (priority < 1 or priority > 5):
        return {"status": "error", "message": "Validation Error: 'priority' must be between 1 and 5."}

    try:
        with Session(get_session()) as session:
            query = select(Task).where(Task.user_id == user_id)

            if status and status != "all":
                query = query.where(Task.status == status)
            if priority is not None:
                query = query.where(Task.priority == priority)
            
            # Get total count before applying limit/offset
            total_count = len(session.exec(query).all())

            query = query.offset(offset).limit(limit)
            tasks = session.exec(query).all()

            task_dicts = [task.dict() for task in tasks] # Convert SQLModel objects to dicts

            return {
                "status": "success",
                "message": f"Successfully retrieved {len(tasks)} tasks.",
                "tasks": task_dicts,
                "total_count": total_count
            }
    except Exception as e:
        print(f"Error listing tasks for user {user_id}: {e}")
        return {"status": "error", "message": f"Database Error: Failed to list tasks. {e}"}
