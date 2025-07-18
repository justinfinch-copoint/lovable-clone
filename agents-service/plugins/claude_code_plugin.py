"""Claude Code Plugin for delegating code generation to Claude Code SDK"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
import json
from datetime import datetime

from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel
from claude_code_sdk import query, ClaudeCodeOptions, Message


class ClaudeCodePlugin(KernelBaseModel):
    """Plugin for delegating code generation to Claude Code SDK"""
    
    working_dir: Path = Path("/tmp/claude_code_workspace")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.working_dir.mkdir(exist_ok=True)
        
    @kernel_function(
        name="generate_game_code",
        description="Generate a complete Phaser 3 game using Claude Code"
    )
    async def generate_game_code(
        self, 
        technical_prompt: str,
        game_name: str = "game",
        max_turns: int = 10
    ) -> Dict[str, Any]:
        """
        Generate game code using Claude Code SDK
        
        Args:
            technical_prompt: Detailed technical specifications for the game
            game_name: Name for the game file (without extension)
            max_turns: Maximum number of turns for Claude Code
            
        Returns:
            Dict with success status, generated files, and execution details
        """
        try:
            # Create a unique project directory for this game
            project_dir = self.working_dir / f"{game_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_dir.mkdir(exist_ok=True)
            
            # Create the system prompt for Claude Code
            system_prompt = """You are a Phaser 3 game development expert. Your task is to create complete, functional HTML5 games.

IMPORTANT: Always create games as a single HTML file with embedded JavaScript and CSS.

Requirements:
- Use Phaser 3 CDN: https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js
- Include all game logic in <script> tags
- Add responsive design with proper viewport meta tags
- Implement complete game mechanics as specified
- Include comments explaining key game logic
- Ensure the game is immediately playable when opened in a browser

File naming: Always save the game as 'game.html' unless specified otherwise."""

            # Configure Claude Code options
            options = ClaudeCodeOptions(
                max_turns=max_turns,
                system_prompt=system_prompt,
                cwd=project_dir,
                allowed_tools=[
                    "Write",
                    "Read", 
                    "Edit",
                    "MultiEdit",
                    "Bash",
                    "LS",
                    "Glob"
                ],
                permission_mode="bypassPermissions"  # Auto-accept edits for automation
            )
            
            # Enhanced prompt with file creation instruction
            full_prompt = f"""{technical_prompt}

Please create the complete game as a single HTML file named 'game.html' in the current directory. The game should be fully functional and ready to play."""
            
            # Execute Claude Code
            messages: List[Message] = []
            claude_code_output = []
            
            async for message in query(prompt=full_prompt, options=options):
                messages.append(message)
                # Store progress messages for the agent to communicate
                if hasattr(message, 'content') and message.content:
                    claude_code_output.append({
                        'type': getattr(message, 'type', 'unknown'),
                        'content': str(message.content)[:200]  # Truncate for progress updates
                    })
            
            # Check if game.html was created
            game_file = project_dir / "game.html"
            if game_file.exists():
                game_code = game_file.read_text()
                
                # Copy to a more permanent location
                output_dir = Path("/workspaces/lovable-clone/generated_games")
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / f"{game_name}.html"
                output_file.write_text(game_code)
                
                return {
                    "success": True,
                    "game_code": game_code,
                    "filename": f"{game_name}.html",
                    "output_path": str(output_file),
                    "project_dir": str(project_dir),
                    "claude_messages": len(messages),
                    "execution_log": claude_code_output
                }
            else:
                # Try to find any HTML files created
                html_files = list(project_dir.glob("*.html"))
                if html_files:
                    game_file = html_files[0]
                    game_code = game_file.read_text()
                    
                    return {
                        "success": True,
                        "game_code": game_code,
                        "filename": game_file.name,
                        "output_path": str(game_file),
                        "project_dir": str(project_dir),
                        "claude_messages": len(messages),
                        "execution_log": claude_code_output
                    }
                else:
                    return {
                        "success": False,
                        "error": "No HTML file was generated",
                        "project_dir": str(project_dir),
                        "claude_messages": len(messages),
                        "execution_log": claude_code_output
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    @kernel_function(
        name="review_and_improve_game",
        description="Review and improve existing game code using Claude Code"
    )
    async def review_and_improve_game(
        self,
        existing_code: str,
        improvement_request: str,
        game_name: str = "improved_game",
        max_turns: int = 8
    ) -> Dict[str, Any]:
        """
        Review and improve existing game code
        
        Args:
            existing_code: The current game HTML code
            improvement_request: Specific improvements requested
            game_name: Name for the improved game
            max_turns: Maximum number of turns for Claude Code
            
        Returns:
            Dict with improved code and changes made
        """
        try:
            # Create project directory
            project_dir = self.working_dir / f"{game_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project_dir.mkdir(exist_ok=True)
            
            # Write existing code to file
            existing_file = project_dir / "current_game.html"
            existing_file.write_text(existing_code)
            
            # System prompt for improvements
            system_prompt = """You are a Phaser 3 game improvement specialist. Your task is to review and enhance existing games.

