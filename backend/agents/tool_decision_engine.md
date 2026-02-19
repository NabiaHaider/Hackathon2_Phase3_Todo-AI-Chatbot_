# `tool_decision_engine.md` - Tool Decision Engine Specification

## 1. Purpose of the Component
The `tool_decision_engine.py` component is designed to assist (or, in a fallback scenario, replace) the Large Language Model (LLM) in identifying user intent and extracting parameters for tool calls. While the primary mechanism for tool selection is the LLM's function calling capability, this component provides a structured, rule-based approach for intent detection, parameter extraction, and defines strategies for tool selection and multi-step reasoning. It acts as a safety net or an explicit guide for LLM behavior.

## 2. Architecture Role
**Role:** Intent Recognizer and Tool Suggestion Helper (primarily for LLM guidance/fallback).
In an architecture heavily reliant on OpenAI's function calling, this component primarily serves as a conceptual framework or a fallback mechanism. It codifies the explicit rules for how intent *could* be detected and how tools *should* be selected and orchestrated. It defines the explicit policies that the LLM is expected to follow, even if the LLM's internal mechanisms handle the actual detection. For LLMs with less robust function calling, or for debugging purposes, it could be used for pre-processing.

## 3. Responsibilities
-   **Intent Detection Logic:** Defines patterns and keywords to identify the user's high-level goal (e.g., "add task," "list tasks").
-   **Parameter Extraction:** Extracts specific data points (e.g., task title, task ID, due date) from natural language input that are necessary for tool execution.
-   **Tool Selection Strategy:** Outlines explicit rules for choosing which MCP tool to use based on detected intent and available parameters.
-   **Multi-step Reasoning Rules:** Provides guidelines for handling complex requests that might involve a sequence or parallel execution of multiple MCP tools.
-   **LLM Guidance Definition:** Articulates the strategies that the LLM is expected to employ when making decisions about tool calls.

## 4. Decision Logic
The decision logic in `tool_decision_engine.py` is rule-based and regex-driven for `detect_intent_and_extract_params`.
-   **Keyword Matching:** It scans user input for predefined keywords and phrases associated with specific tool intents (e.g., "add task", "delete task").
-   **Regex Extraction:** Uses regular expressions to parse out relevant parameters (like task titles, IDs, or due dates) from the user's message.
-   **Tool Mapping:** If an intent and sufficient parameters are detected, it suggests a `tool_name` and a dictionary of `params`.
-   **Clarification Fallback:** If insufficient information is present for a required parameter, the logic implicitly (or explicitly, if used for pre-processing) points towards needing clarification from the user.

## 5. MCP Tool Interaction Flow
This component does not directly interact with MCP tools. Instead, it:
-   **Describes Tool Characteristics:** It is initialized with `available_tools` (a dictionary of tool names to their basic descriptions/schemas), which it uses to understand the landscape of tools it *could* suggest.
-   **Proposes Tool Calls:** Its `detect_intent_and_extract_params` method outputs a suggested `tool_name` and `params` that *could* be passed to an MCP tool. This output is then either directly used by an `AgentRunner` (in a simpler agent) or serves as an explicit example of how the LLM should generate its tool calls.

## 6. Stateless Behavior Explanation
-   The `ToolDecisionEngine` itself is stateless. Its methods operate on the input received (`user_input`, `user_id`) and return a result without storing any internal state across calls.
-   The rules and strategies defined within it are static policies, not dynamic state.
-   Any `user_id` passed to `detect_intent_and_extract_params` is used solely for the current processing and is not retained.

## 7. Error Handling Strategy
-   **Parameter Missing/Invalid:** If `detect_intent_and_extract_params` cannot extract necessary parameters for a tool, it returns `None`, indicating that a clear intent leading to a tool call could not be formed. This signals to the calling component (e.g., `AgentRunner`) that the LLM needs to ask for clarification.
-   **No Direct Execution Errors:** Since this component doesn't execute tools, it doesn't handle execution errors. Its "errors" are primarily failures to parse or match user intent, leading to a request for more information.

