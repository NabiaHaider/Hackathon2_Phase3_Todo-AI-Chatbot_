# `update_task_skill.md` - Update Task MCP Tool Specification

## Name
`update_task`

## Purpose
To modify one or more attributes of an existing task for a specific user. This includes changing the title, description, due date, priority, or status of a task.

## Input Schema
The `update_task` tool accepts a JSON object with the following parameters:

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
      "description": "Unique identifier of the task to be updated."
    },
    "title": {
      "type": "string",
      "description": "Optional new title for the task.",
      "nullable": true
    },
    "description": {
      "type": "string",
      "description": "Optional new detailed description for the task.",
      "nullable": true
    },
    "due_date": {
      "type": "string",
      "format": "date",
      "description": "Optional new due date for the task in 'YYYY-MM-DD' format.",
      "nullable": true
    },
    "priority": {
      "type": "integer",
      "description": "Optional new priority level for the task (1-5).",
      "minimum": 1,
      "maximum": 5,
      "nullable": true
    },
    "status": {
      "type": "string",
      "description": "Optional new status for the task.",
      "enum": ["pending", "completed"],
      "nullable": true
    }
  },
  "required": [
    "user_id",
    "task_id"
  ]
}
```

## Output Schema
The `update_task` tool returns a JSON object indicating the status of the operation and the updated task details.

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
      "description": "Details of the updated task.",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier for the updated task."
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
          "description": "Current status of the task, e.g., 'pending', 'completed'.",
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
3.  **At least one update field**: At least one of `title`, `description`, `due_date`, `priority`, or `status` must be provided.
4.  **Task Existence**: The `task_id` must correspond to an existing task owned by the specified `user_id`.
5.  **`title`**: If provided, must be a non-empty string, maximum length 255 characters.
6.  **`description`**: If provided, must be a string, maximum length 1024 characters.
7.  **`due_date`**: If provided, must be a valid date string in 'YYYY-MM-DD' format.
8.  **`priority`**: If provided, must be an integer between 1 and 5 (inclusive).
9.  **`status`**: If provided, must be one of "pending" or "completed".

## Error Handling
The tool will return an `error` status in its JSON output for the following scenarios:
-   **Invalid Input**: If any validation rule is violated (e.g., missing `user_id`, empty `task_id`, no update fields provided, invalid `due_date` format, out-of-range `priority`, invalid `status` enum value). The `message` field will describe the specific validation error.
-   **Task Not Found**: If no task with the given `task_id` exists for the specified `user_id`.
-   **Database Error**: If the SQLModel interaction fails (e.g., connection issue, update failure). The `message` field will contain a generic error description, avoiding sensitive database details.
-   **Internal Server Error**: Any unhandled exception during the execution of the tool.

## Security (User Isolation)
-   **Mandatory `user_id`**: Every call to `update_task` *must* include a `user_id`.
-   **Ownership Verification**: Before updating a task, the tool will rigorously verify that the `task_id` belongs to the provided `user_id`.
-   **No Cross-User Modification**: It is strictly enforced that a user cannot update a task belonging to another `user_id`. The SQLModel query will include both `task_id` and `user_id` in its `WHERE` clause for all update operations.

## Stateless Execution
The `update_task` tool is stateless. Each invocation processes the provided input parameters independently, performs the database update, and returns a result. It does not store any internal state between calls or rely on previous interactions. The `user_id` and `task_id` are passed with each call to maintain context for data ownership and modification.

## Example Tool Call (OpenAI Function Calling format)
```json
{
  "tool_calls": [
    {
      "id": "call_mno345",
      "function": {
        "name": "update_task",
        "arguments": "{"user_id": "usr_abcde", "task_id": "tsk_001", "title": "Buy organic groceries", "priority": 1}"
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
  "message": "Task 'tsk_001' updated successfully.",
  "task": {
    "id": "tsk_001",
    "user_id": "usr_abcde",
    "title": "Buy organic groceries",
    "description": "Milk, eggs, bread",
    "due_date": "2026-02-15",
    "priority": 1,
    "status": "pending",
    "created_at": "2026-02-11T10:30:00Z",
    "updated_at": "2026-02-11T12:00:00Z"
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

**Error (No Update Fields):**
```json
{
  "status": "error",
  "message": "Validation Error: At least one field (title, description, due_date, priority, status) must be provided for update."
}
```
