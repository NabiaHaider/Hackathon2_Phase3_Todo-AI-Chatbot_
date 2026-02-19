from typing import Dict, Any, Optional
import re

class ToolDecisionEngine:
    """
    Intent detection logic, tool selection strategy, and multi-step reasoning rules.
    This class helps in understanding user requests and mapping them to appropriate MCP tools.
    In a fully integrated system, much of this logic would be handled by the LLM itself
    via function calling, but this provides a structured approach for more explicit control
    or for agents with less advanced function calling capabilities.
    """

    def __init__(self, available_tools: Dict[str, Any]):
        self.available_tools = available_tools

    def detect_intent_and_extract_params(self, user_input: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Detects the user's intent and extracts parameters for tool calls from the user input.
        This is a simplified rule-based approach. In a production system, this would be
        heavily reliant on the LLM's function calling capabilities.
        """
        user_input_lower = user_input.lower()
        
        # Add Task Intent
        if any(keyword in user_input_lower for keyword in ["add task", "create task", "new task", "make task"]):
            title_match = re.search(r"(?:add|create|make) task (?:with title )?['"]?([^'"]+)['"]?(?: due on (\d{4}-\d{2}-\d{2}))?", user_input_lower)
            if title_match:
                title = title_match.group(1).strip()
                due_date = title_match.group(2) if title_match.group(2) else None
                return {
                    "tool_name": "add_task",
                    "params": {"user_id": user_id, "title": title, "due_date": due_date}
                }
            # Fallback if only "add task" is mentioned
            return {"tool_name": "add_task", "params": {"user_id": user_id}}

        # List Tasks Intent
        if any(keyword in user_input_lower for keyword in ["list tasks", "show tasks", "my tasks", "what are my todos"]):
            status_match = re.search(r"tasks (?:with status|that are) (pending|completed)", user_input_lower)
            status = status_match.group(1) if status_match else None
            return {
                "tool_name": "list_tasks",
                "params": {"user_id": user_id, "status": status}
            }

        # Complete Task Intent
        if any(keyword in user_input_lower for keyword in ["complete task", "finish task", "done with task"]):
            task_id_match = re.search(r"(?:complete|finish|done with) task (?:with id )?['"]?([\w-]+)['"]?", user_input_lower)
            if task_id_match:
                task_id = task_id_match.group(1)
                return {
                    "tool_name": "complete_task",
                    "params": {"user_id": user_id, "task_id": task_id}
                }
            return {"tool_name": "complete_task", "params": {"user_id": user_id}} # Needs clarification

        # Delete Task Intent
        if any(keyword in user_input_lower for keyword in ["delete task", "remove task", "get rid of task"]):
            task_id_match = re.search(r"(?:delete|remove|get rid of) task (?:with id )?['"]?([\w-]+)['"]?", user_input_lower)
            if task_id_match:
                task_id = task_id_match.group(1)
                return {
                    "tool_name": "delete_task",
                    "params": {"user_id": user_id, "task_id": task_id}
                }
            return {"tool_name": "delete_task", "params": {"user_id": user_id}} # Needs clarification

        # Update Task Intent
        if any(keyword in user_input_lower for keyword in ["update task", "change task", "modify task"]):
            task_id_match = re.search(r"(?:update|change|modify) task (?:with id )?['"]?([\w-]+)['"]?", user_input_lower)
            if task_id_match:
                task_id = task_id_match.group(1)
                # This is very simplified; in reality, LLM would extract specific update fields
                return {
                    "tool_name": "update_task",
                    "params": {"user_id": user_id, "task_id": task_id}
                }
            return {"tool_name": "update_task", "params": {"user_id": user_id}} # Needs clarification


        return None