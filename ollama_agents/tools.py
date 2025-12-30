"""
Tool registration and calling functionality for Ollama agents
"""
import inspect
from typing import Callable, Dict, Any, List, Optional, get_origin, get_args
from functools import wraps
import json
import re


class ToolRegistry:
    """Registry for managing tools that agents can use"""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register_tool(self, func: Callable):
        """Register a function as a tool"""
        name = func.__name__
        self.tools[name] = func
        return func

    def get_ollama_tools(self) -> List[Dict[str, Any]]:
        """Get tools in Ollama-compatible format"""
        ollama_tools = []

        for name, func in self.tools.items():
            # Extract function signature and docstring
            sig = inspect.signature(func)
            docstring = inspect.getdoc(func) or ""

            # Parse parameters with better type detection
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }

            for param_name, param in sig.parameters.items():
                param_info = self._infer_parameter_type(param)

                # Check if parameter has a default value
                if param.default == inspect.Parameter.empty:
                    parameters["required"].append(param_name)

                # Extract parameter description from docstring if available
                param_desc = self._extract_param_description(docstring, param_name)
                if param_desc:
                    param_info["description"] = param_desc

                parameters["properties"][param_name] = param_info

            tool_def = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": docstring.split('\n\n')[0] if docstring else "",  # First line as description
                    "parameters": parameters
                }
            }

            ollama_tools.append(tool_def)

        return ollama_tools

    def _infer_parameter_type(self, param: inspect.Parameter) -> Dict[str, Any]:
        """Infer parameter type from annotation"""
        param_info = {"type": "string"}  # Default to string

        if param.annotation != inspect.Parameter.empty:
            annotation = param.annotation

            # Handle Optional/Union types
            origin = get_origin(annotation)
            args = get_args(annotation)

            if origin is not None and origin.__name__ in ['Union', 'Optional']:
                # For Union/Optional, we'll use the first non-None type
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    annotation = non_none_types[0]

            # Map Python types to JSON schema types
            if annotation == int:
                param_info["type"] = "integer"
            elif annotation == float:
                param_info["type"] = "number"
            elif annotation == bool:
                param_info["type"] = "boolean"
            elif annotation == str:
                param_info["type"] = "string"
            elif annotation == list or origin is list:
                param_info["type"] = "array"
                # Try to determine item type if possible
                if args:
                    item_type = args[0] if args else str
                    if item_type == int:
                        param_info["items"] = {"type": "integer"}
                    elif item_type == float:
                        param_info["items"] = {"type": "number"}
                    elif item_type == bool:
                        param_info["items"] = {"type": "boolean"}
                    else:
                        param_info["items"] = {"type": "string"}
            elif annotation == dict or origin is dict:
                param_info["type"] = "object"

        return param_info

    def _extract_param_description(self, docstring: str, param_name: str) -> Optional[str]:
        """Extract parameter description from docstring"""
        # Look for Google-style or Sphinx-style docstrings
        lines = docstring.split('\n')

        # Google style: Args: \n    param_name (type): description
        for i, line in enumerate(lines):
            if 'Args:' in line or 'Parameters:' in line or 'Arguments:' in line:
                # Look for the parameter in the following lines
                j = i + 1
                while j < len(lines):
                    line = lines[j].strip()
                    if not line or line.startswith(':'):  # New section starts
                        break
                    # Check if this line starts with the parameter name
                    if line.startswith(f'{param_name} ') or line.startswith(f'{param_name} ('):
                        # Extract description part
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            desc = parts[1].strip()
                            return desc
                    j += 1

        # Sphinx style: :param param_name: description
        for line in lines:
            if f':param {param_name}:' in line:
                desc = line.split(f':param {param_name}:', 1)[1].strip()
                return desc

        return None

    def execute_tool(self, name: str, arguments: Dict[str, Any], tracer=None) -> Any:
        """Execute a registered tool with given arguments"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in registry")

        func = self.tools[name]

        # If tracer is provided, add timing information
        if tracer:
            import time
            start_time = time.time()
            try:
                result = func(**arguments)
                execution_time = time.time() - start_time

                # Log tool execution with timing
                tracer.log_event(
                    "tool.execution",
                    data={
                        "tool_name": name,
                        "arguments": arguments,
                        "result_type": type(result).__name__,
                        "execution_time": execution_time
                    }
                )

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                # Log tool execution error with timing
                tracer.log_event(
                    "tool.execution.error",
                    data={
                        "tool_name": name,
                        "arguments": arguments,
                        "error": str(e),
                        "execution_time": execution_time
                    }
                )
                raise
        else:
            # Execute without timing if no tracer provided
            return func(**arguments)


def tool(description: Optional[str] = None):
    """
    Decorator to register a function as a tool with optional description

    Args:
        description: Optional description for the tool (overrides function docstring)
    """
    def decorator(func: Callable) -> Callable:
        # If description is provided, attach it to the function
        if description:
            # Preserve existing docstring if it exists, otherwise use the provided description
            if not func.__doc__:
                func.__doc__ = description
            else:
                # Prepend the description to the existing docstring
                func.__doc__ = f"{description}\n\n{func.__doc__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._is_tool = True
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__

        return wrapper

    return decorator