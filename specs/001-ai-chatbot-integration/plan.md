# Implementation Plan: AI Todo Chatbot Integration

**Feature Branch**: `001-ai-chatbot-integration`
**Feature Spec**: [spec.md](./spec.md)
**Created**: 2026-02-11
**Status**: Draft

## 1. Technical Context

This plan outlines the engineering steps required to integrate an AI-powered chatbot into an existing full-stack Todo application.

-   **Backend**: Python FastAPI, SQLModel ORM, Neon PostgreSQL, existing JWT Authentication.
-   **Frontend**: Next.js, Vercel deployment.
-   **AI Stack**: OpenAI Agents SDK (for orchestration), Cohere (as the LLM provider), and a custom MCP Server.
-   **Deployment**: Backend will be containerized using Docker and deployed to Hugging Face Spaces. Frontend will be deployed to Vercel.

## 2. Constitution Check

The implementation will adhere to the **Todo AI Chatbot Constitution v2.0.0**.
-   **Statelessness**: All backend services, including the chat endpoint and agent lifecycle, will be stateless.
-   **MCP Tool-Based Architecture**: The AI agent will not access the database directly. All data operations will be performed exclusively through the defined MCP tools (skills).
-   **Security**: All interactions will be protected by the existing JWT authentication system, with `user_id` propagation to enforce strict data isolation.
-   **Folder Structure**: All new code will be placed within the existing `/backend`, `/agents`, and `/skills` folders. No new root folders will be created.

## 3. Engineering Phases

### Phase 1: Backend Scaffolding & Database Migration

**Goal**: Prepare the backend to support conversation persistence and the new chat API.

1.  **Global Error Schema**:
    -   Define a global, structured Pydantic schema for all API error responses to ensure consistency (e.g., `{"detail": {"code": "ERROR_CODE", "message": "Human-readable message"}}`).

2.  **Database Migration**:
    -   In `backend/models.py`, define the `Conversation` and `Message` SQLModel tables.
    -   Generate and apply a migration script to create these tables in the database.

3.  **API Endpoint & Streaming Architecture**:
    -   In `backend/schemas.py`, define Pydantic schemas for chat requests and responses.
    -   In a new router (e.g., `backend/routes/chat.py`), implement `POST /api/v1/chat`.
    -   The endpoint MUST be designed to support streaming responses (e.g., using `StreamingResponse` from FastAPI) to send back data chunk by chunk (e.g., for streaming tool outputs or final answer generation).

4.  **Security & Authentication Integration**:
    -   Apply existing JWT authentication to the `/api/v1/chat` endpoint.
    -   Implement **Secure Headers Middleware** (e.g., for HSTS, X-Content-Type-Options) in the FastAPI application.
    -   Implement **Rate Limiting** (e.g., 30 requests/min) on the chat endpoint. Responses for blocked requests MUST include standard **rate limit response headers** (`Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`).
    -   Ensure the authenticated `user_id` is extracted and propagated.

### Phase 2: Skills Layer & MCP Server Implementation

**Goal**: Build the secure tools that the AI agent will use to interact with the application.

1.  **Skills Implementation (`/skills`)**:
    -   Implement the five core tool functions (`add_task`, `list_tasks`, etc.) in the `/skills` directory.
    -   Each skill must perform validation, call existing services, return structured JSON, and include structured logging.
    -   **Async Background Worker Readiness**: Design long-running skills to be non-blocking. For any tool that could exceed a 1-2 second execution time, implement it using FastAPI's `BackgroundTasks` to process it asynchronously without blocking the main response thread.

2.  **MCP Server Setup**:
    -   Implement the `MCPToolRegistry` within the FastAPI backend to map tool names to the skill functions.
    -   This registry will securely dispatch calls from the `AgentRunner`.

### Phase 3: Agent Architecture Implementation

**Goal**: Implement the core AI agent logic.

1.  **Agent Scaffolding (`/agents`)**:
    -   Create `todo_agent.py`, `agent_runner.py`, `agent_instructions.py`, and `tool_decision_engine.py`.

2.  **`agent_instructions.py`**:
    -   Define the agent's persona, rules, and confirmation strategies.

3.  **`todo_agent.py`**:
    -   Implement the `TodoAgent` class for primary LLM interaction.

4.  **`agent_runner.py`**:
    -   Implement the `AgentRunner` class to orchestrate the request lifecycle, including context loading, tool execution, and database persistence.

5.  **Cohere LLM Integration & Context Management**:
    -   Initialize the Cohere client using the `COHERE_API_KEY` from environment variables.
    -   Implement retry logic and timeouts for Cohere API calls.
    -   **Context Truncation Strategy**: Before sending to the LLM, the conversation history must be pruned to fit within the model's context window. The strategy will be to preserve the system prompt and the `N` most recent messages, ensuring the total token count is below the limit. `N` will be a configurable value.

### Phase 4: Frontend Chat UI Implementation

**Goal**: Build a professional, responsive, and user-friendly chat interface in the existing Next.js application.

1.  **UI Components**:
    -   Create `FloatingChatIcon`, `ChatWindowModal`, `Message`, `TypingIndicator`, and `ErrorDisplay` components.

2.  **State Management**:
    -   Use a state management solution (e.g., React Context, Zustand) for `messages`, `isLoading`, `error`.

3.  **API Integration**:
    -   Create a client-side service to handle `POST` requests to `/api/v1/chat`, attaching the JWT.
    -   Implement logic to handle and render streaming responses from the backend.

4.  **User Flow Implementation**:
    -   Implement the full user interaction flow, including sending messages, showing loading states, and rendering responses.

### Phase 5: Testing & Deployment

**Goal**: Ensure the system is robust, secure, and ready for production.

1.  **Observability Metrics Definitions**:
    -   Define key metrics to be exported for monitoring:
        -   **API**: `chat_requests_total`, `chat_request_latency_seconds`.
        -   **LLM**: `llm_call_duration_seconds`, `llm_token_usage_total`.
        -   **Tools**: `tool_calls_total{tool_name}`, `tool_call_duration_seconds{tool_name}`.

2.  **Testing Strategy**:
    -   Implement comprehensive Unit, Integration, and E2E tests.

3.  **Deployment Workflow**:
    -   **Backend (Docker & HF Spaces)**:
        1.  Create a `Dockerfile` for the FastAPI application.
        2.  **HF Spaces Port Configuration**: Ensure the Docker container exposes port `7860`, and the Hugging Face Spaces configuration maps inbound traffic to this port.
        3.  Set up a CI/CD pipeline in GitHub Actions to build and push the Docker image.
        4.  Configure all required secrets in the HF Spaces settings.
        5.  Implement `/health` and `/ready` health check endpoints.
    -   **Frontend (Vercel)**:
        1.  Connect the GitHub repository to Vercel.
        2.  Configure environment variables and deploy.

## 4. Production Readiness Checklist

-   [ ] **Configuration**: All secrets and configurations are managed via environment variables.
-   [ ] **Logging**: Structured logging is implemented across the backend.
-   [ ] **Monitoring**: Key performance and error metrics are identified for monitoring.
-   [ ] **Security**: Rate limiting, prompt injection protection, and input sanitization are implemented.
-   [ ] **Testing**: Unit, integration, and E2E tests provide adequate coverage.
-   [ ] **CI/CD**: Automated build, test, and deployment pipelines are in place.
-   [ ] **Documentation**: API endpoints and agent architecture are documented.
