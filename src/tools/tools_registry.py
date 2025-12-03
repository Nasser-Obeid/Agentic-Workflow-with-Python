"""
Updated Tool Registry with Code Executor
Replace your src/tools/tool_registry.py with this
"""

import requests
import math
import re
from typing import Callable, List, Dict, Optional
from datetime import datetime

# Import the code executor
from src.tools.code_executor import create_code_executor_tool


class ToolRegistry:
    """Registry of all available tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def register_tool(self, name: str, function: Callable, description: str):
        """Register a new tool"""
        self.tools[name] = {
            "function": function,
            "description": description,
            "name": name
        }
        print(f"🔧 Tool registered: {name}")
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool by name"""
        tool = self.tools.get(name)
        return tool["function"] if tool else None
    
    def list_tools(self) -> List[Dict]:
        """List all available tools"""
        return [
            {"name": tool["name"], "description": tool["description"]}
            for tool in self.tools.values()
        ]
    
    def _register_default_tools(self):
        """Register built-in tools"""
        
        # Original tools
        self.register_tool(
            "web_search", 
            self._web_search, 
            "Search the internet for information"
        )
        
        self.register_tool(
            "calculator", 
            self._calculator, 
            "Perform mathematical calculations"
        )
        
        self.register_tool(
            "write_file", 
            self._write_file, 
            "Write content to a file"
        )
        
        self.register_tool(
            "read_file", 
            self._read_file, 
            "Read content from a file"
        )
        
        self.register_tool(
            "get_time", 
            self._get_time, 
            "Get current date and time"
        )
        
        # NEW: Code Executor Tool
        self.register_tool(
            "execute_code",
            create_code_executor_tool(),
            "Execute Python code and compare output. Input JSON: {\"code\": \"...\", \"expected_output\": \"...\", \"compare_mode\": \"exact|fuzzy|contains\"}"
        )
    
    # ========================================================================
    # EXISTING TOOL IMPLEMENTATIONS
    # ========================================================================
    
    def _web_search(self, query: str) -> Dict:
        """Search the web using DuckDuckGo"""
        try:
            print(f"🔍 Searching web for: {query}")
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            return {
                "query": query,
                "abstract": data.get("AbstractText", ""),
                "abstract_source": data.get("AbstractSource", ""),
                "answer": data.get("Answer", ""),
                "related_topics": [
                    topic.get("Text", "")
                    for topic in data.get("RelatedTopics", [])[:5]
                    if isinstance(topic, dict) and "Text" in topic
                ],
                "success": True
            }
        except Exception as e:
            return {"query": query, "error": str(e), "success": False}
    
    def _calculator(self, expression: str) -> Dict:
        """Evaluate math expressions"""
        try:
            print(f"🔢 Calculating: {expression}")
            safe_expr = re.sub(r'[^0-9+\-*/().sqrt,pow,abs]', '', expression)
            
            allowed_names = {
                "sqrt": math.sqrt,
                "pow": math.pow,
                "abs": abs,
            }
            
            result = eval(safe_expr, {"__builtins__": {}}, allowed_names)
            return {"expression": expression, "result": result, "success": True}
        except Exception as e:
            return {"expression": expression, "error": str(e), "success": False}
    
    def _write_file(self, args: str) -> Dict:
        """Write to file - format: filename|content"""
        try:
            parts = args.split('|', 1)
            filename = parts[0].strip()
            content = parts[1] if len(parts) > 1 else ""
            
            print(f"💾 Writing to file: {filename}")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {"filename": filename, "bytes_written": len(content), "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _read_file(self, filename: str) -> Dict:
        """Read from file"""
        try:
            print(f"📖 Reading file: {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"filename": filename, "content": content, "success": True}
        except Exception as e:
            return {"filename": filename, "error": str(e), "success": False}
    
    def _get_time(self, _=None) -> Dict:
        """Get current time"""
        now = datetime.now()
        return {
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "success": True
        }