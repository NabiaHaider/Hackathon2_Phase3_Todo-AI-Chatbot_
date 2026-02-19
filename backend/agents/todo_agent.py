import cohere
import json
from typing import List, Callable, Dict, Any, Optional

from agents.agent_instructions import AgentInstructions


class TodoAgent:
    """
    Main AI Agent definition for the Todo AI Chatbot, using Cohere as the LLM.
    This agent is responsible for understanding natural language requests
    related to todo tasks and delegating them to appropriate MCP tools.
    """

    def __init__(self, client: cohere.Client, tools: List[Dict[str, Any]]):
        self.client = client
        self.tools = tools
        self.model = "command-r" # Updated from deprecated model

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Returns the list of available tools for this agent.
        """
        return self.tools

    def get_system_prompt(self) -> str:
        """
        Retrieves the detailed system prompt from the AgentInstructions class.
        This prompt guides the agent's overall behavior and persona.
        """
        return AgentInstructions.get_detailed_instructions()

    async def run_conversation(
        self,
        user_id: str,
        messages: List[Dict[str, Any]],
        available_tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Runs a single turn of conversation with the Cohere LLM.
        This method sends the conversation history and available tools to the model
        and returns its response, including any tool calls.
        """
        
        # Cohere's chat endpoint takes a "message" and a "chat_history"
        # The last message is the "user_message", others go into "chat_history"
        user_message_content = messages[-1]["content"]
        
        # chat_history needs to be in Cohere's specific format
        cohere_chat_history = []
        for msg in messages[:-1]: # All messages except the last one
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                cohere_chat_history.append({"role": "User", "message": content})
            elif role == "assistant":
                # Check if it was a tool call (stored as content in some cases or has tool_calls)
                if msg.get("tool_calls"):
                    # Cohere history for tool calls is complex, for simplicity we represent it as Chatbot message
                    # Real Cohere Chat history with tools requires TOOL and CHATBOT roles with tool_results.
                    cohere_chat_history.append({"role": "Chatbot", "message": content or "Calling tools..."})
                else:
                    cohere_chat_history.append({"role": "Chatbot", "message": content})
            elif role == "tool":
                # Cohere doesn't have a simple 'Tool' role in chat_history without specific tool_results list
                # Mapping to 'User' or 'Chatbot' as a workaround if needed, but better to keep it clean.
                # For now, we omit tool results from chat_history or map them to User (as system/env response)
                cohere_chat_history.append({"role": "User", "message": f"Tool Output: {content}"})
        
        # For Cohere Chat API, system message is part of `preamble`.
        preamble = self.get_system_prompt()
        
        try:
            # Note: Cohere SDK v5+ might use chat_stream or chat
            response = self.client.chat(
                model=self.model,
                message=user_message_content,
                chat_history=cohere_chat_history,
                tools=available_tools if available_tools else None,
                preamble=preamble,
                temperature=0.7,
            )
        except Exception as e:
            return {"role": "assistant", "content": f"An error occurred with Cohere: {str(e)}"}

        # Adapt Cohere's response format
        response_data = {"role": "assistant", "content": response.text if response.text else ""}
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            openai_tool_calls = []
            for cohere_tc in response.tool_calls:
                openai_tool_calls.append({
                    "id": f"call_{cohere_tc.name}_{id(cohere_tc)}", 
                    "function": {
                        "name": cohere_tc.name,
                        "arguments": json.dumps(cohere_tc.parameters)
                    },
                    "type": "function"
                })
            response_data["tool_calls"] = openai_tool_calls
            if not response_data["content"]:
                response_data["content"] = "Executing tools..."

        return response_data