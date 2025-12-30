"""
Simple Web UI for agent management.
Provides a Flask-based web interface for managing and monitoring agents.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

try:
    from flask import Flask, render_template_string, request, jsonify, send_from_directory
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from .agent import Agent
from .stats import get_stats_tracker
from .logger import get_logger

logger = get_logger()


class AgentManager:
    """Manages multiple agents for the Web UI"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.conversations: Dict[str, List[Dict]] = {}
    
    def add_agent(self, agent: Agent):
        """Add an agent to the manager"""
        self.agents[agent.name] = agent
        self.conversations[agent.name] = []
        logger.info(f"➕ Added agent to manager: {agent.name}")
    
    def remove_agent(self, agent_name: str):
        """Remove an agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            del self.conversations[agent_name]
            logger.info(f"➖ Removed agent: {agent_name}")
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents with their info"""
        return [
            {
                "name": agent.name,
                "model": agent.model,
                "tools": len(agent.tools),
                "conversation_length": len(self.conversations.get(agent.name, []))
            }
            for agent in self.agents.values()
        ]
    
    def chat(self, agent_name: str, message: str) -> Dict[str, Any]:
        """Send a message to an agent"""
        agent = self.get_agent(agent_name)
        if not agent:
            return {"error": "Agent not found"}
        
        # Add user message to conversation
        self.conversations[agent_name].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get response
        response = agent.chat(message)
        
        # Add agent response to conversation
        self.conversations[agent_name].append({
            "role": "assistant",
            "content": response.get("content", ""),
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def get_conversation(self, agent_name: str) -> List[Dict]:
        """Get conversation history for an agent"""
        return self.conversations.get(agent_name, [])
    
    def clear_conversation(self, agent_name: str):
        """Clear conversation history"""
        if agent_name in self.conversations:
            self.conversations[agent_name] = []


# HTML Templates
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ollama Agents Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; font-size: 1.1em; }
        .main-content { display: flex; height: calc(100vh - 160px); }
        .sidebar {
            width: 300px;
            background: #f7fafc;
            border-right: 1px solid #e2e8f0;
            overflow-y: auto;
        }
        .agent-list { padding: 20px; }
        .agent-card {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.3s;
        }
        .agent-card:hover { border-color: #667eea; transform: translateY(-2px); }
        .agent-card.active { border-color: #667eea; background: #f0f4ff; }
        .agent-name { font-weight: bold; font-size: 1.1em; margin-bottom: 5px; }
        .agent-info { font-size: 0.9em; color: #64748b; }
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f7fafc;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
            max-width: 80%;
        }
        .message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
        }
        .message.assistant {
            background: white;
            border: 1px solid #e2e8f0;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1em;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover { background: #5a67d8; transform: translateY(-2px); }
        .stats {
            padding: 20px;
            background: #f7fafc;
            border-top: 1px solid #e2e8f0;
        }
        .stat-row { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .loading { text-align: center; color: #64748b; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Ollama Agents Manager</h1>
            <div class="subtitle">Manage and chat with your AI agents</div>
        </header>
        <div class="main-content">
            <div class="sidebar">
                <div class="agent-list" id="agentList">
                    <div class="loading">Loading agents...</div>
                </div>
            </div>
            <div class="chat-area">
                <div class="messages" id="messages">
                    <div class="loading">Select an agent to start chatting</div>
                </div>
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Type your message..." disabled>
                    <button onclick="sendMessage()" id="sendButton" disabled>Send</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentAgent = null;
        
        async function loadAgents() {
            const response = await fetch('/api/agents');
            const agents = await response.json();
            
            const listEl = document.getElementById('agentList');
            listEl.innerHTML = agents.map(agent => `
                <div class="agent-card" onclick="selectAgent('${agent.name}')">
                    <div class="agent-name">${agent.name}</div>
                    <div class="agent-info">
                        Model: ${agent.model}<br>
                        Tools: ${agent.tools}<br>
                        Messages: ${agent.conversation_length}
                    </div>
                </div>
            `).join('');
        }
        
        async function selectAgent(name) {
            currentAgent = name;
            
            // Update UI
            document.querySelectorAll('.agent-card').forEach(card => {
                card.classList.remove('active');
            });
            event.target.closest('.agent-card').classList.add('active');
            
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendButton').disabled = false;
            
            // Load conversation
            const response = await fetch(`/api/conversation/${name}`);
            const conversation = await response.json();
            displayConversation(conversation);
        }
        
        function displayConversation(messages) {
            const messagesEl = document.getElementById('messages');
            messagesEl.innerHTML = messages.map(msg => `
                <div class="message ${msg.role}">
                    <div>${msg.content}</div>
                    <small style="opacity: 0.7; font-size: 0.8em;">${new Date(msg.timestamp).toLocaleTimeString()}</small>
                </div>
            `).join('');
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }
        
        async function sendMessage() {
            if (!currentAgent) return;
            
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            input.value = '';
            input.disabled = true;
            document.getElementById('sendButton').disabled = true;
            
            // Add user message immediately
            const messagesEl = document.getElementById('messages');
            messagesEl.innerHTML += `
                <div class="message user">
                    <div>${message}</div>
                    <small style="opacity: 0.7; font-size: 0.8em;">${new Date().toLocaleTimeString()}</small>
                </div>
            `;
            messagesEl.scrollTop = messagesEl.scrollHeight;
            
            // Send to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent: currentAgent, message })
            });
            
            const data = await response.json();
            
            // Add assistant message
            messagesEl.innerHTML += `
                <div class="message assistant">
                    <div>${data.content}</div>
                    <small style="opacity: 0.7; font-size: 0.8em;">${new Date().toLocaleTimeString()}</small>
                </div>
            `;
            messagesEl.scrollTop = messagesEl.scrollHeight;
            
            input.disabled = false;
            document.getElementById('sendButton').disabled = false;
            input.focus();
        }
        
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        // Load agents on start
        loadAgents();
        setInterval(loadAgents, 5000);  // Refresh every 5s
    </script>
</body>
</html>
"""


def create_web_ui(agent_manager: AgentManager, host: str = "0.0.0.0", port: int = 5000):
    """
    Create and run a web UI for agent management.
    
    Args:
        agent_manager: AgentManager instance with agents
        host: Host to bind to
        port: Port to run on
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is required for Web UI. Install with: pip install flask")
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/agents')
    def api_agents():
        return jsonify(agent_manager.list_agents())
    
    @app.route('/api/conversation/<agent_name>')
    def api_conversation(agent_name):
        return jsonify(agent_manager.get_conversation(agent_name))
    
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        data = request.json
        agent_name = data.get('agent')
        message = data.get('message')
        
        if not agent_name or not message:
            return jsonify({"error": "Missing agent or message"}), 400
        
        response = agent_manager.chat(agent_name, message)
        return jsonify(response)
    
    @app.route('/api/stats')
    def api_stats():
        stats = get_stats_tracker().get_all_stats()
        if stats:
            return jsonify(asdict(stats))
        return jsonify({})
    
    logger.info(f"🌐 Starting Web UI on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)


# Export
__all__ = ['AgentManager', 'create_web_ui']