Focus on:
- Maintaining all existing functionality
- Implementing the requested improvements
- Optimizing performance where possible
- Improving code organization
- Adding helpful comments for changes made"""
            
            options = ClaudeCodeOptions(
                max_turns=max_turns,
                system_prompt=system_prompt,
                cwd=project_dir,
                allowed_tools=[
                    "Read",
                    "Write",
                    "Edit",
                    "MultiEdit",
                    "Bash",
                    "LS"
                ],
                permission_mode="bypassPermissions"
            )
            
            improvement_prompt = f"""Please review and improve the game in 'current_game.html'.

Improvement request: {improvement_request}

Create an improved version as 'improved_game.html' that addresses the requested changes while maintaining all existing functionality."""
            
            messages: List[Message] = []
            async for message in query(prompt=improvement_prompt, options=options):
                messages.append(message)
            
            # Check for improved game
            improved_file = project_dir / "improved_game.html"
            if improved_file.exists():
                improved_code = improved_file.read_text()
                
                return {
                    "success": True,
                    "improved_code": improved_code,
                    "filename": "improved_game.html",
                    "project_dir": str(project_dir),
                    "changes_made": self._analyze_changes(existing_code, improved_code)
                }
            else:
                return {
                    "success": False,
                    "error": "No improved game file was created",
                    "project_dir": str(project_dir)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    @kernel_function(
        name="get_claude_code_status",
        description="Check if Claude Code SDK is properly configured"
    )
    async def get_claude_code_status(self) -> Dict[str, Any]:
        """Check Claude Code SDK configuration and status"""
        try:
            # Check if Claude Code CLI is available
            result = await asyncio.create_subprocess_exec(
                "claude-code", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            claude_cli_available = result.returncode == 0
            claude_cli_version = stdout.decode().strip() if claude_cli_available else None
            
            # Check API key
            api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
            
            return {
                "claude_sdk_available": True,
                "claude_cli_available": claude_cli_available,
                "claude_cli_version": claude_cli_version,
                "api_key_configured": api_key_set,
                "working_directory": str(self.working_dir),
                "status": "ready" if claude_cli_available and api_key_set else "not_configured"
            }
            
        except Exception as e:
            return {
                "claude_sdk_available": False,
                "error": str(e),
                "status": "error"
            }
    
    def _analyze_changes(self, original: str, improved: str) -> List[str]:
        """Analyze what changed between original and improved code"""
        changes = []
        
        # Simple heuristic analysis
        if len(improved) > len(original) * 1.1:
            changes.append("Added significant new features")
        elif len(improved) < len(original) * 0.9:
            changes.append("Optimized and reduced code size")
        
        # Check for specific improvements
        improvements_keywords = {
            "performance": ["requestAnimationFrame", "object pool", "cache"],
            "ui": ["button", "menu", "hud", "interface"],
            "graphics": ["particle", "animation", "effect", "shader"],
            "audio": ["sound", "music", "audio"],
            "gameplay": ["difficulty", "level", "score", "powerup"],
        }
        
        for category, keywords in improvements_keywords.items():
            for keyword in keywords:
                if keyword.lower() in improved.lower() and keyword.lower() not in original.lower():
                    changes.append(f"Enhanced {category}")
                    break
        
        if not changes:
            changes.append("Refined existing implementation")
            
        return changes