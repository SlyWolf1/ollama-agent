"""
Model Context Protocol (MCP) support for Ollama Agents SDK
This module provides standardized interfaces for context management, tool discovery, and resource handling.
"""
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
from .tools import ToolRegistry


class MCPResourceType(Enum):
    """Types of resources that can be managed via MCP"""
    FILE = "file"
    DOCUMENT = "document"
    WEBPAGE = "webpage"
    DATABASE = "database"
    API = "api"
    TOOL = "tool"


@dataclass
class MCPResource:
    """Represents a resource that can be accessed via MCP"""
    uri: str
    type: MCPResourceType
    name: str
    description: str = ""
    metadata: Optional[Dict[str, Any]] = None


class MCPContextManager:
    """Manages context resources following MCP standards"""
    
    def __init__(self):
        self.resources: List[MCPResource] = []
        self.tools: List[Dict[str, Any]] = []
    
    def add_resource(self, resource: MCPResource):
        """Add a resource to the context"""
        self.resources.append(resource)
    
    def remove_resource(self, uri: str):
        """Remove a resource by URI"""
        self.resources = [r for r in self.resources if r.uri != uri]
    
    def get_resources(self) -> List[MCPResource]:
        """Get all resources"""
        return self.resources[:]
    
    def register_tool(self, name: str, description: str, parameters: Dict[str, Any]):
        """Register a tool following MCP standards"""
        tool_def = {
            "name": name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys())  # Assuming all parameters are required
            }
        }
        self.tools.append(tool_def)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools"""
        return self.tools[:]
    
    def export_context(self) -> Dict[str, Any]:
        """Export context in MCP-compatible format"""
        return {
            "resources": [
                {
                    "uri": r.uri,
                    "type": r.type.value,
                    "name": r.name,
                    "description": r.description,
                    "metadata": r.metadata or {}
                }
                for r in self.resources
            ],
            "tools": self.tools
        }
    
    def import_context(self, context_data: Dict[str, Any]):
        """Import context from MCP-compatible format"""
        self.resources = []
        for res_data in context_data.get("resources", []):
            resource = MCPResource(
                uri=res_data["uri"],
                type=MCPResourceType(res_data["type"]),
                name=res_data["name"],
                description=res_data.get("description", ""),
                metadata=res_data.get("metadata")
            )
            self.resources.append(resource)
        
        self.tools = context_data.get("tools", [])


class MCPToolAdapter:
    """Adapter to convert standard tools to MCP-compatible format"""
    
    @staticmethod
    def convert_tool_registry_to_mcp(tool_registry: 'ToolRegistry') -> List[Dict[str, Any]]:
        """Convert a ToolRegistry to MCP-compatible tool definitions"""
        mcp_tools = []
        
        for name, func in tool_registry.tools.items():
            # Extract function signature and docstring
            import inspect
            sig = inspect.signature(func)
            docstring = inspect.getdoc(func) or ""
            
            # Parse parameters
            properties = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                param_info = {"type": "string"}  # Default to string
                
                # Try to infer type from annotation
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == int:
                        param_info["type"] = "integer"
                    elif param.annotation == float:
                        param_info["type"] = "number"
                    elif param.annotation == bool:
                        param_info["type"] = "boolean"
                    elif param.annotation == str:
                        param_info["type"] = "string"
                    elif param.annotation == list:
                        param_info["type"] = "array"
                
                # Check if parameter has a default value
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
                
                properties[param_name] = param_info
            
            mcp_tool = {
                "name": name,
                "description": docstring.split('\n\n')[0] if docstring else "",
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
            
            mcp_tools.append(mcp_tool)
        
        return mcp_tools


class MCPContext:
    """Main MCP context class for agents"""
    
    def __init__(self):
        self.context_manager = MCPContextManager()
        self.session_history: List[Dict[str, Any]] = []
    
    def add_to_history(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the session history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp(),
            "metadata": metadata or {}
        }
        self.session_history.append(message)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the session history"""
        return self.session_history[:]
    
    def clear_history(self):
        """Clear the session history"""
        self.session_history.clear()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def export_mcp_context(self) -> str:
        """Export the entire MCP context as JSON"""
        context_data = {
            "context": self.context_manager.export_context(),
            "history": self.session_history
        }
        return json.dumps(context_data, indent=2)
    
    def import_mcp_context(self, context_json: str):
        """Import MCP context from JSON"""
        context_data = json.loads(context_json)
        
        # Import context manager data
        self.context_manager.import_context(context_data.get("context", {}))
        
        # Import history
        self.session_history = context_data.get("history", [])
    
    def register_tool_from_registry(self, tool_registry: 'ToolRegistry'):
        """Register all tools from a ToolRegistry"""
        mcp_tools = MCPToolAdapter.convert_tool_registry_to_mcp(tool_registry)
        for tool in mcp_tools:
            self.context_manager.register_tool(
                tool["name"],
                tool["description"],
                tool["inputSchema"]["properties"]
            )