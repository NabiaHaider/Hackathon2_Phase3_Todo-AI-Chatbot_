import asyncio
import cohere
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from db import get_session
from models.chat import Conversation, Message
from datetime import datetime

class SummarizationWorker:
    """
    Background worker for long-term context summarization tasks.
    This worker will retrieve conversation history, use Cohere to summarize it,
    and persist the summary back into the database.
    """

    def __init__(self, cohere_client: cohere.Client):
        self.cohere_client = cohere_client

    async def _load_conversation_history(self, session: Session, user_id: str, conversation_id: int) -> List[Dict[str, Any]]:
        """
        Loads messages for a given conversation from the database.
        """
        messages = []
        db_messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()
        
        for msg in db_messages:
            # Format messages for Cohere API (User, Chatbot roles)
            if msg.role == "user":
                messages.append({"role": "User", "message": msg.content})
            elif msg.role == "assistant":
                messages.append({"role": "Chatbot", "message": msg.content})
            # Skip tool messages or other internal roles for summarization input directly
        return messages

    async def summarize_conversation(self, user_id: str, conversation_id: int, max_tokens: int = 500) -> Optional[str]:
        """
        Summarizes the conversation history for a given user and conversation.
        """
        with next(get_session()) as session:
            history = await self._load_conversation_history(session, user_id, conversation_id)
            
            if not history:
                return None

            # Concatenate messages for summarization. Cohere's summarize endpoint is generally for single documents.
            # For chat history, using the chat endpoint with a summarization prompt is more appropriate.
            # This is a simplified approach, a more robust solution might involve iterative summarization.
            full_conversation_text = "
".join([f"{msg['role']}: {msg['message']}" for msg in history])
            
            if not full_conversation_text.strip():
                return None

            try:
                # Use Cohere's chat endpoint with a specific prompt for summarization
                response = await self.cohere_client.chat(
                    model="command-r-plus", # Or a more suitable summarization model if available
                    message=f"Please summarize the following conversation concisely, focusing on the main topics and outcomes:

{full_conversation_text}",
                    temperature=0.3,
                    max_tokens=max_tokens,
                )
                summary = response.text
                
                if summary:
                    # Save the summary back as a system message
                    await self._save_summary_message(session, user_id, conversation_id, summary)
                    return summary
                return None

            except cohere.core.api_error.ApiError as e:
                print(f"Cohere API Error during summarization: {e.message}")
                return None
            except Exception as e:
                print(f"An unexpected error occurred during summarization: {e}")
                return None

    async def _save_summary_message(self, session: Session, user_id: str, conversation_id: int, summary_content: str):
        """
        Saves the generated summary as a system message in the conversation history.
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="system_summary", # Use a distinct role for summaries
            content=summary_content,
            created_at=datetime.utcnow()
        )
        session.add(message)
        session.commit()
        session.refresh(message)

# Example usage (would typically be called by a background task scheduler)
async def main():
    # This part would be handled by your application's startup and dependency injection
    COHERE_API_KEY = os.getenv("COHERE_API_KEY") # Ensure this is set in your env
    if not COHERE_API_KEY:
        print("COHERE_API_KEY environment variable not set.")
        return

    cohere_client = cohere.Client(api_key=COHERE_API_KEY)
    worker = SummarizationWorker(cohere_client)

    # Example: Summarize for a specific user and conversation
    test_user_id = "test_user_for_summarization" 
    test_conversation_id = 1 # Replace with an actual conversation ID
    
    # You'd need to ensure there's a conversation and messages in the DB for this user/id
    print(f"Attempting to summarize conversation {test_conversation_id} for user {test_user_id}")
    summary = await worker.summarize_conversation(test_user_id, test_conversation_id)
    
    if summary:
        print("
--- Summary Generated ---")
        print(summary)
    else:
        print("
--- No Summary Generated or Error Occurred ---")

if __name__ == "__main__":
    # This is for local testing of the worker functionality
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())
