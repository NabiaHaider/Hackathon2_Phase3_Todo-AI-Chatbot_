import asyncio
import json
import cohere
from typing import List, Dict, Any, Callable, Optional, AsyncGenerator
from mcp.registry import MCPToolRegistry
from db import get_session, engine
from models.chat import Conversation, Message
from sqlmodel import Session, select
from datetime import datetime

from agents.todo_agent import TodoAgent

class AgentRunner:
    """
    AI Agent runner. Orchestrates tool calls and manages the execution flow
    between the user, the Cohere LLM, and the MCP tools.
    """

    def __init__(self, cohere_client: cohere.Client, mcp_tool_registry: MCPToolRegistry):
        self.cohere_client = cohere_client
        self.mcp_tool_registry = mcp_tool_registry
        self.todo_agent = TodoAgent(self.cohere_client, self._get_function_tools())

    def _get_function_tools(self) -> List[Dict[str, Any]]:
        """
        Converts the MCPToolRegistry into a list of Cohere tool objects.
        """
        cohere_tools = []
        for name, func in self.mcp_tool_registry.get_all_tools().items():
            # ... (the tool schema generation logic)
            # Reusing the logic from the existing file for simplicity
            tool_schema = self._get_tool_schema(name)
            if tool_schema:
                cohere_tools.append({
                    "function": tool_schema
                })
        return cohere_tools

    def _get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the schema for a specific tool.
        """
        if name == "add_task":
            return {
                "name": "add_task",
                "description": "Adds a new task to the user's todo list.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user."},
                        "title": {"type": "string", "description": "The title of the task."},
                        "description": {"type": "string", "description": "A detailed description of the task.", "nullable": True},
                        "due_date": {"type": "string", "description": "Optional due date for the task (YYYY-MM-DD).", "nullable": True},
                        "priority": {"type": "integer", "description": "Optional priority level for the task (1-5, 1 being highest).", "nullable": True},
                    },
                    "required": ["user_id", "title"],
                },
            }
        elif name == "list_tasks":
            return {
                "name": "list_tasks",
                "description": "Lists all tasks for a given user, with optional filtering by status or priority.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user."},
                        "status": {"type": "string", "description": "Optional filter for task status (e.g., 'pending', 'completed').", "nullable": True},
                        "priority": {"type": "integer", "description": "Optional filter for task priority.", "nullable": True},
                    },
                    "required": ["user_id"],
                },
            }
        # ... and so on for other tools. 
        # I'll preserve the original full set below for safety.
        elif name == "update_task":
            return {
                "name": "update_task",
                "description": "Updates an existing task for a user. Can change title, description, due date, priority, or status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user."},
                        "task_id": {"type": "integer", "description": "The ID of the task to update."},
                        "title": {"type": "string", "description": "New title for the task.", "nullable": True},
                        "description": {"type": "string", "description": "New description for the task.", "nullable": True},
                        "due_date": {"type": "string", "description": "New due date for the task (YYYY-MM-DD).", "nullable": True},
                        "priority": {"type": "integer", "description": "New priority level for the task (1-5, 1 being highest).", "nullable": True},
                        "status": {"type": "string", "description": "New status for the task (e.g., 'pending', 'completed').", "nullable": True},
                    },
                    "required": ["user_id", "task_id"],
                },
            }
        elif name == "complete_task":
            return {
                "name": "complete_task",
                "description": "Marks a task as completed for a given user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user."},
                        "task_id": {"type": "integer", "description": "The ID of the task to mark as completed."},
                    },
                    "required": ["user_id", "task_id"],
                },
            }
        elif name == "delete_task":
            return {
                "name": "delete_task",
                "description": "Deletes a task for a given user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user."},
                        "task_id": {"type": "integer", "description": "The ID of the task to delete."},
                    },
                    "required": ["user_id", "task_id"],
                },
            }
        elif name == "error_handling_skill":
            return {
                "name": "error_handling_skill",
                "description": "Handles errors gracefully and provides user-friendly messages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user."},
                        "error_message": {"type": "string", "description": "The error message to handle."},
                    },
                    "required": ["user_id", "error_message"],
                },
            }
        elif name == "user_greeting_skill":
            return {
                "name": "user_greeting_skill",
                "description": "Greets the user and provides a personalized welcome message.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The ID of the user."},
                        "user_name": {"type": "string", "description": "The name of the user.", "nullable": True},
                    },
                    "required": ["user_id"],
                },
            }
        else:
            return {
                "name": name,
                "description": f"A tool for {name}.",
                "parameters": {"type": "object", "properties": {}},
            }

    async def _get_or_create_conversation(self, user_id: str, session: Session) -> Conversation:
        conversation = session.exec(select(Conversation).where(Conversation.user_id == user_id)).first()
        if not conversation:
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        return conversation

    async def _load_conversation_history(self, session: Session, user_id: str, conversation_id: int) -> List[Dict[str, Any]]:
        messages = []
        db_messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()
        
        for msg in db_messages:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    async def _save_message(self, session: Session, user_id: str, conversation_id: int, role: str, content: str):
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        session.add(message)
        session.commit()
        session.refresh(message)

    async def run_chat_completion(self, user_id: Any, user_message: str) -> AsyncGenerator[str, None]:
        """
        Executes a full chat completion turn, handling tool calls.
        """
        # Ensure user_id is a string as expected by the database schema
        user_id_str = str(user_id)

        with Session(engine) as session:
            conversation = await self._get_or_create_conversation(user_id_str, session)
            history = await self._load_conversation_history(session, user_id_str, conversation.id)
            
            await self._save_message(session, user_id_str, conversation.id, "user", user_message)
            history.append({"role": "user", "content": user_message})

            # Run initial conversation
            response_message = await self.todo_agent.run_conversation(
                user_id_str, history, self.todo_agent.get_tools()
            )
            history.append(response_message)

            tool_calls = response_message.get("tool_calls")
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_to_call = self.mcp_tool_registry.get_tool(function_name)

                    if function_to_call:
                        try:
                            function_args = json.loads(tool_call["function"]["arguments"])
                            function_args['user_id'] = user_id_str 
                            
                            tool_output = await function_to_call(**function_args)
                            
                            # Streaming tool execution feedback
                            yield f"data: {json.dumps({ 'type': 'tool_code', 'name': function_name, 'output': tool_output })}\n\n"

                            history.append(
                                {
                                    "tool_call_id": tool_call.get("id"),
                                    "role": "tool",
                                    "name": function_name,
                                    "content": json.dumps(tool_output),
                                }
                            )
                        except Exception as e:
                            error_message = f"Error executing tool {function_name}: {e}"
                            try:
                                error_handling_func = self.mcp_tool_registry.get_tool("error_handling_skill")
                                error_output = await error_handling_func(user_id=user_id_str, error_message=error_message)
                                msg = error_output.get('user_facing_message', error_message)
                            except:
                                msg = error_message
                                
                            yield f"data: {json.dumps({ 'type': 'error', 'message': msg })}\n\n"
                            history.append(
                                {
                                    "tool_call_id": tool_call.get("id"),
                                    "role": "tool",
                                    "name": function_name,
                                    "content": json.dumps({"error": error_message}),
                                }
                            )
                    else:
                        yield f"data: {json.dumps({ 'type': 'error', 'message': f'Agent tried to call an unknown tool: {function_name}' })}\n\n"
                        history.append(
                            {"role": "assistant", "content": f"Error: Agent tried to call an unknown tool: {function_name}"}
                        )
                
                # Second response after tool calls
                second_response = await self.todo_agent.run_conversation(
                    user_id_str, history, self.todo_agent.get_tools()
                )
                assistant_content = second_response.get("content", "")
                await self._save_message(session, user_id_str, conversation.id, "assistant", assistant_content)
                yield f"data: {json.dumps({ 'type': 'final_response', 'message': assistant_content })}\n\n"
            else:
                assistant_content = response_message.get("content", "")
                await self._save_message(session, user_id_str, conversation.id, "assistant", assistant_content)
                yield f"data: {json.dumps({ 'type': 'final_response', 'message': assistant_content })}\n\n"

