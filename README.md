# 🤖 Agentic Workflow System

A multi-agent AI system built with Ollama and Flask that enables specialized AI agents to collaborate on complex tasks using various tools including web search, code execution, file operations, and more.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Available Tools](#available-tools)
- [Creating Custom Agents](#creating-custom-agents)
- [Adding New Tools](#adding-new-tools)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### 🎯 Multi-Agent System
- **Specialized Agents**: Researcher, Writer, Analyst, and Assistant agents with distinct capabilities
- **Agent Collaboration**: Agents can work together, passing context and results between each other
- **Memory Management**: Each agent maintains conversation history for context-aware responses

### 🛠️ Powerful Tools
- **Web Search**: Search the internet using DuckDuckGo API
- **Code Execution**: Safely execute Python code with output validation and comparison
- **Calculator**: Perform mathematical calculations
- **File Operations**: Read and write files
- **Time/Date**: Get current date and time information

### 🔒 Safety Features
- **Sandboxed Code Execution**: Restricted environment prevents dangerous operations
- **Resource Limits**: Timeout and memory limits for code execution
- **Input Validation**: All inputs are validated before processing
- **Error Handling**: Comprehensive error handling and reporting

### 🌐 RESTful API
- Clean, well-documented API endpoints
- JSON request/response format
- Easy integration with frontend applications

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask API Layer                          │
│  (Handles HTTP requests and routes to appropriate agents)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-Agent System Coordinator                  │
│   (Manages agent collaboration and workflow orchestration)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────┴─────────────────────┐
        │                     │                      │
        ▼                     ▼                      ▼
┌──────────────┐     ┌──────────────┐      ┌──────────────┐
│   Researcher │     │    Writer    │      │   Analyst    │
│    Agent     │────▶│    Agent     │◀────▶│    Agent     │
└──────────────┘     └──────────────┘      └──────────────┘
        │                     │                      │
        └─────────────────────┴──────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Tool Registry  │
                    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                      ▼
┌──────────────┐     ┌──────────────┐      ┌──────────────┐
│  Web Search  │     │Code Executor │      │  Calculator  │
└──────────────┘     └──────────────┘      └──────────────┘
```

**How It Works:**
1. User sends a request to the Flask API
2. The request is routed to the appropriate agent or workflow
3. Agents use the AI model (Ollama) to process the request
4. Agents can call tools when needed (web search, code execution, etc.)
5. Results are passed between agents in collaborative workflows
6. Final response is returned to the user

---

## 📥 Installation

### Prerequisites

- **Python 3.8+**
- **Ollama** (for running local LLM models)
- **Git** (for cloning the repository)

### Step 1: Install Ollama

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com/)

### Step 2: Pull an AI Model

```bash
# Pull the Llama 3.2 model (recommended)
ollama pull llama3.2

# Or pull Llama 3.1 if you prefer
ollama pull llama3.1

# Start Ollama server
ollama serve
```

### Step 3: Clone the Repository

```bash
git clone https://github.com/yourusername/agentic_workflow.git
cd agentic_workflow
```

### Step 4: Install Python Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python main.py
```

The server will start at `http://localhost:5000`

---

## 🚀 Quick Start

### Test the Server

```bash
# Check if server is running
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "agents": ["researcher", "writer", "analyst", "assistant"],
  "tools": [...],
  "timestamp": "2024-12-29T10:00:00"
}
```

### Simple Chat with an Agent

```bash
curl -X POST http://localhost:5000/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "assistant",
    "task": "Explain what Python is in simple terms"
  }'
```

### Use a Tool Directly

```bash
# Web search
curl -X POST http://localhost:5000/tool/use \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "web_search",
    "input": "latest AI news"
  }'

# Calculator
curl -X POST http://localhost:5000/tool/use \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "calculator",
    "input": "sqrt(144) + 25"
  }'

# Execute code
curl -X POST http://localhost:5000/tool/use \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "execute_code",
    "input": "print(\"Hello, World!\")"
  }'
```

### Multi-Agent Collaboration

```bash
# Research and write workflow
curl -X POST http://localhost:5000/workflow/research-and-write \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The history of artificial intelligence"
  }'
```

---

## 💡 Usage Examples

### Example 1: Code Testing Agent

Ask an agent to write and validate code:

```bash
curl -X POST http://localhost:5000/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "assistant",
    "task": "Write a Python function to calculate the factorial of 5 and verify the result is 120"
  }'
```

The agent will:
1. Write the factorial function
2. Execute it using the code executor tool
3. Compare output with expected result (120)
4. Report success or failure

### Example 2: Research and Content Creation

```bash
curl -X POST http://localhost:5000/workflow/research-and-write \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Benefits of renewable energy"
  }'
```

Workflow:
1. **Researcher Agent**: Searches the web for information
2. **Writer Agent**: Creates article based on research
3. Returns comprehensive article with sources

### Example 3: Code Output Validation

```bash
curl -X POST http://localhost:5000/tool/use \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "execute_code",
    "input": "{\"code\": \"print(2 + 2)\", \"expected_output\": \"4\\n\", \"compare_mode\": \"exact\"}"
  }'
```

Response:
```json
{
  "execution_success": true,
  "output": "4\n",
  "comparison": {
    "mode": "exact",
    "match": true,
    "similarity": 1.0,
    "details": "✅ Output matches exactly!"
  }
}
```

### Example 4: Data Analysis

```bash
curl -X POST http://localhost:5000/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "analyst",
    "task": "Calculate the average of these numbers: 10, 20, 30, 40, 50"
  }'
```

---

## 📚 API Reference

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "agents": ["researcher", "writer", "analyst", "assistant"],
  "tools": [...],
  "timestamp": "2024-12-29T10:00:00"
}
```

---

### List Available Tools

**Endpoint:** `GET /tools`

**Response:**
```json
{
  "tools": [
    {
      "name": "web_search",
      "description": "Search the internet for information"
    },
    {
      "name": "execute_code",
      "description": "Execute Python code and compare output"
    }
  ]
}
```

---

### Send Task to Agent

**Endpoint:** `POST /agent/task`

**Request Body:**
```json
{
  "agent": "researcher",
  "task": "Find information about quantum computing",
  "context": "Optional context from previous interactions"
}
```

**Response:**
```json
{
  "agent": "researcher",
  "task": "Find information about quantum computing",
  "result": "Quantum computing is...",
  "timestamp": "2024-12-29T10:00:00"
}
```

---

### Use Tool Directly

**Endpoint:** `POST /tool/use`

**Request Body:**
```json
{
  "tool": "web_search",
  "input": "latest AI developments"
}
```

**Response:**
```json
{
  "query": "latest AI developments",
  "abstract": "...",
  "related_topics": [...],
  "success": true
}
```

---

### Research and Write Workflow

**Endpoint:** `POST /workflow/research-and-write`

**Request Body:**
```json
{
  "topic": "Climate change impacts"
}
```

**Response:**
```json
{
  "topic": "Climate change impacts",
  "steps": [
    {
      "agent": "researcher",
      "output": "Research findings..."
    },
    {
      "agent": "writer",
      "output": "Final article..."
    }
  ],
  "final_output": "Complete article text..."
}
```

---

### Get Agent Memory

**Endpoint:** `GET /memory/<agent_name>`

**Response:**
```json
{
  "agent": "researcher",
  "memory": [
    {
      "prompt": "Search for AI news",
      "response": "...",
      "timestamp": "2024-12-29T10:00:00"
    }
  ],
  "total_interactions": 5
}
```

---

## 🛠️ Available Tools

### 1. Web Search (`web_search`)

Search the internet using DuckDuckGo API.

**Input:** Search query string  
**Output:** Search results with abstracts and related topics

**Example:**
```json
{
  "tool": "web_search",
  "input": "Python programming"
}
```

---

### 2. Code Executor (`execute_code`)

Execute Python code safely with output validation.

**Input:** Code string or JSON with code and expected output  
**Output:** Execution results and comparison

**Example:**
```json
{
  "tool": "execute_code",
  "input": "{\"code\": \"print(5*5)\", \"expected_output\": \"25\\n\", \"compare_mode\": \"exact\"}"
}
```

**Comparison Modes:**
- `exact`: Character-by-character match
- `fuzzy`: 80%+ similarity
- `contains`: Expected text in output

---

### 3. Calculator (`calculator`)

Perform mathematical calculations.

**Input:** Mathematical expression  
**Output:** Calculation result

**Example:**
```json
{
  "tool": "calculator",
  "input": "sqrt(144) + pow(2, 3)"
}
```

---

### 4. File Operations

**Write File (`write_file`)**
```json
{
  "tool": "write_file",
  "input": "test.txt|Hello, World!"
}
```

**Read File (`read_file`)**
```json
{
  "tool": "read_file",
  "input": "test.txt"
}
```

---

### 5. Get Time (`get_time`)

Get current date and time.

**Input:** None (any string)  
**Output:** Current datetime information

---

## 🎨 Creating Custom Agents

### Define a New Agent Role

Edit `src/agent/agent_roles.py`:

```python
class AgentRole(Enum):
    RESEARCHER = "researcher"
    WRITER = "writer"
    ANALYST = "analyst"
    ASSISTANT = "assistant"
    CODER = "coder"  # NEW: Add your custom role
```

### Create the Agent

Edit `src/systems/multi_agent.py`:

```python
self.agents = {
    # ... existing agents ...
    "coder": ToolUsingAgent(
        "Coding Agent",
        AgentRole.CODER,
        self.tool_registry
    )
}
```

### Define Agent Behavior

Edit `src/agent/base_agent.py`:

```python
base_prompts = {
    # ... existing prompts ...
    AgentRole.CODER: """
        You are an expert coding agent.
        Your job is to write clean, efficient code.
        Always test your code and validate outputs.
    """
}
```

---

## 🔧 Adding New Tools

### Step 1: Create Tool Function

Edit `src/tools/tool_registry.py`:

```python
def _my_custom_tool(self, input_data: str) -> Dict:
    """My custom tool description"""
    try:
        # Your tool logic here
        result = process_input(input_data)
        
        return {
            "result": result,
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }
```

### Step 2: Register the Tool

```python
def _register_default_tools(self):
    # ... existing tools ...
    
    self.register_tool(
        "my_tool",
        self._my_custom_tool,
        "Description of what my tool does"
    )
```

### Step 3: Use the Tool

```bash
curl -X POST http://localhost:5000/tool/use \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "my_tool",
    "input": "test input"
  }'
```

---

## ⚙️ Configuration

### Ollama Settings

Edit `src/config/settings.py`:

```python
# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # Change to your preferred model
```

### Flask Settings

```python
# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
```

### Code Executor Settings

Edit `src/tools/code_executor.py`:

```python
# Timeout and memory limits
executor_tool = CodeExecutorTool(
    timeout=5,       # seconds
    memory_limit=50  # MB
)
```

---

## 🐛 Troubleshooting

### Ollama Connection Error

**Problem:** `Error communicating with Ollama`

**Solution:**
1. Make sure Ollama is running: `ollama serve`
2. Check if model is downloaded: `ollama list`
3. Pull model if needed: `ollama pull llama3.2`

---

### Import Errors

**Problem:** `ImportError: cannot import name 'ToolEnabledMultiAgentSystem'`

**Solution:**
1. Ensure all `__init__.py` files exist
2. Check file structure matches documentation
3. Run from project root directory: `python main.py`

---

### Code Execution Timeout

**Problem:** Code execution times out

**Solution:**
1. Increase timeout in `src/tools/code_executor.py`
2. Optimize your code
3. Check for infinite loops

---

### Port Already in Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
# Edit FLASK_PORT in src/config/settings.py
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

### Coding Standards

- Follow PEP 8 style guide
- Add docstrings to all functions
- Include type hints where possible
- Write tests for new features
- Update documentation

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Ollama** - For providing local LLM infrastructure
- **Flask** - For the web framework
- **DuckDuckGo** - For the search API

---

## 📧 Contact

For questions or support:
- Email: nasserobeid8@gmail.com

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Multi-agent system
- ✅ Tool integration
- ✅ Code execution with validation
- ✅ Web search capability

### Version 1.1 (Planned)
- [ ] Frontend web interface
- [ ] Database integration
- [ ] More specialized agents
- [ ] Improved error handling

### Version 2.0 (Future)
- [ ] Agent learning from feedback
- [ ] Custom workflow designer
- [ ] Multi-language support
- [ ] Cloud deployment options

---

## 📊 Performance Tips

1. **Use appropriate models**: `llama3.2` is faster than larger models
2. **Set reasonable timeouts**: Balance safety with performance
3. **Cache frequent requests**: Implement caching for repeated queries
4. **Monitor memory usage**: Track agent memory growth
5. **Batch operations**: Group similar tasks together

---

**Built with ❤️ by Nasser**

*Happy building! 🚀*
