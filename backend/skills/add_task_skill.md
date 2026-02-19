# `add_task_skill.md` - Add Task MCP Tool Specification

## Name
`add_task`

## Purpose
To create and persist a new task for a specific user in the Todo AI Chatbot's database. This tool encapsulates the logic required to receive task details and store them, ensuring user data isolation.

## Input Schema
The `add_task` tool accepts a JSON object with the following parameters:

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "Unique identifier for the user creating the task. Required for user isolation."
    },
    "title": {
      "type": "string",
      "description": "The title or brief description of the task. Must be non-empty."
    },
    "description": {
      "type": "string",
      "description": "An optional, more detailed description of the task.",
      "nullable": true
    },
    "due_date": {
      "type": "string",
      "format": "date",
      "description": "Optional due date for the task in 'YYYY-MM-DD' format.",
      "nullable": true
    },
    "priority": {
      "type": "integer",
      "description": "Optional priority level for the task (e.g., 1 for high, 5 for low).",
      "minimum": 1,
      "maximum": 5,
      "nullable": true
    }
  },
  "required": [
    "user_id",
    "title"
  ]
}
```

## Output Schema
The `add_task` tool returns a JSON object indicating the status of the operation and the details of the newly created task.

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
      "description": "Details of the newly created task.",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier for the created task."
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
          "description": "Current status of the task, e.g., 'pending'.",
          "enum": ["pending", "completed"]
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp when the task was created."
        }
      },
      "required": ["id", "user_id", "title", "status", "created_at"]
    }
  },
  "required": ["status", "message"]
}
```

## Validation Rules
1.  **`user_id`**: Must be a non-empty string.
2.  **`title`**: Must be a non-empty string, maximum length 255 characters.
3.  **`description`**: If provided, must be a string, maximum length 1024 characters.
4.  **`due_date`**: If provided, must be a valid date string in 'YYYY-MM-DD' format. Past dates are allowed, but the agent should guide users for future dates.
5.  **`priority`**: If provided, must be an integer between 1 and 5 (inclusive).

## Error Handling
The tool will return an `error` status in its JSON output for the following scenarios:
-   **Invalid Input**: If any validation rule is violated (e.g., missing `user_id`, empty `title`, invalid `due_date` format, out-of-range `priority`). The `message` field will describe the specific validation error.
-   **Database Error**: If the SQLModel interaction fails (e.g., connection issue, integrity constraint violation). The `message` field will contain a generic error description, avoiding sensitive database details.
-   **Internal Server Error**: Any unhandled exception during the execution of the tool.

## Security (User Isolation)
-   **Mandatory `user_id`**: Every call to `add_task` *must* include a `user_id`.
-   **Data Scoping**: The task creation process will explicitly link the new task to the provided `user_id`. SQLModel queries will inherently filter and restrict data access to ensure a user can only add tasks associated with their `user_id`.
-   **No Cross-User Access**: The underlying database interaction (via SQLModel) is designed to prevent a task from being created or associated with a `user_id` other than the one authenticated for the request.

## Stateless Execution
The `add_task` tool is stateless. Each invocation processes the provided input parameters independently, performs the database operation, and returns a result. It does not store any internal state between calls or rely on previous interactions. The `user_id` is passed with each call to maintain context for data ownership.

## Example Tool Call (OpenAI Function Calling format)
```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "function": {
        "name": "add_task",
        "arguments": "{"user_id": "usr_abcde", "title": "Buy groceries", "description": "Milk, eggs, bread", "due_date": "2026-02-15", "priority": 2}"
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
  "message": "Task 'Buy groceries' created successfully.",
  "task": {
    "id": "tsk_001",
    "user_id": "usr_abcde",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "due_date": "2026-02-15",
    "priority": 2,
    "status": "pending",
    "created_at": "2026-02-11T10:30:00Z"
  }
}
```

**Error (Validation):**
```json
{
  "status": "error",
  "message": "Validation Error: 'title' is required and cannot be empty."
}
```

**Error (Database):**
```json
{
  "status": "error",
  "message": "Database Error: Failed to save task. Please try again."
}
```
