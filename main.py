from flask import Flask, request, jsonify
from  src.system.multi_agent import ToolEnabledMultiAgentSystem
from datetime import datetime

app = Flask(__name__)
system = ToolEnabledMultiAgentSystem()


@app.route('/health', methods=['GET'])
def health_check():
    """Check server status"""
    return jsonify({
        "status": "healthy",
        "agents": list(system.agents.keys()),
        "tools": system.tool_registry.list_tools(),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/tools', methods=['GET'])
def list_tools():
    """List all available tools"""
    return jsonify({
        "tools": system.tool_registry.list_tools()
    })


@app.route('/agent/task', methods=['POST'])
def agent_task():
    """
    Send a task to a specific agent
    The agent will automatically use tools if needed
    
    Example:
    POST /agent/task
    {
        "agent": "researcher",
        "task": "Find information about quantum computing"
    }
    """
    data = request.get_json()
    
    if not data or 'agent' not in data or 'task' not in data:
        return jsonify({"error": "Agent and task required"}), 400
    
    agent_name = data['agent']
    task = data['task']
    context = data.get('context')
    
    if agent_name not in system.agents:
        return jsonify({"error": f"Unknown agent: {agent_name}"}), 400
    
    result = system.agents[agent_name].think(task, context)
    
    return jsonify({
        "agent": agent_name,
        "task": task,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/tool/use', methods=['POST'])
def use_tool():
    """
    Directly use a tool without agent reasoning
    
    Example:
    POST /tool/use
    {
        "tool": "web_search",
        "input": "Python programming tutorials"
    }
    """
    data = request.get_json()
    
    if not data or 'tool' not in data or 'input' not in data:
        return jsonify({"error": "Tool and input required"}), 400
    
    # Use any agent to execute the tool
    result = system.agents["assistant"].use_tool_directly(
        data['tool'],
        data['input']
    )
    
    return jsonify(result)


@app.route('/workflow/research-and-write', methods=['POST'])
def research_and_write():
    """
    Run the research and write workflow
    
    Example:
    POST /workflow/research-and-write
    {
        "topic": "The history of artificial intelligence"
    }
    """
    data = request.get_json()
    
    if not data or 'topic' not in data:
        return jsonify({"error": "Topic required"}), 400
    
    result = system.research_and_write(data['topic'])
    
    return jsonify(result)


@app.route('/memory/<agent_name>', methods=['GET'])
def get_memory(agent_name):
    """Get an agent's memory"""
    if agent_name not in system.agents:
        return jsonify({"error": "Unknown agent"}), 404
    
    memory = system.agents[agent_name].get_memory()
    
    return jsonify({
        "agent": agent_name,
        "memory": memory,
        "total_interactions": len(memory)
    })


# ============================================================================
# RUN THE SERVER
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Tool-Enabled Multi-Agent System Starting...")
    print("="*60)
    print(f"\nEndpoints:")
    print("  - GET  /health                    : Server status")
    print("  - GET  /tools                     : List all tools")
    print("  - POST /agent/task                : Send task to agent")
    print("  - POST /tool/use                  : Use tool directly")
    print("  - POST /workflow/research-and-write : Research & write workflow")
    print("  - GET  /memory/<agent>            : Get agent memory")
    print(f"\nServer: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
