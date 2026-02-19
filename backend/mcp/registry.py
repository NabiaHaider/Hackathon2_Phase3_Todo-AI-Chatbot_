from typing import Callable, Dict, Any, Optional, List

# Import all implemented skills
from skills.add_task_skill import add_task
from skills.list_tasks_skill import list_tasks
from skills.update_task_skill import update_task
from skills.complete_task_skill import complete_task
from skills.delete_task_skill import delete_task
from skills.error_handling_skill import error_handling_skill
from skills.natural_language_parsing_skill import natural_language_parsing_skill
from skills.user_greeting_skill import user_greeting_skill
from skills.conversation_management_skill import conversation_management_skill

# Ensure models are loaded so SQLModel.metadata has them
import models.chat # noqa: F401
import models# noqa: F401


class MCPToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "update_task": update_task,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "error_handling_skill": error_handling_skill,
            "natural_language_parsing_skill": natural_language_parsing_skill,
            "user_greeting_skill": user_greeting_skill,
            "conversation_management_skill": conversation_management_skill,
            # Add other skills here as they are implemented
        }

    def get_tool(self, name: str) -> Optional[Callable[..., Any]]:
        return self._tools.get(name)

    def get_all_tool_names(self) -> List[str]:
        return list(self._tools.keys())

    def get_all_tools(self) -> Dict[str, Callable[..., Any]]:
        return self._tools
