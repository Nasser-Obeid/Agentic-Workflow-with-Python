"""Agent role definitions"""
from enum import Enum

class AgentRole(Enum):
    """Agent roles/specialties"""
    RESEARCHER = "researcher"
    WRITER = "writer"
    ANALYST = "analyst"
    ASSISTANT = "assistant"