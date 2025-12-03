"""Base agent implementation with tool usage"""
import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
from src.agent.agent_roles import AgentRole
from src.config.settings import OLLAMA_URL, MODEL_NAME

class ToolUsingAgent:
    """Agent that can use tools"""
    
    def __init__(self, name: str, role: AgentRole, 
                 tool_registry, model_name: str = MODEL_NAME):
        self.name = name
        self.role = role
        self.tool_registry = tool_registry
        self.model_name = model_name
        self.memory = []
        self.system_prompt = self._create_system_prompt()
        
        print(f"✨ Agent '{self.name}' ({self.role.value}) ready!")
    
    def _create_system_prompt(self) -> str:
        """Create system prompt based on role"""
        tools_info = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.tool_registry.list_tools()
        ])
        
        base_prompts = {
            AgentRole.RESEARCHER: "You are a research agent.",
            AgentRole.WRITER: "You are a writing agent.",
            AgentRole.ANALYST: "You are an analyst agent.",
            AgentRole.ASSISTANT: "You are a helpful assistant."
        }
        
        prompt = base_prompts.get(self.role, "You are a helpful agent.")
        prompt += f"\n\nAVAILABLE TOOLS:\n{tools_info}\n\n"
        prompt += "To use a tool, respond with:\nTOOL: tool_name\nINPUT: tool_input"
        
        return prompt
    
    def think(self, prompt: str, context: Optional[str] = None) -> str:
        """Think and potentially use tools"""
        full_prompt = f"{self.system_prompt}\n\n"
        if context:
            full_prompt += f"Context: {context}\n\n"
        full_prompt += f"Task: {prompt}"
        
        try:
            response = self._get_ai_response(full_prompt)
            tool_usage = self._parse_tool_request(response)
            
            if tool_usage:
                tool_result = self._execute_tool(
                    tool_usage["tool"],
                    tool_usage["input"]
                )
                
                final_prompt = f"""
                Tool '{tool_usage["tool"]}' results: {json.dumps(tool_result)}
                Original task: {prompt}
                Provide your final answer using these results.
                """
                
                final_response = self._get_ai_response(final_prompt)
                
                self.memory.append({
                    "agent": self.name,
                    "prompt": prompt,
                    "tool_used": tool_usage["tool"],
                    "tool_result": tool_result,
                    "response": final_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                return final_response
            else:
                self.memory.append({
                    "agent": self.name,
                    "prompt": prompt,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                return response
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from Ollama"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    
    def _parse_tool_request(self, response: str) -> Optional[Dict]:
        """Parse tool request from agent response"""
        pattern = r'TOOL:\s*(\w+)\s*\nINPUT:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        
        if match:
            return {
                "tool": match.group(1).strip(),
                "input": match.group(2).strip()
            }
        return None
    
    def _execute_tool(self, tool_name: str, tool_input: str) -> Dict:
        """Execute a tool"""
        tool_function = self.tool_registry.get_tool(tool_name)
        
        if not tool_function:
            return {"error": f"Tool '{tool_name}' not found", "success": False}
        
        try:
            result = tool_function(tool_input)
            print(f"✅ Tool '{tool_name}' executed")
            return result
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def use_tool_directly(self, tool_name: str, tool_input: str) -> Dict:
        """Directly use a tool without AI reasoning"""
        return self._execute_tool(tool_name, tool_input)
    
    def get_memory(self) -> List[Dict]:
        """Get agent memory"""
        return self.memory