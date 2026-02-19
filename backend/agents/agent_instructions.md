# `agent_instructions.md` - Agent Behavioral Instructions Specification

## 1. Purpose of the Component
The `agent_instructions.py` component serves as the central repository for the explicit, detailed behavioral guidelines that govern the Todo AI Chatbot's interactions. Its primary purpose is to define the agent's persona, communication style, and rules for confirmation and error handling, ensuring consistent and predictable user experience. These instructions are distinct from the LLM's intrinsic knowledge and are injected into the system prompt to steer its responses and actions.

## 2. Architecture Role
**Role:** Behavioral Policy Enforcer and User Experience Guide.
This component provides the "rules of engagement" for the chatbot. It dictates *how* the `TodoAgent` (via the LLM) should interact with users, ensuring alignment with the project's user experience and safety standards. While `todo_agent.py` defines *what* the agent is, `agent_instructions.py` defines *how* it should behave.

## 3. Responsibilities
-   **Define Persona:** Establishes the agent's friendly, efficient, and user-centric persona.
-   **Natural Language Behavior:** Specifies guidelines for understanding user intent, clarity of responses, contextual awareness (within stateless limits), and proactive assistance.
-   **Confirmation Strategy:** Outlines when and how to seek user confirmation for actions (especially irreversible ones) and how to provide feedback after actions.
-   **Error Handling Strategy:** Details how errors should be detected, reported (in user-friendly language), and what advice to offer. It reinforces the stateless nature of error reporting.
-   **User ID Isolation Mandate:** Emphasizes the critical rule that all operations must respect `user_id` isolation.
-   **Guidance for LLM:** The instructions contained here are integrated into the `TodoAgent`'s system prompt, acting as explicit directives for the LLM's behavior.

## 4. Decision Logic
The `agent_instructions.py` component itself does not contain runtime decision logic. Instead, it *informs* the decision logic of the `TodoAgent` (and consequently, the LLM) by providing a comprehensive set of rules and constraints. The LLM's interpretation and adherence to these instructions form the basis of the agent's operational decisions regarding:
-   When to ask for more information.
-   When to seek confirmation before executing a tool.
-   How to phrase responses, confirmations, and error messages.
-   The implicit understanding that `user_id` is a mandatory parameter for all data-modifying operations.

## 5. MCP Tool Interaction Flow
This component doesn't directly interact with MCP tools. Its role is purely instructional. The rules it provides (e.g., "always confirm before `delete_task`") guide the `TodoAgent` (LLM) on *how* to interact with the user before suggesting an MCP tool call, or *how* to interpret the results of an MCP tool call to formulate a response.

## 6. Stateless Behavior Explanation
-   The `AgentInstructions` component is inherently stateless; it's a collection of static guidelines.
-   It reinforces the overall system's stateless design by explicitly stating that the agent should not store conversational state and should rely on explicit `user_id` for all operations.
-   It mandates that error handling should not involve retaining internal state but rather immediate, user-facing communication.

## 7. Error Handling Strategy
-   **Detection:** The instructions guide the agent (LLM) to detect when an error occurs during tool execution (as reported by the `AgentRunner` back to the LLM).
-   **User-Friendly Reporting:** Explicitly mandates translating technical errors into clear, non-technical language.
-   **Suggesting Next Steps:** Encourages offering helpful advice or alternative actions to the user in case of an error.
-   **No Internal Recovery:** Reaffirms that the agent should not attempt to recover from errors using internal state, emphasizing that each interaction is a fresh start.

## 8. Production Design Explanation
-   **Centralized Policies:** Consolidates all behavioral policies into a single, easily maintainable location, making it simple to update or audit the agent's interaction rules.
-   **Separation of Concerns:** Clearly separates *what* the agent does (defined in `todo_agent.py` and `agent_runner.py`) from *how* it behaves.
-   **Consistency:** Ensures a consistent user experience by providing a unified set of guidelines for all interactions.
-   **Auditable:** The explicit nature of these instructions makes the agent's behavioral guardrails transparent and auditable for compliance or quality assurance.
-   **LLM Guidance:** Provides critical guidance to the LLM, effectively "programming" its interaction style and adherence to critical constraints (like `user_id` isolation).

## 9. Execution Flow Diagrams (Text-Based)

This component's influence is represented within the `TodoAgent`'s system prompt.

```mermaid
graph TD
    A[Developers define Agent Instructions] --> B(agent_instructions.py)
    B -- get_detailed_instructions() --> C(TodoAgent.get_system_prompt())
    C --> D[OpenAI API Call (System Message)]
    D --> E[LLM Behavior Guided by Instructions]
    E -- User Input --> F[LLM Processes Request]
    F -- Decision (e.g., Tool Call, Clarification, Confirmation, Error Message) --> G[Agent Response to User]
```

## 10. Example Conversation → Tool Mapping

The examples below illustrate how the *rules* from `agent_instructions.py` influence the LLM's response, rather than the component directly mapping to tools.

| User Input                                             | Relevant Instruction                                                                            | Agent's LLM-driven Response (influenced by instructions)                                           |
| :----------------------------------------------------- | :---------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------- |
| "Add task"                                             | "Proactive Assistance: If a request seems incomplete... ask for necessary missing information."   | "I can add a task for you! What would you like the title of the task to be?"                       |
| "Delete task 'TASK-123'."                              | "Before Action (for irreversible actions): Always confirm with the user..."                     | "Just to confirm, would you like to delete the task with ID 'TASK-123'?"                         |
| "Complete task 'TASK-789'." (After MCP tool success)   | "After Action (for all actions): Provide a friendly and clear confirmation message..."          | "✅ Task 'TASK-789' has been marked as completed. Great job!"                                      |
| (MCP tool for `list_tasks` fails)                      | "User-Friendly Messages: Translate technical error messages into understandable language."      | "I'm sorry, I encountered an issue fetching your tasks right now. Please try again in a moment."  |
| "Update task 'TASK-456' status to 'done'." (Invalid status) | "Validation Errors: If user input leads to validation errors... inform the user about the specific issue." | "The status 'done' is not valid. Please use 'pending' or 'completed' instead."                     |
| "My user ID is..."                                     | "User ID Isolation: Every MCP tool call *must* include the `user_id` parameter."                | (LLM implicitly understands to use this user_id in subsequent tool calls, without explicitly stating it back unless asked.) |
