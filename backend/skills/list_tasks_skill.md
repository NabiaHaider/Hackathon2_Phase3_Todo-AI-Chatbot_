# `list_tasks_skill.md` - List Tasks MCP Tool Specification

## Name
`list_tasks`

## Purpose
To retrieve a list of tasks for a specific user, with optional filtering based on task status or priority. This tool supports users in viewing and managing their existing tasks.

## Input Schema
The `list_tasks` tool accepts a JSON object with the following parameters:

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "Unique identifier for the user whose tasks are to be listed. Required for user isolation."
    },
    "status": {
      "type": "string",
      "description": "Optional filter to retrieve tasks by their current status.",
      "enum": ["pending", "completed", "all"],
      "default": "all",
      "nullable": true
    },
    "priority": {
      "type": "integer",
      "description": "Optional filter to retrieve tasks by their priority level (1-5).",
      "minimum": 1,
      "maximum": 5,
      "nullable": true
    },
    "limit": {
      "type": "integer",
      "description": "Optional limit on the number of tasks to return.",
      "minimum": 1,
      "default": 10,
      "nullable": true
    },
    "offset": {
      "type": "integer",
      "description": "Optional offset for pagination, indicating how many tasks to skip.",
      "minimum": 0,
      "default": 0,
      "nullable": true
    }
  },
  "required": [
    "user_id"
  ]
}
```

## Output Schema
The `list_tasks` tool returns a JSON object containing a list of tasks that match the criteria.

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
    "tasks": {
      "type": "array",
      "description": "A list of task objects that match the criteria.",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique identifier for the task."
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
            "description": "Timestamp when the task was last updated.",
            "nullable": true
          }
        },
        "required": ["id", "user_id", "title", "status", "created_at"]
      }
    },
    "total_count": {
      "type": "integer",
      "description": "Total number of tasks matching the filters, disregarding limit/offset.",
      "minimum": 0
    }
  },
  "required": ["status", "message", "tasks", "total_count"]
}
```

## Validation Rules
1.  **`user_id`**: Must be a non-empty string.
2.  **`status`**: If provided, must be one of "pending", "completed", or "all".
3.  **`priority`**: If provided, must be an integer between 1 and 5 (inclusive).
4.  **`limit`**: If provided, must be an integer greater than or equal to 1.
5.  **`offset`**: If provided, must be an integer greater than or equal to 0.

## Error Handling
The tool will return an `error` status in its JSON output for the following scenarios:
-   **Invalid Input**: If any validation rule is violated (e.g., missing `user_id`, invalid `status` enum value, out-of-range `priority`, `limit`, or `offset`). The `message` field will describe the specific validation error.
-   **Database Error**: If the SQLModel interaction fails (e.g., connection issue). The `message` field will contain a generic error description, avoiding sensitive database details.
-   **Internal Server Error**: Any unhandled exception during the execution of the tool.

## Security (User Isolation)
-   **Mandatory `user_id`**: Every call to `list_tasks` *must* include a `user_id`.
-   **Data Scoping**: The underlying SQLModel query will apply a mandatory filter on `user_id`, ensuring that only tasks belonging to the specified `user_id` are retrieved.
-   **No Cross-User Access**: It is strictly enforced that a user cannot query or view tasks belonging to another `user_id`.

## Stateless Execution
The `list_tasks` tool is stateless. Each invocation processes the provided input parameters independently, executes the database query, and returns a result. It does not store any internal state between calls or rely on previous interactions. The `user_id` is passed with each call to maintain context for data ownership.

## Example Tool Call (OpenAI Function Calling format)
```json
{
  "tool_calls": [
    {
      "id": "call_def456",
      "function": {
        "name": "list_tasks",
        "arguments": "{"user_id": "usr_abcde", "status": "pending", "limit": 5}"
      },
      "type": "function"
    }
  ]
}
```

## Example Response
**Success (Tasks Found):**
```json
{
  "status": "success",
  "message": "Successfully retrieved 2 pending tasks.",
  "tasks": [
    {
      "id": "tsk_001",
      "user_id": "usr_abcde",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "due_date": "2026-02-15",
      "priority": 2,
      "status": "pending",
      "created_at": "2026-02-11T10:30:00Z",
      "updated_at": "2026-02-11T10:30:00Z"
    },
    {
      "id": "tsk_003",
      "user_id": "usr_abcde",
      "title": "Call doctor",
      "description": null,
      "due_date": "2026-02-12",
      "priority": 1,
      "status": "pending",
      "created_at": "2026-02-10T09:00:00Z",
      "updated_at": "2026-02-10T09:00:00Z"
    }
  ],
  "total_count": 2
}
```

**Success (No Tasks Found):**
```json
{
  "status": "success",
  "message": "No tasks found matching the criteria.",
  "tasks": [],
  "total_count": 0
}
```

**Error (Validation):**
```json
{
  "status": "error",
  "message": "Validation Error: 'status' must be one of 'pending', 'completed', or 'all'."
}
```
