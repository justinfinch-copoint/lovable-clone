"""Plugins module for game development tools"""

from .file_operations import FileOperationsPlugin
from .phaser_tools import PhaserToolsPlugin
from .claude_code_plugin import ClaudeCodePlugin
from .claude_code_bridge import ClaudeCodeBridge
# from .code_generation import CodeGenerationPlugin
# from .project_management import ProjectManagementPlugin

__all__ = [
    "FileOperationsPlugin",
    "PhaserToolsPlugin",
    "ClaudeCodePlugin",
    "ClaudeCodeBridge",
    # "CodeGenerationPlugin",
    # "ProjectManagementPlugin",
]