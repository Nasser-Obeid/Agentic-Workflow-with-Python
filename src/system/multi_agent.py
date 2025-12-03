"""Multi-agent system implementation"""
from src.agent.base_agent import ToolUsingAgent
from src.agent.agent_roles import AgentRole
from src.tools.tools_registry import ToolRegistry
from typing import Dict

class ToolEnabledMultiAgentSystem:
    """Multi-agent system where agents can use tools"""
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        
        self.agents = {
            "researcher": ToolUsingAgent("Research Agent", AgentRole.RESEARCHER, self.tool_registry),
            "writer": ToolUsingAgent("Writing Agent", AgentRole.WRITER, self.tool_registry),
            "analyst": ToolUsingAgent("Analysis Agent", AgentRole.ANALYST, self.tool_registry),
            "assistant": ToolUsingAgent("Assistant Agent", AgentRole.ASSISTANT, self.tool_registry)
        }
        
        print(f"\n{'='*60}")
        print(f"🤖 Multi-Agent System Initialized")
        print(f"Agents: {len(self.agents)} | Tools: {len(self.tool_registry.list_tools())}")
        print(f"{'='*60}\n")
    
    def research_and_write(self, topic: str) -> Dict:
        """Research a topic then write about it"""
        print(f"\n{'='*60}")
        print(f"📚 Research & Write: {topic}")
        print(f"{'='*60}\n")
        
        result = {"topic": topic, "steps": [], "final_output": ""}
        
        try:
            print("🔍 Step 1: Researching...")
            research = self.agents["researcher"].think(
                f"Research key information about: {topic}"
            )
            result["steps"].append({"agent": "researcher", "output": research})
            print("✅ Research complete\n")
            
            print("✍️ Step 2: Writing...")
            article = self.agents["writer"].think(
                f"Write an article about: {topic}",
                context=f"Research: {research}"
            )
            result["steps"].append({"agent": "writer", "output": article})
            result["final_output"] = article
            print("✅ Writing complete\n")
            
        except Exception as e:
            result["error"] = str(e)
        
        return result