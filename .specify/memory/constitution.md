<!--
version_change: "1.0.0 -> 2.0.0"
modified_principles:
  - "Entire constitution rewritten based on AI Chatbot integration requirements."
added_sections:
  - "System Architecture Constitution"
  - "Agent Constitution"
  - "MCP Server Constitution"
  - "Skill Layer Constitution"
  - "Stateless Execution Rules"
  - "Tool Execution Policies"
  - "Security Rules"
  - "Authentication Integration Rules"
  - "Conversation Persistence Rules"
  - "Multi-Agent Compatibility Rules"
  - "Cohere + OpenAI Agents Integration Design"
  - "Error Handling Constitution"
  - "Tool Routing Constitution"
  - "Deployment Readiness Rules"
  - "Scalability Constitution"
  - "Production Safety Rules"
  - "Logging & Observability Rules"
  - "Hackathon Phase-3 Compliance Mapping"
removed_sections:
  - "All previous sections related to Phase II Todo Full-Stack Web App."
templates_requiring_updates:
  - path: ".specify/templates/plan-template.md"
    status: "⚠ pending"
    reason: "Needs update to reflect new AI architecture, Cohere LLM, OpenAI Agents SDK, MCP Server, and database models for conversation/messages. Current template is for general feature planning."
  - path: ".specify/templates/spec-template.md"
    status: "⚠ pending"
    reason: "Needs update to incorporate AI-specific requirements, conversation flows, and tool specifications. Current template is for general feature specifications."
  - path: ".specify/templates/tasks-template.md"
    status: "⚠ pending"
    reason: "Needs update to include tasks related to agent development, skill creation, LLM integration, and conversation persistence. Current template is for general task breakdown."
  - path: ".specify/templates/commands/create-phr.sh"
    status: "⚠ pending"
    reason: "Needs review to ensure no outdated agent-specific names (e.g., 'CLAUDE') remain; ensure it aligns with generic agent concepts."
  - path: "README.md"
    status: "⚠ pending"
    reason: "Project overview, setup instructions, and architecture details need to be updated to reflect the AI Chatbot integration, new technologies (Cohere, OpenAI Agents SDK, MCP Server), and updated project structure."
todos:
  - "TODO(RATIFICATION_DATE): Determine the official ratification date for this constitution."
  - "TODO(Logging & Observability Rules): Define concrete logging levels, formats, and monitoring tools/strategies for the AI services and MCP server."
---
-->
# Todo AI Chatbot Constitution - Phase 3

## 1. System Architecture Constitution

### 1.1 Existing Stack (Backend)
The AI Chatbot will be integrated into an existing Python FastAPI backend.
-   **ORM**: SQLModel
-   **Database**: Neon Serverless PostgreSQL
-   **Authentication**: Existing JWT-based system ("Better Auth")
-   **Data Models**: Existing Task Model and APIs (`/api/tasks`)

### 1.2 AI Architecture Requirements
-   **Agent Logic**: OpenAI Agents SDK
-   **LLM Provider**: Cohere API Key for underlying language model capabilities
-   **MCP Server**: Micro-service Control Plane (MCP) Server using Official MCP SDK for tool execution
-   **Chat Endpoint**: Stateless FastAPI endpoint (`/api/{user_id}/chat`)
-   **Conversation State**: Database-driven persistence for conversation history

## 2. Agent Constitution

### 2.1 Agent Responsibilities
-   **Natural Language Understanding**: MUST accurately interpret user input.
-   **Intent Detection**: MUST identify the primary goal of the user's request (e.g., add, list, complete, delete, update task).
-   **MCP Tool Decision**: MUST decide which MCP tool(s) are required to fulfill the user's intent.
-   **Multi-Tool Execution**: MUST be capable of orchestrating and executing multiple MCP tools sequentially or in parallel for complex requests.
-   **Action Confirmation**: SHOULD provide friendly confirmations to the user before executing irreversible actions and after successful operations.
-   **Error Handling**: MUST handle errors gracefully, providing user-friendly feedback.
-   **Clarification**: MUST ask for clarification when user input is ambiguous or insufficient.

