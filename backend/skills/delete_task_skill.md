# `delete_task_skill.md` - Delete Task MCP Tool Specification

## Name
`delete_task`

## Purpose
To permanently remove a specific task for a specific user from the Todo AI Chatbot's database. This is an irreversible operation.

## Input Schema
The `delete_task` tool accepts a JSON object with the following parameters:

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
      "description": "Unique identifier of the task to be deleted."
    }
  },
  "required": [
    "user_id",
    "task_id"
  ]
}
```

## Output Schema
The `delete_task` tool returns a JSON object indicating the status of the operation.

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
    }
  },
  "required": ["status", "message"]
}
```

## Validation Rules
1.  **`user_id`**: Must be a non-empty string.
2.  **`task_id`**: Must be a non-empty string.
3.  **Task Existence**: The `task_id` must correspond to an existing task owned by the specified `user_id`.

## Error Handling
The tool will return an `error` status in its JSON output for the following scenarios:
-   **Invalid Input**: If any validation rule is violated (e.g., missing `user_id`, empty `task_id`). The `message` field will describe the specific validation error.
-   **Task Not Found**: If no task with the given `task_id` exists for the specified `user_id`. The `message` will indicate the task was not found.
-   **Database Error**: If the SQLModel interaction fails (e.g., connection issue, deletion failure). The `message` field will contain a generic error description, avoiding sensitive database details.
-   **Internal Server Error**: Any unhandled exception during the execution of the tool.

## Security (User Isolation)
-   **Mandatory `user_id`**: Every call to `delete_task` *must* include a `user_id`.
-   **Ownership Verification**: Before deleting a task, the tool will rigorously verify that the `task_id` belongs to the provided `user_id`.
-   **No Cross-User Deletion**: It is strictly enforced that a user cannot delete a task belonging to another `user_id`. The SQLModel query will include both `task_id` and `user_id` in its `WHERE` clause for the delete operation.

## Stateless Execution
The `delete_task` tool is stateless. Each invocation processes the provided input parameters independently, performs the database deletion, and returns a result. It does not store any internal state between calls or rely on previous interactions. The `user_id` and `task_id` are passed with each call to maintain context for data ownership and modification.

## Example Tool Call (OpenAI Function Calling format)
```json
{
  "tool_calls": [
    {
      "id": "call_jkl012",
      "function": {
        "name": "delete_task",
        "arguments": "{"user_id": "usr_abcde", "task_id": "tsk_002"}"
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
  "message": "Task 'tsk_002' deleted successfully."
}
```

**Error (Task Not Found):**
```json
{
  "status": "error",
  "message": "Task not found: No task with ID 'tsk_999' found for user 'usr_abcde'."
}
```

**Error (Database):**
```json
{
  "status": "error",
  "message": "Database Error: Failed to delete task. Please try again."
}
```
