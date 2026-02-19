# `todo_agent.md` - Todo AI Chatbot Main Agent Specification

## 1. Purpose of the Component
The `todo_agent.py` component serves as the core intelligent agent for the Todo AI Chatbot. Its primary purpose is to act as the interface between the user's natural language requests and the underlying MCP (Micro-service Control Plane) tools. It encapsulates the agent's persona, system prompt, and the mechanism for interacting with the OpenAI API to facilitate function calling.

## 2. Architecture Role
**Role:** Main conversational AI driver.
Within the overall stateless server architecture, `todo_agent.py` is the central orchestrator of the conversational flow. It consumes user input, applies the system's "persona" and rules, and intelligently decides (via OpenAI's function calling capabilities) which MCP tool, if any, needs to be invoked. It is the component that holds the "brain" (LLM interaction logic) of the chatbot.

## 3. Responsibilities
-   **Natural Language Understanding:** Interprets user requests expressed in natural language.
-   **Intent Detection:** Identifies the user's core objective (e.g., add a task, list tasks).
-   **Tool Selection:** Selects the most appropriate MCP tool based on the detected intent and available parameters.
-   **Prompt Management:** Constructs the system and user prompts sent to the OpenAI model, integrating agent instructions and tool schemas.
-   **Model Interaction:** Manages the API calls to the OpenAI `chat.completions.create` endpoint.
-   **Stateless Operation:** Ensures that each interaction with the OpenAI model is self-contained, not relying on persistent internal state across requests.
-   **Response Generation:** Processes the LLM's response, including extracting tool calls or direct text responses.

## 4. Decision Logic
The primary decision logic is delegated to the underlying Large Language Model (LLM) provided by OpenAI, specifically through its **Function Calling** capability.
-   The `get_system_prompt` method defines the overarching rules, persona, and constraints that guide the LLM's decisions.
-   The `get_tools` method exposes the available MCP tools and their schemas to the LLM.
-   The LLM, based on the user's message, the system prompt, and the tool schemas, decides:
    -   Whether to respond directly in natural language.
    -   Whether to call one or more tools.
    -   Which tool(s) to call.
    -   What arguments to pass to the selected tool(s).

## 5. MCP Tool Interaction Flow
1.  **Tool Definition Exposure:** The agent gathers all available MCP `FunctionTool` objects (from `agent_runner`) and presents their schemas to the OpenAI model via the `tools` parameter in the `chat.completions.create` API call.
2.  **LLM Decision:** The LLM, guided by its training and the provided system prompt, analyzes the user's input and the tool schemas to determine if a tool call is necessary.
3.  **Tool Call Generation:** If the LLM decides to call a tool, it generates a `tool_calls` object in its response, specifying the `function_name` and `arguments` (as a JSON string).
4.  **No Direct Execution:** The `todo_agent` itself does not execute the MCP tools. It merely requests the LLM to identify the need for a tool call and its parameters. The actual execution is handled by the `agent_runner`.

## 6. Stateless Behavior Explanation
-   The `TodoAgent` maintains statelessness by not storing any conversational history or user-specific data internally across different invocations.
-   For each `run_conversation` call, a new, complete set of messages (including the system prompt and the current user query) is constructed and passed to the OpenAI API.
-   Any "state" required for a conversation turn (e.g., previous messages to provide context for the LLM) is managed externally by the `AgentRunner` and passed into the `run_conversation` method for that specific interaction. This ensures that the `TodoAgent` itself remains a pure function, processing input to produce output without side effects or reliance on past internal memory.

## 7. Error Handling Strategy
-   **LLM Guidance:** The system prompt instructs the agent to handle errors gracefully and inform the user. The expectation is that if a tool call returns an error, the LLM will interpret this error (which is fed back to it as a "tool" message) and generate a user-friendly explanation.
-   **No Internal Recovery:** The `TodoAgent` does not implement complex error recovery logic. Its role is to pass information to and from the LLM. Error *execution* and *reporting* (e.g., catching exceptions during actual tool invocation) are handled by the `AgentRunner`.
-   **Clarification:** If the LLM determines (or is instructed) that the user input is ambiguous or insufficient for a tool call, it should ask for clarification, preventing erroneous tool execution.