### 2.2 Agent Constraints
-   **Database Access**: Agent MUST NEVER directly access the database. All data operations MUST go through MCP tools.
-   **System State Modification**: Agent MUST NEVER directly modify system state. All system modifications MUST go through MCP tools.
-   **Local Memory**: Agent MUST NOT store local memory between requests. All conversation history MUST be persisted in the database.
-   **Server State**: Agent MUST NOT maintain server-side runtime state. All interactions MUST be stateless.
-   **MCP Tools Only**: Agent MUST ALWAYS exclusively use MCP Tools for all actions that interact with the application's data or services.
-   **Stateless Architecture**: Agent MUST ALWAYS adhere to the stateless server architecture.
-   **Structured Responses**: Agent MUST ALWAYS return structured, predictable responses.

## 3. MCP Server Constitution

### 3.1 Purpose
The MCP Server acts as the secure, controlled gateway for AI agents to interact with the backend services and data. It exposes well-defined tools (skills) that AI agents can invoke.

### 3.2 Key Characteristics
-   **Tool Exposure**: MUST expose the `add_task`, `list_tasks`, `complete_task`, `delete_task`, and `update_task` tools.
-   **API Integration**: Integrates directly with the existing FastAPI backend's business logic.
-   **Stateless Operation**: Each MCP tool invocation is independent and stateless.

## 4. Skill Layer Constitution

### 4.1 Skill Definition
Each tool (skill) exposed by the MCP Server MUST adhere to the following:
-   **Name**: A unique, descriptive name.
-   **Purpose**: A clear, concise objective for the tool.
-   **Input Schema**: A formal JSON schema defining all expected input parameters and their types.
-   **Output Schema**: A formal JSON schema defining the structure of success and error responses.
-   **Validation Rules**: Explicit rules for validating all input parameters.
-   **Error Handling**: Defined responses for various failure modes, adhering to the output schema.
-   **Security**: Implement user isolation and access control.
-   **Stateless Execution**: Guarantee of no internal state retention between calls.
-   **Example Tool Call**: Illustrative example in OpenAI Function Calling format.
-   **Example Response**: Illustrative example of successful and erroneous output.

### 4.2 Mandatory Tool Requirements
-   **`user_id` Requirement**: Every tool invocation MUST require `user_id` as an input parameter for authentication and authorization.
-   **SQLModel Interaction**: Tools MUST interact with the database exclusively via SQLModel.
-   **Statelessness**: Tools MUST be stateless; all necessary context MUST be provided in the input.
-   **Structured JSON Output**: Tools MUST return responses in structured JSON format, adhering to their output schemas.
-   **OpenAI Agents Compatible**: Tool definitions (schemas) MUST be compatible with OpenAI Agents SDK function calling.
-   **Multi-Agent Orchestration**: Tools MUST be designed to support invocation as part of multi-step agent workflows.

## 5. Stateless Execution Rules

### 5.1 Request Flow
The system MUST operate in a completely stateless server mode with the following request flow:
1.  **Request Reception**: Receive HTTP POST request at `/api/{user_id}/chat`.
2.  **History Load**: Load conversation history from the database based on `user_id` and `conversation_id` (if provided).
3.  **User Message Storage**: Store the incoming user message in the database.
4.  **Agent Context Build**: Construct the complete agent message context (system prompt, conversation history, current user message).
5.  **Agent Run**: Execute the AI agent using the Cohere LLM via OpenAI Agents SDK.
6.  **Tool Selection**: The agent identifies and selects necessary MCP tools based on user intent.
7.  **Tool Execution**: Execute the selected MCP tools.
8.  **Assistant Response Storage**: Store the agent's (assistant's) response, including tool outputs and final natural language response, in the database.
9.  **Structured Response Return**: Return a structured JSON response to the client.
10. **Runtime State**: The server MUST store NO runtime state between requests.

## 6. Tool Execution Policies

-   **Atomic Operations**: Each MCP tool MUST perform an atomic operation.
-   **Input Validation**: All tool inputs MUST be rigorously validated against their defined schemas.
-   **Database Interaction**: Tools MUST use SQLModel for all database read and write operations.
-   **Error Reporting**: Tools MUST report execution errors via their defined output schemas.
-   **Timeout Handling**: Tools SHOULD implement appropriate timeouts for external dependencies (e.g., database).

