from sqlmodel import Session, select
from db import get_session
from models import Task
from typing import Optional
from datetime import datetime

async def complete_task(user_id: str, task_id: str):
    """
    Marks an existing task as completed for the specified user.
    """
    if not user_id or not task_id:
        return {"status": "error", "message": "Validation Error: 'user_id' and 'task_id' are required."}

    try:
        with Session(get_session()) as session:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"status": "error", "message": f"Task not found: No task with ID '{task_id}' found for user '{user_id}'."}
            
            if task.status == "completed":
                return {"status": "error", "message": f"Task '{task_id}' is already completed."}

            task.status = "completed"
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)
            return {
                "status": "success",
                "message": f"Task '{task_id}' marked as completed.",
                "task": task.dict()
            }
    except Exception as e:
        print(f"Error completing task {task_id} for user {user_id}: {e}")
        return {"status": "error", "message": f"Database Error: Failed to complete task. {e}"}