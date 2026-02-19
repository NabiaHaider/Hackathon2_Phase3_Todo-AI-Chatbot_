# Tasks for Feature: AI Todo Chatbot Integration

**Feature Branch**: `001-ai-chatbot-integration`
**Implementation Plan**: [plan.md](./plan.md)
**Feature Spec**: [spec.md](./spec.md)

This document breaks down the implementation plan into actionable, sequential, and parallelizable tasks.

---

## Phase 1: Setup
      
- [x] T001 Create a `.env.example` file in the `backend` directory with placeholders for `Neon_db_url`, `COHERE_API_KEY`, `BETTER_AUTH_SECRET`, and `BETTER_AUTH_URL`.
- [x] T002 [P] Install `alembic` for database migrations in the backend environment.
- [x] T003 [P] Install `fastapi-limiter` for rate limiting in the backend environment.

---

## Phase 2: Foundational Backend & Core AI

**Goal**: Establish the core backend infrastructure, including database models, API endpoints, security, and agent architecture, before any UI work begins.

- [x] T004 Define `Conversation` and `Message` SQLModel schemas in `backend/models/chat.py`.
- [x] T005 [P] Define Pydantic schemas for chat API request/response and a global error schema in `backend/schemas/chat.py`.
- [x] T006 Implement a global error middleware in `backend/middleware/error_handling.py` to catch unhandled exceptions and return structured error responses.
- [x] T007 Generate a new Alembic migration to create the `conversation` and `message` tables and apply it to the database.
- [x] T008 Implement a new API router in `backend/routes/chat.py` with a `POST /api/v1/chat` endpoint that supports `StreamingResponse`.
- [x] T009 [P] Implement secure headers middleware in the main `backend/main.py` file.
- [x] T010 Implement rate limiting middleware and apply it to the chat router in `backend/main.py`. Rate limit headers MUST be included in responses.
- [x] T011 Apply the existing JWT authentication dependency to the `POST /api/v1/chat` endpoint in `backend/routes/chat.py`.
- [x] T012 [P] Implement the `add_task` skill function in `skills/add_task_skill.py`.
- [x] T013 [P] Implement the `list_tasks` skill function in `skills/list_tasks_skill.py`.
- [x] T014 [P] Implement the `update_task` skill function in `skills/update_task_skill.py`.
- [x] T015 [P] Implement the `complete_task` skill function in `skills/complete_task_skill.py`.
- [x] T016 [P] Implement the `delete_task` skill function in `skills/delete_task_skill.py`.
- [x] T017 [P] Implement a generic `error_handling_skill` in `skills/error_handling_skill.py` for the agent to call when it's confused.
- [x] T018 [P] Implement a placeholder `natural_language_parsing_skill` in `skills/natural_language_parsing_skill.py`.
- [x] T019 [P] Implement a `user_greeting_skill` in `skills/user_greeting_skill.py` for initial interactions.
- [x] T020 [P] Implement a `conversation_management_skill` in `skills/conversation_management_skill.py` (e.g., for summarizing or starting fresh).
- [x] T021 Implement the MCP Tool Registry to map all tool names to skill functions in `backend/mcp/registry.py`.
- [x] T022 [P] Create the agent instruction definitions in `agents/agent_instructions.py`.
- [x] T023 [P] Implement the `tool_decision_engine.py` with placeholder logic for intent detection.
- [x] T024 Create the `TodoAgent` class structure in `agents/todo_agent.py`.
- [x] T025 Implement the `AgentRunner` class in `agents/agent_runner.py` with logic for context loading, tool execution, and persistence.
- [x] T026 Integrate the Cohere client into `agents/agent_runner.py`, including context truncation and retry logic.
- [x] T027 Connect the `AgentRunner` to the `POST /api/v1/chat` endpoint in `backend/routes/chat.py`.

---

## Phase 3: User Story 1 - User Manages Tasks via Chat

**Goal**: Implement the frontend UI for the chatbot, allowing users to interact with the backend agent.
**Independent Test**: A user can open the chat modal, send a message to perform a CRUD action, and see a response, with the result reflected in their main task list.