## 7. Security Rules

### 7.1 User Isolation
-   **Mandatory `user_id`**: Every data access or modification operation MUST be scoped by the `user_id`.
-   **Data Filtering**: All database queries (via SQLModel) MUST include `user_id` as a primary filter.
-   **No Cross-User Access**: It is a critical security violation for any user to access or modify another user's data. This MUST be enforced at the backend and database layers.

### 7.2 JWT-Based Access Control
-   **Authentication Context**: The agent operates based on a `user_id` derived from an authenticated context (e.g., decoded JWT token).
-   **API Protection**: All chat endpoints and MCP tool endpoints MUST be protected by JWT.
-   **Token Validation**: The backend MUST validate JWT tokens for authenticity, expiry, and integrity.
-   **Unauthorized Access**: Requests with invalid, missing, or expired JWT tokens MUST be rejected with a `401 Unauthorized` response.

## 8. Authentication Integration Rules

-   **Logged-in User Email**: The system MUST be capable of identifying the logged-in user's email from the authentication context.
-   **`user_id` Derivation**: The `user_id` (e.g., email or unique ID) MUST be consistently derived from the authentication token and passed to all MCP tools and conversation persistence mechanisms.
-   **Existing System Reuse**: The existing JWT-based authentication system MUST be fully utilized without modification.
-   **No Agent Authentication**: The AI agent itself does not perform authentication; it relies on the backend to provide the authenticated `user_id`.

## 9. Conversation Persistence Rules

### 9.1 Database Models
-   **Task Model**: Existing `Task` model will be used.
    -   `id`, `user_id`, `title`, `description`, `completed`, `created_at`, `updated_at`
-   **Conversation Model**: A new `Conversation` model MUST be created.
    -   `id`: Unique identifier for the conversation.
    -   `user_id`: Links to the user who owns the conversation.
    -   `created_at`: Timestamp of conversation creation.
    -   `updated_at`: Timestamp of last update.
-   **Message Model**: A new `Message` model MUST be created.
    -   `id`: Unique identifier for the message.
    -   `conversation_id`: Foreign key linking to the `Conversation`.
    -   `user_id`: Links to the user (redundant but good for data integrity/querying).
    -   `role`: Role of the message sender (e.g., "user", "assistant", "tool").
    -   `content`: The message content.
    -   `created_at`: Timestamp of message creation.

### 9.2 Persistence Mechanism
-   All user messages and assistant responses MUST be stored in the database for conversation history retrieval.
-   Conversation history MUST be loaded from the database for each request to maintain context for the LLM.

## 10. Multi-Agent Compatibility Rules

-   **OpenAI Agents SDK**: The system MUST leverage the OpenAI Agents SDK as the framework for agent logic, ensuring compatibility with its multi-turn, tool-using paradigm.
-   **Standardized Interfaces**: All MCP tools MUST expose standardized input/output schemas (JSON) to facilitate seamless integration and orchestration by potentially multiple agent instances or different agent implementations.
-   **Statelessness**: The stateless nature of agents and tools inherently supports compatibility, as no shared runtime state is assumed.

## 11. Cohere + OpenAI Agents Integration Design

-   **LLM Provider**: The Cohere API Key WILL be used as the underlying Large Language Model (LLM) provider.
-   **Agent Framework**: The OpenAI Agents SDK WILL be used to define agent logic, manage conversation flow, and orchestrate tool calls.
-   **Integration Point**: The OpenAI Agents SDK will be configured to use Cohere as the backend LLM, likely through a compatible `llm_provider` or `client` abstraction within the SDK.
-   **Tool Definition**: OpenAI Agents SDK's `FunctionTool` definition will be used to describe MCP tools to the Cohere-backed agent.

## 12. Error Handling Constitution

### 12.1 Agent Error Handling
-   **Graceful Failure**: Agents MUST handle errors from MCP tools gracefully, informing the user with clear, non-technical language.
-   **No Internal Recovery**: Agents MUST NOT attempt to recover from errors by maintaining internal state.
-   **Clarification**: If an error indicates ambiguous input, the agent MUST ask for clarification.