## 8. Production Design Explanation
-   **Modularity:** Separates the core AI logic (LLM interaction) from tool execution (`agent_runner`) and explicit instructions (`agent_instructions`).
-   **Scalability:** The stateless nature allows for easy horizontal scaling, as no session-specific data needs to be maintained on the agent instance. Each request can be processed independently by any available agent instance.
-   **Observability:** Clear input/output boundaries for each `run_conversation` call facilitate logging and monitoring of LLM interactions and tool call decisions.
-   **Flexibility:** The `model` parameter in `__init__` allows for easy switching between different OpenAI models (e.g., `gpt-4o-mini`, `gpt-4o`) or even other LLM providers by modifying the `client` and `model` attributes.
-   **Security:** By strictly enforcing tool-based interaction and `user_id` isolation (as instructed in the system prompt), the agent prevents direct database access and ensures data privacy.

## 9. Execution Flow Diagrams (Text-Based)

```mermaid
graph TD
    A[User Input] --> B(AgentRunner.run_chat_completion)
    B --> C{Construct LLM Messages & Tools}
    C --> D(TodoAgent.run_conversation)
    D --> E[OpenAI API Call]
    E --> F{LLM Response}
    F -- Tool Call --> G(AgentRunner: Execute MCP Tool)
    G --> H{MCP Tool Output}
    H --> I{Append Tool Output to Messages}
    I --> J(TodoAgent.run_conversation - 2nd Call)
    J --> K[OpenAI API Call (with Tool Output)]
    K --> L{LLM Final Response}
    L --> M[AgentRunner: Return Final Response]
    F -- Direct Text Response --> M
```

## 10. Example Conversation → Tool Mapping

| User Conversation                                       | Detected Intent (LLM) | Tool Call (LLM Suggestion)                      | Tool Arguments (LLM Suggestion)                                                                 | Agent Confirmation / Response Example                 |
| :------------------------------------------------------ | :-------------------- | :---------------------------------------------- | :---------------------------------------------------------------------------------------------- | :---------------------------------------------------- |
| "Add 'Buy milk' to my todo list."                       | Add Task              | `add_task`                                      | `user_id="<user_id>", title="Buy milk"`                                                         | "✅ Your task 'Buy milk' has been added."             |
| "List all my pending tasks."                            | List Tasks            | `list_tasks`                                    | `user_id="<user_id>", status="pending"`                                                         | "Here are your pending tasks:..." (summary)           |
| "Complete task 'TASK-123'."                             | Complete Task         | `complete_task`                                 | `user_id="<user_id>", task_id="TASK-123"`                                                       | "✅ Task 'TASK-123' has been marked as completed."    |
| "Delete the 'Walk dog' task with ID 'TASK-456'."        | Delete Task           | `delete_task`                                   | `user_id="<user_id>", task_id="TASK-456"`                                                       | "🗑️ Task 'TASK-456' has been deleted."                 |
| "Change task 'TASK-789' title to 'Buy groceries'."      | Update Task           | `update_task`                                   | `user_id="<user_id>", task_id="TASK-789", title="Buy groceries"`                                | "🔄 Task 'TASK-789' has been updated."               |
| "Can you tell me a joke?"                               | None (General Query)  | (None - Direct LLM Text Response)               | (N/A)                                                                                           | "Why don't scientists trust atoms? Because they make up everything!" |
| "Add task without details."                             | Add Task              | (None - Clarification Needed)                   | (N/A)                                                                                           | "I can add a task, but what would you like the title to be?" |
| "Complete task 'UNKNOWN-ID'." (assuming ID doesn't exist) | Complete Task         | `complete_task` (returns error from MCP)        | `user_id="<user_id>", task_id="UNKNOWN-ID"`                                                     | "❌ I couldn't find a task with ID 'UNKNOWN-ID'. Please check the ID and try again." |
