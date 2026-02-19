from sqlmodel import Session, select
from db import get_session
from models import Task
from typing import Optional
from datetime import datetime

async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[int] = None,
    status: Optional[str] = None
):
    """
    Updates an existing task for the specified user.
    """
    if not user_id or not task_id:
        return {"status": "error", "message": "Validation Error: 'user_id' and 'task_id' are required."}

    # Check if at least one field is provided for update
    if not any([title, description, due_date, priority, status]):
        return {"status": "error", "message": "Validation Error: At least one field must be provided for update."}

    # Validate priority
    if priority is not None and (priority < 1 or priority > 5):
        return {"status": "error", "message": "Validation Error: 'priority' must be between 1 and 5."}
    
    # Validate status
    if status is not None and status not in ["pending", "completed"]:
        return {"status": "error", "message": "Validation Error: 'status' must be 'pending' or 'completed'."}
    
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            return {"status": "error", "message": "Validation Error: 'due_date' must be in YYYY-MM-DD format."}

    try:
        with Session(get_session()) as session:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"status": "error", "message": f"Task not found: No task with ID '{task_id}' found for user '{user_id}'."}

            # Update fields if provided
            if title:
                task.title = title
            if description is not None: # Allow setting to null
                task.description = description
            if parsed_due_date:
                task.due_date = parsed_due_date
            if priority is not None:
                task.priority = priority
            if status:
                task.status = status
            
            task.updated_at = datetime.utcnow() # Update timestamp

            session.add(task)
            session.commit()
            session.refresh(task)
            return {
                "status": "success",
                "message": f"Task '{task_id}' updated successfully.",
                "task": task.dict()
            }
    except Exception as e:
        print(f"Error updating task {task_id} for user {user_id}: {e}")
        return {"status": "error", "message": f"Database Error: Failed to update task. {e}"}