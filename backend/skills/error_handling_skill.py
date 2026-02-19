from typing import Dict, Any

async def error_handling_skill(user_id: str, error_message: str) -> Dict[str, Any]:
    """
    A generic skill to handle and format error messages for the user.
    This skill would be called by the agent when it encounters an issue or is confused.
    """
    if not user_id:
        return {"status": "error", "message": "Validation Error: 'user_id' is required for error handling."}
    
    # In a more advanced scenario, this might log the error internally
    # or look up specific user-friendly messages based on error_message content.
    
    return {
        "status": "success",
        "message": f"I encountered an issue: {error_message}. Please try rephrasing your request or provide more details.",
        "user_facing_message": "I'm sorry, I couldn't complete your request. Could you please try again or rephrase it?",
        "original_error": error_message
    }