- [x] T028 [P] [US1] Create a `FloatingChatIcon` React component in `frontend/components/chat/FloatingChatIcon.tsx`.
- [x] T029 [P] [US1] Create a `ChatWindowModal` React component in `frontend/components/chat/ChatWindowModal.tsx`.
- [x] T030 [P] [US1] Create a `Message` React component to render user and AI messages in `frontend/components/chat/Message.tsx`.
- [x] T031 [P] [US1] Create a `TypingIndicator` React component in `frontend/components/chat/TypingIndicator.tsx`.
- [x] T032 [P] [US1] Create an `ErrorDisplay` React component in `frontend/components/chat/ErrorDisplay.tsx`.
- [x] T033 [US1] Set up state management for the chat client using Zustand or React Context in `frontend/lib/chat-store.ts`.
- [x] T034 [US1] Implement the API service to call the `/api/v1/chat` endpoint, handling streaming responses, in `frontend/lib/api.ts`.
- [x] T035 [US1] Integrate the chat components and state management into the main application layout in `frontend/app/layout.tsx`.
- [x] T036 [US1] Implement the end-to-end user flow for sending a message and rendering the streamed response.

---

## Phase 4: User Story 2 - Chatbot Handles Unclear Instructions

**Goal**: Ensure the agent's clarification flows are correctly implemented and tested.
**Independent Test**: Sending an ambiguous command like "add task" results in the agent responding with a clarifying question, "What is the title of the task?".

- [x] T037 [P] [US2] Write an integration test to verify that sending a POST to `/api/v1/chat` with an ambiguous prompt ("add task") returns a request for more information.
- [x] T038 [US2] Refine the system prompt in `agents/agent_instructions.py` to improve clarification behavior based on test results.

---

## Phase 5: User Story 3 - Chatbot Persists Conversation History

**Goal**: Verify that conversation history is correctly saved and loaded for each user.
**Independent Test**: A user can have a conversation, refresh the page, and see their previous messages loaded in the chat window.

- [x] T039 [P] [US3] Write an integration test to verify the conversation history is correctly persisted and reloaded by the `/api/v1/chat` endpoint.
- [x] T040 [US3] Implement the specific database read/write logic for `Conversation` and `Message` models within the `AgentRunner` in `agents/agent_runner.py`.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T041 [P] Create a `Dockerfile` for the backend application, ensuring it exposes port `7860` for Hugging Face Spaces.
- [x] T042 [P] Implement `/health` and `/ready` health check endpoints in `backend/main.py`.
- [ ] T043 [P] Implement structured logging for observability metrics (API latency, LLM calls, tool usage) in `backend/main.py` and `agents/agent_runner.py`.
- [x] T044 Design and implement an `async` background worker for long-term context summarization tasks in `backend/workers/summarization.py`.
- [x] T045 [P] Set up a GitHub Actions workflow for CI to run backend and frontend tests.
- [x] T046 Write E2E tests using Playwright or Cypress to simulate full user conversations.
- [x] T047 Configure the Hugging Face Space and Vercel projects for deployment, including environment variables.
- [x] T048 Perform a final review of all security measures, including rate limiting, headers, and input sanitization.

---

## Dependencies

-   **US1 (Frontend)** depends on **Phase 2 (Foundational Backend)**. The UI cannot be fully tested without a working API.
-   **US2 (Clarification)** and **US3 (Persistence)** are backend-focused and can be developed in parallel with US1 after Phase 2 is complete.
-   **Phase 6 (Polish)** depends on all previous user stories being complete.

## Parallel Execution Examples

-   **Within Phase 2**: The five skill implementations (T011-T015) can be developed in parallel. Agent instruction definition (T017) can also be done in parallel.
-   **Across User Stories**: After Phase 2 is complete, frontend work on US1 (T022-T030) can proceed in parallel with backend integration tests for US2 (T031) and US3 (T033).

## Implementation Strategy

The suggested MVP (Minimum Viable Product) is the completion of **Phase 2** and **User Story 1**. This delivers the core value proposition: a functional chatbot interface for managing tasks. US2 and US3 enhance the experience and can be delivered in a subsequent iteration.
