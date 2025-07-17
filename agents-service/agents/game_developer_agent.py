from typing import Dict, List, Optional, Any
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
import os


class GameDeveloperAgent:
    """Agent specialized in Phaser 3 game development"""
    
    AGENT_NAME = "GameDeveloper"
    AGENT_INSTRUCTIONS = """You are a Phaser 3 game development specialist. Your role is to create complete, functional HTML5 games using the Phaser 3 framework.

CORE REQUIREMENTS:
- Always use Phaser 3 framework (latest stable version)
- Create complete, runnable HTML files with embedded JavaScript
- Include proper DOCTYPE and meta tags for responsive design
- Use Phaser CDN link: https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js

GAME STRUCTURE:
- Implement proper Phaser scene structure with preload(), create(), and update() methods
- Use scene management for complex games (Boot, Preload, Game, GameOver scenes)
- Include proper game configuration with canvas setup
- Make games responsive and work on different screen sizes
- Set up proper game dimensions and scaling

TECHNICAL FEATURES TO INCLUDE:
- Physics system (Arcade Physics for most games)
- Player input handling (keyboard, mouse, touch as appropriate)
- Sprite management and animations
- Collision detection and response
- Asset loading and management
- Basic game states (start, play, pause, game over)
- Sound effects and music loading (even if not implemented)
- Score tracking and display
- Basic UI elements (buttons, text, HUD)

GAME TYPES GUIDANCE:
- Platformer: Include gravity, jumping, collision with platforms, moving enemies
- Shooter: Projectile management, enemy spawning, collision detection, health system
- Puzzle: Grid-based systems, match detection, turn-based or real-time logic
- Arcade: Simple physics, increasing difficulty, power-ups, high score system

CODE QUALITY:
- Use modern JavaScript (ES6+) syntax
- Include comments explaining game logic
- Organize code into logical sections
- Handle errors gracefully
- Use Phaser's built-in methods and properties
- Follow Phaser best practices for performance

DELIVERABLES:
- Complete HTML file with embedded CSS and JavaScript
- Fully functional game that runs in a browser
- Proper asset loading structure (even if using simple colored rectangles)
- Basic game loop with win/lose conditions
- Responsive design that works on desktop and mobile

When asked to create a game, always provide a complete, playable implementation."""
    
    def __init__(self, kernel: Kernel, service_id: str = "game_developer", use_claude_code: bool = True):
        self.kernel = kernel
        self.service_id = service_id
        self.use_claude_code = use_claude_code
        self.agent = self._create_agent()
        self.chat_history = ChatHistory()
        
        # Try to get Claude Code bridge plugin from kernel
        self.claude_code_bridge = None
        if use_claude_code:
            try:
                # Look for the Claude Code bridge plugin
                for plugin_name, plugin in kernel.plugins.items():
                    if hasattr(plugin, 'generate_game_with_claude_code'):
                        self.claude_code_bridge = plugin
                        break
            except Exception as e:
                print(f"⚠️ Claude Code bridge not available: {e}")
                self.use_claude_code = False
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the game developer agent"""
        try:
            # Try new API first
            return ChatCompletionAgent(
                kernel=self.kernel,
                name=self.AGENT_NAME,
                instructions=self.AGENT_INSTRUCTIONS,
                service_id=self.service_id
            )
        except Exception as e:
            print(f"⚠️ Trying fallback ChatCompletionAgent creation: {e}")
            # Fallback for different API
            return ChatCompletionAgent(
                kernel=self.kernel,
                name=self.AGENT_NAME,
                instructions=self.AGENT_INSTRUCTIONS
            )
    
    async def generate_game(self, prompt: str) -> Dict[str, Any]:
        """Generate a Phaser 3 game based on the prompt"""
        
        # Try to use Claude Code SDK first if available
        if self.use_claude_code and self.claude_code_bridge:
            try:
                print("🚀 Using Claude Code SDK for game generation...")
                result = await self.claude_code_bridge.generate_game_with_claude_code(prompt)
                
                if result.get("success"):
                    print("✅ Claude Code SDK generation successful")
                    return {
                        "success": True,
                        "game_code": result.get("game_code", ""),
                        "filename": result.get("filename", "game.html"),
                        "summary": result.get("summary", "Game generated with Claude Code SDK"),
                        "files_created": result.get("files_created", []),
                        "messages": result.get("messages", [])
                    }
                else:
                    print(f"⚠️ Claude Code SDK failed: {result.get('error')}, falling back to Semantic Kernel")
            except Exception as e:
                print(f"⚠️ Claude Code SDK error: {e}, falling back to Semantic Kernel")
        
        # Fallback to Semantic Kernel agent generation
        print("🔄 Using Semantic Kernel agent for game generation...")
        
        # Enhanced prompt for game generation
        enhanced_prompt = f"""Create a Phaser 3 game based on this request: {prompt}

Please provide:
1. A complete HTML file with embedded JavaScript and CSS
2. The game should be fully functional and playable
3. Include proper comments explaining the game logic
4. Make sure the game has clear objectives and is fun to play

Generate the complete game code now."""
        
        # Add user message to history
        self.chat_history.add_user_message(enhanced_prompt)
        
        # Get response from agent
        response = await self.agent.invoke(self.chat_history)
        
        # Add response to history
        self.chat_history.add_message(response)
        
        # Extract game code from response
        game_code = self._extract_game_code(str(response.content))
        
        return {
            "success": True,
            "game_code": game_code,
            "filename": "game.html",
            "summary": self._generate_summary(prompt, game_code),
            "chat_history": self.chat_history
        }
    
    def _extract_game_code(self, response: str) -> str:
        """Extract HTML game code from the response"""
        # Look for HTML code blocks
        if "```html" in response:
            start = response.find("```html") + 7
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        
        # Look for <!DOCTYPE html> as a fallback
        if "<!DOCTYPE html>" in response:
            start = response.find("<!DOCTYPE html>")
            # Find the closing </html> tag
            end = response.find("</html>", start)
            if end > start:
                return response[start:end + 7].strip()
        
        # If no HTML found, return the full response
        return response
    
    def _generate_summary(self, prompt: str, game_code: str) -> str:
        """Generate a summary of the created game"""
        # Simple analysis of the game code
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
        if "gameover" in game_code.lower():
            features.append("game over state")
        
        feature_text = ", ".join(features) if features else "basic gameplay"
        
        return f"Created a Phaser 3 {game_type} with {feature_text}. The game is ready to play!"
    
    async def review_game(self, game_code: str, feedback: str) -> Dict[str, Any]:
        """Review and improve existing game code"""
        review_prompt = f"""Review and improve this Phaser 3 game code based on the feedback:

Current game code:
```html
{game_code}
```

Feedback: {feedback}

Please provide an improved version of the game that addresses the feedback."""
        
        self.chat_history.add_user_message(review_prompt)
        response = await self.agent.invoke(self.chat_history)
        self.chat_history.add_message(response)
        
        improved_code = self._extract_game_code(str(response.content))
        
        return {
            "success": True,
            "improved_code": improved_code,
            "changes_summary": self._summarize_changes(game_code, improved_code)
        }
    
    def _summarize_changes(self, original: str, improved: str) -> str:
        """Generate a summary of changes made"""
        # This is a simple implementation
        # In a real system, you might use diff tools or more sophisticated analysis
        if len(improved) > len(original):
            return "Enhanced the game with additional features and improvements"
        else:
            return "Optimized and refined the game code"