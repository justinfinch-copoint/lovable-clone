import os
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments

# Note: This requires the Claude Code SDK to be installed
# pip install @anthropic-ai/claude-code (if available for Python)
# For now, we'll simulate the interface based on the TypeScript SDK

try:
    # Attempt to import Claude Code SDK
    # This is a placeholder - the actual import would depend on the Python SDK structure
    from claude_code import query, SDKMessage
    CLAUDE_CODE_AVAILABLE = True
except ImportError:
    # Fallback if Claude Code SDK is not available
    CLAUDE_CODE_AVAILABLE = False
    print("⚠️ Claude Code SDK not available. Using fallback implementation.")


class ClaudeCodePlugin:
    """Plugin that integrates Claude Code SDK with Semantic Kernel"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 claude_code_path: Optional[str] = None,
                 working_directory: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.claude_code_path = claude_code_path or os.getenv("CLAUDE_CODE_PATH")
        self.working_directory = working_directory or os.getcwd()
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Claude Code SDK")
    
    @kernel_function(
        name="generate_phaser_game",
        description="Generate a complete Phaser 3 game using Claude Code SDK"
    )
    async def generate_phaser_game(
        self,
        prompt: str,
        max_turns: int = 10,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a Phaser 3 game using Claude Code SDK"""
        
        if not CLAUDE_CODE_AVAILABLE:
            return await self._fallback_generation(prompt)
        
        # Enhanced prompt with Phaser 3 expertise
        enhanced_prompt = f"""You are a Phaser 3 game development specialist. Create a complete, functional HTML5 game using the Phaser 3 framework.

USER REQUEST: {prompt}

REQUIREMENTS:
- Use Phaser 3 framework (latest stable version)
- Create a complete, runnable HTML file with embedded JavaScript
- Include proper DOCTYPE and meta tags for responsive design
- Use Phaser CDN: https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js

GAME STRUCTURE:
- Implement proper Phaser scene structure (preload, create, update)
- Include physics system (Arcade Physics recommended)
- Add player input handling (keyboard/mouse/touch)
- Implement collision detection and game mechanics
- Include score tracking and game states
- Add proper error handling

DELIVERABLE:
- Save the complete game as an HTML file
- Make it fully playable in a browser
- Include comments explaining the game logic
- Ensure responsive design for desktop and mobile

Generate the complete game now."""

        try:
            # Collect all messages and files from Claude Code execution
            messages = []
            files_created = []
            code_generated = {}
            
            # Create abort controller for the operation
            abort_controller = asyncio.Event()
            
            # Execute Claude Code query
            async for message in query({
                "prompt": enhanced_prompt,
                "abortController": abort_controller,
                "options": {
                    "maxTurns": max_turns,
                    "cwd": self.working_directory,
                    "executable": "node",
                    "pathToClaudeCodeExecutable": self.claude_code_path,
                    "model": model or os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                    "customSystemPrompt": None,  # Using our enhanced prompt instead
                    "permissionMode": "bypassPermissions"
                }
            }):
                messages.append(message)
                
                # Process different message types
                if message.get("type") == "assistant":
                    content = message.get("message", {}).get("content", "")
                    if isinstance(content, str):
                        # Look for file creation mentions
                        import re
                        file_matches = re.findall(r'(?:created?|wrote|saved?)\s+(?:file\s+)?([^\s]+\.(html|js|ts|css|json))', content, re.IGNORECASE)
                        for match in file_matches:
                            filename = match[0]
                            if filename not in files_created:
                                files_created.append(filename)
                
                elif message.get("type") == "result":
                    # Handle completion or error
                    if message.get("subtype") in ["error_max_turns", "error_during_execution"]:
                        raise Exception(f"Claude Code execution failed: {message.get('subtype')}")
            
            # Extract generated code from messages
            game_code = self._extract_game_code_from_messages(messages)
            
            return {
                "success": True,
                "game_code": game_code,
                "files_created": files_created,
                "messages": messages,
                "summary": self._generate_summary(prompt, game_code),
                "session_info": self._extract_session_info(messages)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "messages": messages if 'messages' in locals() else [],
                "files_created": files_created if 'files_created' in locals() else [],
                "summary": ""
            }
    
    @kernel_function(
        name="review_and_improve_code",
        description="Review and improve existing game code using Claude Code SDK"
    )
    async def review_and_improve_code(
        self,
        game_code: str,
        feedback: str,
        max_turns: int = 5
    ) -> Dict[str, Any]:
        """Review and improve existing game code"""
        
        if not CLAUDE_CODE_AVAILABLE:
            return await self._fallback_review(game_code, feedback)
        
        review_prompt = f"""Review and improve this Phaser 3 game code based on the feedback provided.

CURRENT GAME CODE:
```html
{game_code}
```

USER FEEDBACK: {feedback}

INSTRUCTIONS:
- Analyze the existing code and identify areas for improvement
- Apply the user feedback to enhance the game
- Maintain the existing game structure and mechanics
- Improve code quality, performance, and user experience
- Add any missing features or fix any bugs
- Ensure the game remains fully functional

Provide the improved version of the complete game."""

        try:
            messages = []
            
            async for message in query({
                "prompt": review_prompt,
                "options": {
                    "maxTurns": max_turns,
                    "cwd": self.working_directory,
                    "model": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                    "permissionMode": "bypassPermissions"
                }
            }):
                messages.append(message)
            
            improved_code = self._extract_game_code_from_messages(messages)
            
            return {
                "success": True,
                "improved_code": improved_code,
                "changes_summary": self._summarize_changes(game_code, improved_code),
                "messages": messages
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "improved_code": game_code,  # Return original on error
                "changes_summary": "Error occurred during review"
            }
    
    @kernel_function(
        name="get_claude_code_session_info",
        description="Get information about the last Claude Code session"
    )
    async def get_session_info(self, messages: List[Dict]) -> Dict[str, Any]:
        """Extract session information from Claude Code messages"""
        return self._extract_session_info(messages)
    
    def _extract_game_code_from_messages(self, messages: List[Dict]) -> str:
        """Extract HTML game code from Claude Code messages"""
        for message in reversed(messages):  # Start from the most recent
            if message.get("type") == "assistant":
                content = message.get("message", {}).get("content", "")
                if isinstance(content, str):
                    # Look for HTML code blocks
                    if "```html" in content:
                        start = content.find("```html") + 7
                        end = content.find("```", start)
                        if end > start:
                            return content[start:end].strip()
                    
                    # Look for DOCTYPE as fallback
                    if "<!DOCTYPE html>" in content:
                        start = content.find("<!DOCTYPE html>")
                        end = content.find("</html>", start)
                        if end > start:
                            return content[start:end + 7].strip()
        
        # If no HTML found, return the last assistant message
        for message in reversed(messages):
            if message.get("type") == "assistant":
                content = message.get("message", {}).get("content", "")
                if isinstance(content, str):
                    return content
        
        return ""
    
    def _generate_summary(self, prompt: str, game_code: str) -> str:
        """Generate a summary of the created game"""
        game_type = "game"
        if "platformer" in prompt.lower():
            game_type = "platformer game"
        elif "shooter" in prompt.lower():
            game_type = "shooter game"
        elif "puzzle" in prompt.lower():
            game_type = "puzzle game"
        elif "arcade" in prompt.lower():
            game_type = "arcade game"
        
        features = []
        if "physics" in game_code.lower():
            features.append("physics")
        if "keyboard" in game_code.lower():
            features.append("keyboard controls")
        if "score" in game_code.lower():
            features.append("scoring system")
        if "collision" in game_code.lower():
            features.append("collision detection")
        
        feature_text = ", ".join(features) if features else "basic gameplay"
        return f"Created a Phaser 3 {game_type} with {feature_text} using Claude Code SDK."
    
    def _extract_session_info(self, messages: List[Dict]) -> Dict[str, Any]:
        """Extract session information from messages"""
        result_message = next((m for m in messages if m.get("type") == "result"), None)
        if result_message:
            return {
                "session_id": result_message.get("session_id"),
                "duration": result_message.get("duration_ms"),
                "api_duration": result_message.get("duration_api_ms"),
                "total_cost": result_message.get("total_cost_usd"),
                "usage": result_message.get("usage"),
                "num_turns": result_message.get("num_turns")
            }
        return {}
    
    def _summarize_changes(self, original: str, improved: str) -> str:
        """Generate a summary of changes made during review"""
        if len(improved) > len(original):
            return "Enhanced the game with additional features and improvements"
        elif len(improved) < len(original):
            return "Optimized and streamlined the game code"
        else:
            return "Refined and improved the game implementation"
    
    async def _fallback_generation(self, prompt: str) -> Dict[str, Any]:
        """Fallback implementation when Claude Code SDK is not available"""
        return {
            "success": False,
            "error": "Claude Code SDK not available. Please install the Claude Code SDK Python package.",
            "game_code": "",
            "files_created": [],
            "messages": [],
            "summary": "Claude Code SDK integration required"
        }
    
    async def _fallback_review(self, game_code: str, feedback: str) -> Dict[str, Any]:
        """Fallback for code review when Claude Code SDK is not available"""
        return {
            "success": False,
            "error": "Claude Code SDK not available for code review.",
            "improved_code": game_code,
            "changes_summary": "Review requires Claude Code SDK"
        }