## 8. Production Design Explanation
-   **Explicit Policy Definition:** Provides a clear, human-readable specification of how tool decisions are intended to be made, which is crucial for development, debugging, and auditing in a production environment.
-   **LLM Augmentation/Fallback:** Can serve as an augmentation to the LLM's function calling for complex edge cases, or as a robust fallback if LLM function calling is unavailable or insufficient.
-   **Testability:** The rule-based nature of `detect_intent_and_extract_params` makes it highly testable, allowing for explicit unit tests of intent detection and parameter extraction.
-   **Maintainability:** Centralizes the logic for how user intents map to tool actions, making it easier to update or add new tool-related parsing rules.
-   **Transparency:** Increases transparency in the agent's decision-making process by explicitly outlining the rules and strategies.

## 9. Execution Flow Diagrams (Text-Based)

```mermaid
graph TD
    A[User Input] --> B(ToolDecisionEngine.detect_intent_and_extract_params)
    B --> C{Regex Pattern Matching<br>on Keywords & Phrases}
    C -- Match Found --> D{Extract Parameters}
    D --> E{Construct Suggested Tool Call<br>(tool_name, params)}
    E --> F[Output to AgentRunner/LLM for Execution]
    C -- No Match / Insufficient Params --> G[Output None<br>(Signifies need for LLM Clarification)]
```

## 10. Example Conversation → Tool Mapping

This section demonstrates how this engine *would* map an example conversation to a tool call suggestion.

| User Conversation                                           | Intent Detection Logic (`detect_intent_and_extract_params`)                                                                        | Suggested Tool Call Output (`tool_name`, `params`)                                                                                             | LLM's Subsequent Action (if using this as guidance)                                     |
| :---------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------- |
| "Please add a task to buy groceries."                       | Keywords: "add task". Regex for title: "buy groceries".                                                                            | `{"tool_name": "add_task", "params": {"user_id": "<user_id>", "title": "buy groceries"}}`                                                     | Calls `add_task` MCP tool.                                                              |
| "Can you list my completed tasks?"                          | Keywords: "list tasks", "completed".                                                                                               | `{"tool_name": "list_tasks", "params": {"user_id": "<user_id>", "status": "completed"}}`                                                       | Calls `list_tasks` MCP tool with status filter.                                         |
| "Complete task 'TASK-789'."                                 | Keywords: "complete task". Regex for ID: "TASK-789".                                                                               | `{"tool_name": "complete_task", "params": {"user_id": "<user_id>", "task_id": "TASK-789"}}`                                                   | Calls `complete_task` MCP tool.                                                         |
| "Delete task 'ABC-123'."                                    | Keywords: "delete task". Regex for ID: "ABC-123".                                                                                  | `{"tool_name": "delete_task", "params": {"user_id": "<user_id>", "task_id": "ABC-123"}}`                                                       | Calls `delete_task` MCP tool.                                                           |
| "Update task 'DEF-456' title to 'Read a book'."             | Keywords: "update task". Regex for ID: "DEF-456". (Simplified for this component, actual LLM would extract title change)         | `{"tool_name": "update_task", "params": {"user_id": "<user_id>", "task_id": "DEF-456"}}` (Title parameter would be null/missing here)         | LLM would ask for more details or call `update_task` without title (if allowed).        |
| "Just add a task."                                          | Keywords: "add task". No title found.                                                                                              | `{"tool_name": "add_task", "params": {"user_id": "<user_id>"}}` (title missing)                                                                | LLM would realize missing required 'title' and ask user for it.                         |
| "Tell me a joke."                                           | No matching keywords for any defined tool intents.                                                                                 | `None`                                                                                                                                         | LLM generates a direct, conversational response (e.g., a joke).                         |
