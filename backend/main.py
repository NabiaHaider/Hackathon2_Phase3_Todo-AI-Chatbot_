from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

import os
from db import create_db_and_tables, get_session
from routes import tasks, auth
from schemas.chat import GlobalError, ErrorDetail
from sqlmodel import Session, select

from middleware.rate_limiter import InMemoryRateLimiterMiddleware

# Define SecureHeadersMiddleware
class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://cdn.jsdelivr.net; font-src 'self';"
        return response

app = FastAPI()

# Configure CORS - Ensure this is applied immediately after app initialization
origins = [
    "http://localhost:3000",
    "https://hackathon2-phase2-todo-application-liart.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add InMemoryRateLimiterMiddleware before SecureHeadersMiddleware
app.add_middleware(InMemoryRateLimiterMiddleware)

# Add SecureHeadersMiddleware after CORS
# app.add_middleware(SecureHeadersMiddleware)

# Global Exception Handler
@app.exception_handler(Exception)
async def custom_general_exception_handler(request: Request, exc: Exception):
    error_detail = ErrorDetail(code="UNHANDLED_EXCEPTION", message=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=GlobalError(detail=error_detail).dict(),
    )


@app.get("/")
def root():
    return {"message": "Todo API running successfully 🚀"}

@app.on_event("startup")
def on_startup(): # Changed to def
    create_db_and_tables()

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/ready")
def readiness_check(session: Session = Depends(get_session)):
    try:
        # A simple query to check DB connection
        session.exec(select(1)).first()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database connection failed: {e}")

app.include_router(tasks.router, prefix="/api/tasks") # Uncomment once tasks router is implemented
app.include_router(auth.router, prefix="/api/auth")

# Import Cohere client, MCP Tool Registry, and AgentRunner
import cohere
from mcp.registry import MCPToolRegistry
from agents.agent_runner import AgentRunner

# Initialize Cohere Client (once globally)
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable not set.")
cohere_client = cohere.Client(api_key=COHERE_API_KEY)

# Initialize MCP Tool Registry (once globally)
mcp_tool_registry = MCPToolRegistry()

# Initialize AgentRunner (once globally)
agent_runner = AgentRunner(cohere_client, mcp_tool_registry)

# Include chat router after global agent_runner is initialized
from routes import chat
app.include_router(chat.router, prefix="/api") # Prefix /api to match /api/v1/chat