### 12.2 MCP Tool Error Handling
-   **Structured Error Responses**: All MCP tools MUST return structured JSON error responses, adhering to their output schemas, including a `status: "error"` and a descriptive `message`.
-   **Specific Error Codes/Messages**: Errors SHOULD be specific enough to aid debugging but generalized for user-facing messages.
-   **Sensitive Data**: Error messages MUST NOT expose sensitive internal details (e.g., database connection strings, stack traces).

## 13. Tool Routing Constitution

-   **LLM-Driven Routing**: The primary mechanism for tool routing is the LLM's function-calling capability, as exposed through the OpenAI Agents SDK.
-   **Schema-Based Selection**: The LLM will select the appropriate MCP tool based on the user's natural language intent and the provided input schemas of available tools.
-   **Parameter Extraction**: The LLM will be responsible for extracting all necessary parameters from the user's request to populate the tool call arguments.
-   **`AgentRunner` Orchestration**: The `AgentRunner` component acts as the dispatcher, executing the tool calls suggested by the LLM.

## 14. Deployment Readiness Rules

-   **Environment Variables**: All sensitive information (API keys, database URLs, JWT secrets) MUST be configured via environment variables.
-   **Containerization**: The backend and MCP server components SHOULD be containerized (e.g., Docker) for consistent deployment.
-   **Health Checks**: API endpoints MUST include health check routes.
-   **Scalability Design**: The stateless nature ensures horizontal scalability.
-   **Monitoring Integration**: SHOULD integrate with standard monitoring tools.

## 15. Scalability Constitution

-   **Stateless Services**: All FastAPI services, AI agents, and MCP tools MUST be stateless, enabling horizontal scaling by simply adding more instances.
-   **Database as Source of Truth**: The Neon PostgreSQL database MUST serve as the sole source of truth for all application and conversation state, avoiding distributed state issues.
-   **Asynchronous Operations**: FastAPI and SQLModel's asynchronous capabilities MUST be leveraged for non-blocking I/O, enhancing concurrency.
-   **Resource Allocation**: Resources for LLM calls (Cohere) and database connections (Neon) SHOULD be managed efficiently to prevent bottlenecks.

## 16. Production Safety Rules

-   **Input Sanitization**: All user inputs and tool parameters MUST be sanitized to prevent injection attacks (SQL, command, XSS).
-   **Rate Limiting**: API endpoints SHOULD implement rate limiting to prevent abuse and ensure stability.
-   **Circuit Breakers**: External calls (e.g., to Cohere API, database) SHOULD implement circuit breakers to prevent cascading failures.
-   **Access Control**: Role-based access control (RBAC) MUST be enforced for critical operations, in addition to user isolation.
-   **Secrets Management**: Secrets MUST be managed securely (e.g., environment variables, dedicated secret management services).

## 17. Logging & Observability Rules

TODO(Logging & Observability Rules): Define concrete logging levels, formats, and monitoring tools/strategies for the AI services and MCP server. This should cover:
-   **Structured Logging**: Log messages MUST be structured (e.g., JSON) for easy parsing and analysis.
-   **Key Metrics**: Define key metrics for AI agent performance (response time, tool call success/failure rates), MCP tool execution (latency, error rates), and system health.
-   **Tracing**: Implement distributed tracing to track requests across services (FastAPI, MCP, LLM).
-   **Alerting**: Establish alerting thresholds for critical errors and performance deviations.

## 18. Hackathon Phase-3 Compliance Mapping

This constitution serves as the foundational compliance document for Hackathon Phase-3. All development and integration efforts MUST adhere to the principles and rules outlined herein.
-   **AI Chatbot Functionality**: Full compliance with the AI-powered Todo Chatbot objective (add, list, complete, delete, update tasks).
-   **Existing Stack Integration**: Strict adherence to integrating ONLY into the existing backend, authentication, and database structure.
-   **AI Architecture**: Full implementation of OpenAI Agents SDK, Cohere LLM, and MCP Server.
-   **Statelessness**: Guaranteed stateless operation of all components.
-   **Security & User Isolation**: Unwavering enforcement of security rules, particularly user isolation and JWT protection.
-   **Database Persistence**: Correct implementation of `Conversation` and `Message` models for history.

---
**Version**: 2.0.0 | **Ratified**: 2026-01-19 | **Last Amended**: 2026-02-11