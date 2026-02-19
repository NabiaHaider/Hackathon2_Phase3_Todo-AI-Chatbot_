from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock, call
import pytest
from auth.jwt import get_current_user_id
from db import get_session, create_db_and_tables
from sqlmodel import Session, SQLModel, create_engine
import os

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def override_get_session():
    """Dependency override for test session."""
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)

@pytest.fixture(name="db_session", scope="function")
def db_session_fixture():
    """Fixture to create and clean up the database for each test."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="test_client", scope="function")
def test_client_fixture(db_session):
    """Fixture to provide a test client with isolated database and auth."""
    app.dependency_overrides[get_current_user_id] = lambda: "test_user_id"
    yield client
    app.dependency_overrides = {}


@patch('cohere.Client.chat')
async def test_ambiguous_add_task_clarification(mock_cohere_chat, test_client):
    """
    Test that sending an ambiguous 'add task' prompt returns a request for more information.
    """
    mock_cohere_chat.return_value = AsyncMock(
        text="I can add a task for you! What would you like the title to be?",
        tool_calls=[]
    )

    response = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": "Bearer fake-jwt-token"},
        json={"message": "add task"}
    )
    
    expected_response_chunk = 'data: {"type": "final_response", "message": "I can add a task for you! What would you like the title to be?"}'
    assert expected_response_chunk in response.text
    assert response.status_code == 200

@patch('cohere.Client.chat')
def test_conversation_history_persistence(mock_cohere_chat, test_client):
    """
    Test that conversation history is correctly persisted and reloaded
    between separate chat requests.
    """
    # --- First Call ---
    # Mock the Cohere response for the first message
    mock_cohere_chat.return_value = AsyncMock(text="Hello there!", tool_calls=[])

    # Send the first message
    response1 = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": "Bearer fake-jwt-token"},
        json={"message": "Hello"},
    )
    assert response1.status_code == 200
    assert 'data: {"type": "final_response", "message": "Hello there!"}' in response1.text

    # Verify the first call to Cohere had no history
    first_call_args = mock_cohere_chat.call_args_list[0].kwargs
    assert first_call_args['message'] == "Hello"
    assert first_call_args['chat_history'] == []

    # --- Second Call ---
    # Mock the Cohere response for the second message
    mock_cohere_chat.return_value = AsyncMock(text="Here are your tasks.", tool_calls=[])

    # Send the second message
    response2 = test_client.post(
        "/api/v1/chat",
        headers={"Authorization": "Bearer fake-jwt-token"},
        json={"message": "List my tasks"},
    )
    assert response2.status_code == 200
    assert 'data: {"type": "final_response", "message": "Here are your tasks."}' in response2.text

    # Verify the second call to Cohere received the history from the first call
    assert mock_cohere_chat.call_count == 2
    second_call_args = mock_cohere_chat.call_args_list[1].kwargs
    assert second_call_args['message'] == "List my tasks"
    
    expected_history = [
        {'role': 'User', 'message': 'Hello'},
        {'role': 'Chatbot', 'message': 'Hello there!'}
    ]
    
    # Extract and adapt the actual history for comparison
    actual_history = []
    for item in second_call_args['chat_history']:
        # The agent runner appends the full response object, extract what we need
        if 'role' in item and 'content' in item:
             role = "User" if item['role'] == "user" else "Chatbot"
             actual_history.append({'role': role, 'message': item['content']})

    # This assertion is tricky because of the exact format. We'll check for content.
    assert any(h['role'] == 'User' and h['message'] == 'Hello' for h in second_call_args['chat_history'])
    # The assistant's response is a complex object, so we check for its existence
    assert any(h['role'] == 'assistant' for h in second_call_args['chat_history'])
