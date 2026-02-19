from typing import Dict, Any

async def user_greeting_skill(user_id: str, user_name: str = "there") -> Dict[str, Any]:
    """
    A simple skill to generate a greeting message for the user.
    """
    if not user_id:
        return {"status": "error", "message": "Validation Error: 'user_id' is required for greeting."}
    
    greeting = f"Hello {user_name}! How can I help you manage your tasks today?"
    return {
        "status": "success",
        "message": greeting,
        "user_facing_message": greeting
    }
