"""
Logging functionality for Ollama Agents SDK with Rich visuals
"""
import logging
import sys
from typing import Optional
from enum import Enum
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree


class LogLevel(Enum):
    """Log levels for the Ollama Agents SDK"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RichLogger:
    """Logger class for the Ollama Agents SDK with Rich visuals"""

    def __init__(self, name: str = "ollama_agents", level: LogLevel = LogLevel.INFO, enabled: bool = False):
        self.name = name
        self.console = Console()
        self.enabled = enabled

        # Create a standard logger but use RichHandler for formatting
        self.logger = logging.getLogger(name)
        
        # Set level based on enabled state
        if enabled:
            self.logger.setLevel(getattr(logging, level.value.upper()))
        else:
            # Disable logging by setting to CRITICAL+1 (higher than any log level)
            self.logger.setLevel(logging.CRITICAL + 1)

        # Prevent adding multiple handlers if logger already exists
        if not self.logger.handlers:
            # Use RichHandler for beautiful console output
            rich_handler = RichHandler(
                console=self.console,
                show_time=True,
                show_path=True,
                markup=True,
                rich_tracebacks=True
            )
            self.logger.addHandler(rich_handler)

    def debug(self, message: str, agent_id: Optional[str] = None, **kwargs):
        """Log a debug message"""
        self._log(logging.DEBUG, message, agent_id, **kwargs)

    def info(self, message: str, agent_id: Optional[str] = None, **kwargs):
        """Log an info message"""
        self._log(logging.INFO, message, agent_id, **kwargs)

    def warning(self, message: str, agent_id: Optional[str] = None, **kwargs):
        """Log a warning message"""
        self._log(logging.WARNING, message, agent_id, **kwargs)

    def error(self, message: str, agent_id: Optional[str] = None, **kwargs):
        """Log an error message"""
        self._log(logging.ERROR, message, agent_id, **kwargs)

    def critical(self, message: str, agent_id: Optional[str] = None, **kwargs):
        """Log a critical message"""
        self._log(logging.CRITICAL, message, agent_id, **kwargs)

    def _log(self, level: int, message: str, agent_id: Optional[str] = None, **kwargs):
        """Internal method to log a message"""
        if not self.enabled:
            return
            
        if agent_id:
            message = f"[bold blue]Agent:[/bold blue] {agent_id} | {message}"

        if kwargs:
            extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            message += f" [dim]| Extra: {extra_info}[/dim]"

        self.logger.log(level, message)

    def log_agent_stats(self, agent_id: str, stats: dict):
        """Log agent statistics in a formatted table"""
        table = Table(title=f"Agent {agent_id} Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right")

        for key, value in stats.items():
            table.add_row(str(key), str(value))

        self.console.print(table)

    def log_handoff(self, from_agent: str, to_agent: str, reason: str = ""):
        """Log agent handoff with visual tree"""
        tree = Tree(f"[bold green]Agent Handoff[/bold green]")
        from_branch = tree.add(f"[blue]From:[/blue] {from_agent}")
        to_branch = tree.add(f"[green]To:[/green] {to_agent}")
        if reason:
            to_branch.add(f"[yellow]Reason:[/yellow] {reason}")

        self.console.print(tree)

    def log_token_usage(self, usage: dict):
        """Log token usage with visual representation"""
        panel = Panel(
            f"[bold]Token Usage:[/bold]\n"
            f"Prompt tokens: {usage.get('prompt_tokens', 0)}\n"
            f"Completion tokens: {usage.get('completion_tokens', 0)}\n"
            f"Total tokens: {usage.get('total_tokens', 0)}",
            title="Token Usage",
            border_style="blue"
        )
        self.console.print(panel)

    def log_tool_call(self, tool_name: str, args: dict, result: str = ""):
        """Log tool calls with visual representation"""
        tree = Tree(f"[bold cyan]Tool Call:[/bold cyan] {tool_name}")
        args_branch = tree.add("[yellow]Arguments:[/yellow]")
        for key, value in args.items():
            args_branch.add(f"[dim]{key}:[/dim] {value}")

        if result:
            tree.add(f"[green]Result:[/green] {result[:100]}{'...' if len(result) > 100 else ''}")

        self.console.print(tree)


# Global logger instance - lazy initialization for better startup performance
_global_logger = None
_logging_enabled = False


def get_logger() -> RichLogger:
    """Get the global logger instance (lazy initialized)"""
    global _global_logger, _logging_enabled
    if _global_logger is None:
        _global_logger = RichLogger(enabled=_logging_enabled)
    return _global_logger


def enable_logging(level: LogLevel = LogLevel.INFO):
    """Enable logging globally"""
    global _logging_enabled
    _logging_enabled = True
    logger = get_logger()
    logger.enabled = True
    logger.logger.setLevel(getattr(logging, level.value.upper()))


def disable_logging():
    """Disable logging globally"""
    global _logging_enabled
    _logging_enabled = False
    logger = get_logger()
    logger.enabled = False
    logger.logger.setLevel(logging.CRITICAL + 1)


def set_global_log_level(level: LogLevel):
    """Set the global log level and enable logging"""
    global _logging_enabled
    _logging_enabled = True
    logger = get_logger()
    logger.enabled = True
    logger.logger.setLevel(getattr(logging, level.value.upper()))