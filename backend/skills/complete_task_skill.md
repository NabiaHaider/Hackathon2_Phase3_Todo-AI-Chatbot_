# `complete_task_skill.md` - Complete Task MCP Tool Specification

## Name
`complete_task`

## Purpose
To mark an existing task as completed for a specific user. This tool modifies the status of a task, indicating it has been finished.

## Input Schema
The `complete_task` tool accepts a JSON object with the following parameters:

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "Unique identifier for the user who owns the task. Required for user isolation."
    },
    "task_id": {
      "type": "string",
      "description": "Unique identifier of the task to be marked as completed."
    }
  },
  "required": [
    "user_id",
    "task_id"
  ]
}
```

## Output Schema
The `complete_task` tool returns a JSON object indicating the status of the operation and the updated task details.

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "description": "Status of the operation. 'success' or 'error'."
    },
    "message": {
      "type": "string",
      "description": "A human-readable message about the operation result."
    },
    "task": {
      "type": "object",
      "description": "Details of the updated task, with status set to 'completed'.",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier for the completed task."
        },
        "user_id": {
          "type": "string",
          "description": "User ID associated with the task."
        },
        "title": {
          "type": "string",
          "description": "Title of the task."
        },
        "description": {
          "type": "string",
          "description": "Description of the task.",
          "nullable": true
        },
        "due_date": {
          "type": "string",
          "format": "date",
          "description": "Due date of the task.",
          "nullable": true
        },
        "priority": {
          "type": "integer",
          "description": "Priority of the task.",
          "nullable": true
        },
        "status": {
          "type": "string",
          "description": "Current status of the task, always 'completed' on success.",
          "enum": ["pending", "completed"]
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp when the task was created."
        },
        "updated_at": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp when the task was last updated."
        }
      },
      "required": ["id", "user_id", "title", "status", "created_at", "updated_at"]
    }
  },
  "required": ["status", "message"]
}
```

## Validation Rules
1.  **`user_id`**: Must be a non-empty string.
2.  **`task_id`**: Must be a non-empty string.
3.  **Task Existence**: The `task_id` must correspond to an existing task owned by the specified `user_id`.
4.  **Task Status**: The task must not already be in the 'completed' status.

## Error Handling
The tool will return an `error` status in its JSON output for the following scenarios:
-   **Invalid Input**: If any validation rule is violated (e.g., missing `user_id`, empty `task_id`). The `message` field will describe the specific validation error.
-   **Task Not Found**: If no task with the given `task_id` exists for the specified `user_id`.
-   **Task Already Completed**: If the task identified by `task_id` is already in 'completed' status.
-   **Database Error**: If the SQLModel interaction fails (e.g., connection issue, update failure). The `message` field will contain a generic error description, avoiding sensitive database details.
-   **Internal Server Error**: Any unhandled exception during the execution of the tool.

## Security (User Isolation)
-   **Mandatory `user_id`**: Every call to `complete_task` *must* include a `user_id`.
-   **Ownership Verification**: Before marking a task as completed, the tool will rigorously verify that the `task_id` belongs to the provided `user_id`.
-   **No Cross-User Modification**: It is strictly enforced that a user cannot complete a task belonging to another `user_id`. The SQLModel query will include both `task_id` and `user_id` in its `WHERE` clause for all update operations.

## Stateless Execution
The `complete_task` tool is stateless. Each invocation processes the provided input parameters independently, performs the database update, and returns a result. It does not store any internal state between calls or rely on previous interactions. The `user_id` and `task_id` are passed with each call to maintain context for data ownership and modification.

## Example Tool Call (OpenAI Function Calling format)
```json
{
  "tool_calls": [
    {
      "id": "call_ghi789",
      "function": {
        "name": "complete_task",
        "arguments": "{"user_id": "usr_abcde", "task_id": "tsk_001"}"
      },
      "type": "function"
    }
  ]
}
```

## Example Response
**Success:**
```json
{
  "status": "success",
  "message": "Task 'tsk_001' marked as completed.",
  "task": {
    "id": "tsk_001",
    "user_id": "usr_abcde",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "due_date": "2026-02-15",
    "priority": 2,
    "status": "completed",
    "created_at": "2026-02-11T10:30:00Z",
    "updated_at": "2026-02-11T11:00:00Z"
  }
}
```

**Error (Task Not Found):**
```json
{
  "status": "error",
  "message": "Task not found: No task with ID 'tsk_999' found for user 'usr_abcde'."
}
```

**Error (Task Already Completed):**
```json
{
  "status": "error",
  "message": "Task 'tsk_001' is already completed."
}
```
