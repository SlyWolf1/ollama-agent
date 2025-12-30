"""
Built-in tools for Ollama agents.
Provides ready-to-use tools for common tasks.
"""

import os
import json
import subprocess
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from .tools import tool


# File System Tools
@tool("Read a file")
def read_file(file_path: str) -> str:
    """Read contents of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool("Write to a file")
def write_file(file_path: str, content: str) -> str:
    """Write content to a file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool("List directory contents")
def list_directory(directory: str = ".") -> str:
    """List files and directories in a directory"""
    try:
        items = os.listdir(directory)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# Web Tools
@tool("Make HTTP GET request")
def http_get(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """Make an HTTP GET request"""
    try:
        response = requests.get(url, headers=headers or {}, timeout=10)
        return json.dumps({
            "status_code": response.status_code,
            "content": response.text[:1000],  # Limit content
            "headers": dict(response.headers)
        })
    except Exception as e:
        return f"Error making request: {str(e)}"


@tool("Make HTTP POST request")
def http_post(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> str:
    """Make an HTTP POST request"""
    try:
        response = requests.post(url, json=data, headers=headers or {}, timeout=10)
        return json.dumps({
            "status_code": response.status_code,
            "content": response.text[:1000],
            "headers": dict(response.headers)
        })
    except Exception as e:
        return f"Error making request: {str(e)}"


# System Tools
@tool("Execute shell command")
def execute_command(command: str, timeout: int = 30) -> str:
    """Execute a shell command (use with caution!)"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })
    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool("Get current time")
def get_current_time() -> str:
    """Get the current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool("Get environment variable")
def get_env_var(var_name: str) -> str:
    """Get an environment variable value"""
    value = os.environ.get(var_name)
    if value is None:
        return f"Environment variable '{var_name}' not found"
    return value


# Data Tools
@tool("Parse JSON")
def parse_json(json_str: str) -> str:
    """Parse a JSON string"""
    try:
        data = json.loads(json_str)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error parsing JSON: {str(e)}"


@tool("Format JSON")
def format_json(data: Any) -> str:
    """Format data as JSON"""
    try:
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error formatting JSON: {str(e)}"


@tool("Calculate")
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression (use with caution!)"""
    try:
        # Only allow safe operations
        allowed_chars = "0123456789+-*/().**. "
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"


# Text Tools
@tool("Count words")
def count_words(text: str) -> str:
    """Count words in text"""
    word_count = len(text.split())
    return f"Word count: {word_count}"


@tool("Count characters")
def count_characters(text: str) -> str:
    """Count characters in text"""
    char_count = len(text)
    return f"Character count: {char_count}"


@tool("Convert to uppercase")
def to_uppercase(text: str) -> str:
    """Convert text to uppercase"""
    return text.upper()


@tool("Convert to lowercase")
def to_lowercase(text: str) -> str:
    """Convert text to lowercase"""
    return text.lower()


# Tool Collections
FILE_TOOLS = [read_file, write_file, list_directory]
WEB_TOOLS = [http_get, http_post]
SYSTEM_TOOLS = [execute_command, get_current_time, get_env_var]
DATA_TOOLS = [parse_json, format_json, calculate]
TEXT_TOOLS = [count_words, count_characters, to_uppercase, to_lowercase]

ALL_BUILTIN_TOOLS = (
    FILE_TOOLS + WEB_TOOLS + SYSTEM_TOOLS + DATA_TOOLS + TEXT_TOOLS
)


def get_tool_collection(collection_name: str) -> List:
    """Get a collection of tools by name"""
    collections = {
        "file": FILE_TOOLS,
        "web": WEB_TOOLS,
        "system": SYSTEM_TOOLS,
        "data": DATA_TOOLS,
        "text": TEXT_TOOLS,
        "all": ALL_BUILTIN_TOOLS,
    }
    return collections.get(collection_name.lower(), [])
