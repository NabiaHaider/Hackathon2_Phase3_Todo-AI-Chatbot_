---
id: 0005
title: Create Implementation Plan for AI Chatbot
stage: plan
date: 2026-02-11
surface: agent
model: gemini-1.5-flash
feature: ai-chatbot-integration
branch: 001-ai-chatbot-integration
user: TODO(USER)
command: /sp.plan
labels: ["plan", "architecture", "backend", "frontend", "deployment"]
links:
  spec: specs/001-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-ai-chatbot-integration/plan.md
tests:

---

## Prompt

You are a Senior Production AI Architect, FastAPI Backend Engineer, MCP System Designer, OpenAI Agents SDK Specialist, Cohere LLM Integration Engineer, and Senior Full Stack UI/UX Planner.

Your task is to generate a COMPLETE IMPLEMENTATION PLAN (sp.plan) for Hackathon Phase-3:
"AI Todo Chatbot Integration into an EXISTING Full Stack Todo Application".

IMPORTANT:
This is NOT a new project.
You MUST integrate the AI Chatbot into an already existing Full Stack Todo App built with:
- FastAPI Backend
- Neon PostgreSQL Database
- JWT Authentication
- Next.js Frontend
- Existing Todo CRUD APIs
- Existing Task Entity

========================================
CORE AI ARCHITECTURE REQUIREMENTS
========================================

The plan MUST follow:

1. Stateless Server Architecture
2. MCP Tool-Based System (NO direct DB access by agent)
3. OpenAI Agents SDK for orchestration
4. Cohere as LLM Provider
5. Skills Layer for task operations
6. Secure JWT authenticated chat endpoint
7. Conversation history persistence
8. Tool registry + AgentRunner architecture
9. Multi-step tool execution
10. Production-grade logging and observability
11. Conversation + Message database schema migration planning
12. API versioning strategy (/api/v1/chat)
13. Streaming-ready response architecture
14. Background task readiness for async processing

========================================
COHERE + AGENT INTEGRATION
========================================

- Cohere API key will be loaded from backend environment variables.
- Agent must run using OpenAI Agents SDK logic but with Cohere LLM provider.
- No hardcoded keys.
- Include retry strategy for LLM failures.
- Include timeout handling.
- Include fallback handling for LLM downtime.
- Include token truncation + context size management.

========================================
REQUIRED MCP TOOLS (SKILLS)
========================================

Plan MUST include implementation steps for:

- add_task
- list_tasks
- update_task
- complete_task
- delete_task

Each tool MUST:
- be stateless
- require authenticated user_id
- use FastAPI existing services
- return structured JSON
- include error schema
- include input validation layer
- include structured logging

========================================
AGENT FOLDER STRUCTURE PLAN
========================================

/agents
- todo_agent.py
- agent_runner.py
- agent_instructions.py
- tool_decision_engine.py

Include:
- agent lifecycle per request
- context rebuild from DB
- clarification flow
- structured response format
- streaming-ready architecture

========================================
SKILLS LAYER STRUCTURE
========================================

/skills
- add_task_skill.py
- list_tasks_skill.py
- update_task_skill.py
- complete_task_skill.py
- delete_task_skill.py
- error_handling_skill.py
- natural_language_parsing_skill.py
- user_greeting_skill.py
- conversation_management_skill.py

Include:
- JSON schema definitions
- validation layer
- secure tool router
- MCP tool registry plan
- audit logging hooks

========================================
FRONTEND CHATBOT UI PLAN (VERY IMPORTANT)
========================================

Design a PROFESSIONAL and BEAUTIFUL chatbot UI:

1. Floating Chat Icon on all authenticated pages
2. Modal Chat Window
3. Professional modern design
4. Clean spacing and responsive layout
5. Loading animation
6. Smooth message transitions
7. Error boundary UI layer
8. Reconnect + retry UI flow

CHAT COLOR BEHAVIOR:

- User typing box:
  Primary container
  White typing text

- User messages:
  White box
  Dark text

- AI responses:
  Primary color message box
  White text inside

- Typing indicator:
  Animated dots
  Primary theme color

Include:
- state management
- message rendering flow
- API integration steps
- error UI handling
- reconnect handling
- streaming response rendering readiness

========================================
SECURITY PLAN
========================================

Include planning for:

- JWT middleware
- user_id propagation
- rate limiting (30 req/min example)
- rate limit response headers
- prompt injection protection
- input sanitization
- RBAC awareness
- secrets via environment variables
- CORS configuration
- secure headers middleware
- audit logging

========================================
DEPLOYMENT PLAN
========================================

Frontend:
- Next.js on Vercel

Backend:
- FastAPI + Agents + MCP in Docker
- Deploy to HuggingFace Spaces

Database:
- Neon PostgreSQL

Include:
- environment configuration
- .env loading strategy
- HF Spaces port configuration (7860)
- production logging
- monitoring metrics
- health check endpoints (/health, /ready)
- docker build strategy
- CI/CD validation build steps

========================================
PERFORMANCE PLAN
========================================

Include:

- response < 3s target
- concurrent users >= 50
- context trimming
- token usage control
- caching strategy if needed
- async execution strategy

========================================
OUTPUT FORMAT
========================================

Generate a COMPLETE IMPLEMENTATION PLAN with:

1. Step-by-step engineering phases
2. Backend implementation steps
3. Agents architecture plan
4. Skills development plan
5. Frontend UI build plan
6. Integration checkpoints
7. Testing strategy
8. Deployment workflow
9. Production readiness checklist

Do NOT give explanations.
Produce a structured professional sp.plan document only.
Do NOT omit any production components.

## Response snapshot

A complete implementation plan was generated and saved to `specs/001-ai-chatbot-integration/plan.md`. The plan outlines a phased approach covering backend scaffolding, database migration, skills and MCP server implementation, agent architecture, frontend UI development, and finally, testing and deployment. It adheres to all specified architectural constraints, including statelessness, security, and the defined technology stack.

## Outcome

- ✅ Impact: A comprehensive, step-by-step engineering plan is now available, providing a clear roadmap for developing and deploying the AI Chatbot feature. This enables the team to proceed to the task breakdown phase (`/sp.tasks`).
- 🧪 Tests: No tests were run as this was a planning phase.
- 📁 Files: `specs/001-ai-chatbot-integration/plan.md` was created/updated.
- 🔁 Next prompts: The user is expected to proceed with `/sp.tasks` to break down the created plan into actionable development tasks.
- 🧠 Reflection: The prompt was extremely detailed, allowing for the generation of a highly specific and structured implementation plan. The process successfully translated high-level architectural requirements from the constitution and specification into a concrete, phased engineering plan. The continued failure of the shell script remains a minor obstacle, but the manual fallback is effective.

## Evaluation notes (flywheel)

- Failure modes observed: `create-phr.sh` script failed.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
