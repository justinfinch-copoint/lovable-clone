from typing import Dict, Any
from semantic_kernel import Kernel
from semantic_kernel.contents import ChatHistory, ChatMessageContent, AuthorRole
import json


class GameDeveloperAgent:
    """Agent that acts as a game development project manager, delegating to Claude Code"""
    
    SYSTEM_MESSAGE = """You are a friendly game development project manager who helps users create Phaser 3 games.

Your role is to:
1. Understand what kind of game the user wants
2. Create detailed technical specifications for Claude Code
3. Delegate the actual coding to Claude Code (your development team)
4. Keep the user informed about progress in a friendly, conversational way
5. Handle any issues or requests for improvements

When a user asks for a game:
- First, chat with them to understand their vision
- Ask clarifying questions if needed (but don't overdo it - often you can infer details)
- Transform their request into detailed technical specifications
- Use the generate_game_code function to have Claude Code build it
- Present the results in an encouraging, friendly way

Keep your responses conversational and encouraging. You're helping them bring their game ideas to life!

Example interactions:
User: "Make me a space shooter"
You: "A space shooter sounds awesome! I'll create one with enemy waves, power-ups, and asteroid obstacles. Let me get Claude Code working on that for you..."

User: "I want a puzzle game"
You: "Great choice! I'll design a puzzle game for you. Would you prefer something like match-3, block-sliding, or word puzzles? Or should I surprise you with a creative puzzle mechanic?"

Remember: You're the friendly face, Claude Code is your expert developer."""
    
    def __init__(self, kernel: Kernel, service_id: str = "game_developer"):
        self.kernel = kernel
        self.service_id = service_id
        self.chat_history = ChatHistory()
        
        # Add system message to chat history
        system_message = ChatMessageContent(
            role=AuthorRole.SYSTEM,
            content=self.SYSTEM_MESSAGE
        )
        self.chat_history.add_message(system_message)
    
    async def generate_game(self, prompt: str) -> Dict[str, Any]:
        """Generate a Phaser 3 game based on the prompt using delegation pattern"""
        
        print("🎮 Game Developer PM: Analyzing your game request...")
        
        # Create a conversational message that will generate technical specs
        pm_prompt = f"""The user wants: "{prompt}"

Please:
1. First, acknowledge their request in a friendly way
2. Describe what kind of game you'll create based on their request
3. Use the generate_game_code function to create the game with detailed technical specifications

Transform their request into comprehensive technical requirements for the game, including:
- Core gameplay mechanics
- Player controls
- Game objectives
- Visual style (even if simple)
- Any special features that would make it fun

Remember to keep the user engaged with friendly progress updates!"""
        
        # Add user message to history
        user_message = ChatMessageContent(
            role=AuthorRole.USER,
            content=pm_prompt
        )
        self.chat_history.add_message(user_message)
        
        # Get response from kernel using chat completion
        try:
            chat_completion_service = self.kernel.get_service(self.service_id)
            result = await chat_completion_service.get_chat_message_contents(
                chat_history=self.chat_history,
                settings=chat_completion_service.get_prompt_execution_settings_class()(
                    function_choice_behavior="auto"
                ),
                kernel=self.kernel
            )
            
            if result:
                response = result[0]  # Get first response
                # Add response to history
                self.chat_history.add_message(response)
                
                # Parse the response to extract game details
                parsed_result = self._parse_agent_response(response)
                
                return {
                    "success": parsed_result.get("success", True),
                    "game_code": parsed_result.get("game_code", ""),
                    "filename": parsed_result.get("filename", "game.html"),
                    "summary": parsed_result.get("summary", str(response.content)),
                    "chat_history": self.chat_history,
                    "agent_response": str(response.content)
                }
            else:
                return {
                    "success": False,
                    "error": "No response from AI service",
                    "chat_history": self.chat_history
                }
        except Exception as e:
            print(f"❌ Error generating game: {e}")
            return {
                "success": False,
                "error": str(e),
                "chat_history": self.chat_history
            }
    
    async def review_game(self, game_code: str, feedback: str) -> Dict[str, Any]:
        """Review and improve existing game code using delegation"""
        
        review_prompt = f"""The user has feedback about their game: "{feedback}"

Please:
1. Acknowledge their feedback positively
2. Explain what improvements you'll make
3. Use the review_and_improve_game function to enhance the game
4. Present the improvements in an encouraging way

Current game code: {game_code[:500]}... (truncated)"""
        
        # Add user message to history
        user_message = ChatMessageContent(
            role=AuthorRole.USER,
            content=review_prompt
        )
        self.chat_history.add_message(user_message)
        
        # Get response from kernel using chat completion
        try:
            chat_completion_service = self.kernel.get_service(self.service_id)
            result = await chat_completion_service.get_chat_message_contents(
                chat_history=self.chat_history,
                settings=chat_completion_service.get_prompt_execution_settings_class()(
                    function_choice_behavior="auto"
                ),
                kernel=self.kernel
            )
            
            if result:
                response = result[0]  # Get first response
                # Add response to history
                self.chat_history.add_message(response)
                
                # Parse the response to extract game details
                parsed_result = self._parse_agent_response(response)
                
                return {
                    "success": parsed_result.get("success", True),
                    "improved_code": parsed_result.get("improved_code", game_code),
                    "changes_summary": parsed_result.get("changes_summary", str(response.content)),
                    "agent_response": str(response.content)
                }
            else:
                return {
                    "success": False,
                    "error": "No response from AI service"
                }
        except Exception as e:
            print(f"❌ Error reviewing game: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_agent_response(self, response) -> Dict[str, Any]:
        """Parse agent response to extract game code and metadata"""
        
        if hasattr(response, 'content'):
            content = str(response.content)
        else:
            content = str(response)
        
        # Try to extract structured data if the agent included it
        result = {
            "success": True,
            "summary": content
        }
        
        # Look for code blocks
        if "```html" in content:
            start = content.find("```html") + 7
            end = content.find("```", start)
            if end > start:
                result["game_code"] = content[start:end].strip()
                result["filename"] = "game.html"
        
        # Look for JSON results (in case the agent returns structured data)
        if "{" in content and "}" in content:
            try:
                # Find the last JSON object in the response
                json_start = content.rfind("{")
                json_end = content.rfind("}") + 1
                if json_start < json_end:
                    json_str = content[json_start:json_end]
                    json_data = json.loads(json_str)
                    if isinstance(json_data, dict):
                        result.update(json_data)
            except:
                pass  # If JSON parsing fails, continue with basic result
        
        return result
    
    def _enhance_prompt_for_claude(self, user_prompt: str) -> str:
        """Transform user's simple prompt into detailed technical specifications"""
        
        # This method helps create comprehensive specs from simple requests
        base_specs = """
Create a complete Phaser 3 game with these specifications:

Technical Requirements:
- Single HTML file with embedded JavaScript and CSS
- Use Phaser 3 CDN (latest stable version)
- Responsive design that works on desktop and mobile
- Proper game states (menu, play, game over)
- Score system and UI elements
- Sound effects preparation (even if muted by default)

"""
        
        # Analyze the user prompt and add specific requirements
        prompt_lower = user_prompt.lower()
        
        if "platformer" in prompt_lower:
            base_specs += """
Platformer Specific Requirements:
- Gravity-based physics
- Jump mechanics with variable height
- Moving platforms
- Collectible items
- Enemy AI with patrol patterns
- Multiple levels or scrolling world
"""
        elif "shooter" in prompt_lower:
            if "space" in prompt_lower:
                base_specs += """
Space Shooter Specific Requirements:
- Player spaceship with smooth controls
- Projectile system with pooling
- Enemy waves with different patterns
- Power-ups (rapid fire, shields, multi-shot)
- Parallax star background
- Boss enemy after certain score
"""
            else:
                base_specs += """
Shooter Specific Requirements:
- Aiming system (mouse or touch)
- Projectile physics
- Enemy spawning system
- Reload mechanics
- Health/ammo display
- Different weapon types
"""
        elif "puzzle" in prompt_lower:
            base_specs += """
Puzzle Game Specific Requirements:
- Grid-based or physics-based mechanics
- Clear objective and rules
- Progressive difficulty
- Hint system
- Move counter or timer
- Satisfying feedback for correct moves
"""
        elif "racing" in prompt_lower:
            base_specs += """
Racing Game Specific Requirements:
- Vehicle physics with acceleration/deceleration
- Track boundaries and collision
- Lap timing system
- AI opponents
- Speed boost zones
- Mini-map or position indicator
"""
        else:
            # Generic game requirements
            base_specs += """
Game Specific Requirements:
- Clear objective and win condition
- Intuitive controls
- Progressive difficulty
- Visual and audio feedback
- Engaging gameplay loop
- Replayability factor
"""
        
        return base_specs + f"\nUser's specific request: {user_prompt}"