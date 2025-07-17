import os
import chainlit as cl
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

# Load environment variables
load_dotenv()

# Import our agents and plugins
from agents.game_developer_agent import GameDeveloperAgent
from plugins.file_operations import FileOperationsPlugin
from plugins.phaser_tools import PhaserToolsPlugin
# Claude Code bridge removed - using Semantic Kernel agent only

# Configure Chainlit for React integration
# Note: Configuration is now handled via config.toml and environment variables


@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    try:
        # Clear any existing session data first
        cl.user_session.clear()
        
        # Create a welcome message with the app's capabilities
        welcome_message = """👋 Welcome to the **Phaser Game Generator**!

I'm an AI agent specialized in creating Phaser 3 games. I can help you:

🎮 **Create Various Game Types:**
- Platformers with physics and collision detection
- Shooter games with projectiles and enemies
- Puzzle games with grid-based mechanics
- Arcade games with scoring systems

🛠️ **Features I Can Include:**
- Player controls (keyboard, mouse, touch)
- Physics systems
- Animations and sprites
- Sound effects and music
- Score tracking and UI
- Multiple game scenes

💡 **How to Get Started:**
Simply describe the game you want to create! For example:
- "Create a space shooter game with asteroids"
- "Build a platformer with jumping mechanics"
- "Make a puzzle game like Tetris"

What kind of game would you like me to create today?"""
        
        await cl.Message(content=welcome_message).send()
        
        # Initialize the kernel and store in session
        kernel = Kernel()
        
        # Add OpenAI service if API key is available
        if os.getenv("OPENAI_API_KEY"):
            service_id = "game_developer"
            kernel.add_service(
                OpenAIChatCompletion(
                    service_id=service_id,
                    ai_model_id=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
                )
            )
            
            # Add plugins to kernel
            file_ops_plugin = FileOperationsPlugin(output_dir=os.getenv("OUTPUT_DIR", "./generated_games"))
            phaser_tools_plugin = PhaserToolsPlugin()
            
            kernel.add_plugin(file_ops_plugin, plugin_name="FileOperations")
            kernel.add_plugin(phaser_tools_plugin, plugin_name="PhaserTools")
            
            # Create game developer agent
            game_agent = GameDeveloperAgent(kernel, service_id)
            
            cl.user_session.set("kernel", kernel)
            cl.user_session.set("service_id", service_id)
            cl.user_session.set("game_agent", game_agent)
        else:
            await cl.Message(
                content="⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in your .env file."
            ).send()
        
        # Initialize chat history
        chat_history = ChatHistory()
        cl.user_session.set("chat_history", chat_history)
        
    except Exception as e:
        print(f"Error during session initialization: {e}")
        await cl.Message(
            content=f"❌ Error initializing session: {str(e)}"
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    try:
        game_agent = cl.user_session.get("game_agent")
        
        if not game_agent:
            await cl.Message(
                content="❌ Session not properly initialized. Please refresh the page."
            ).send()
            return
        
        # Send initial status message
        status_msg = await cl.Message(content="🤔 Planning your game development...").send()
        
        # Generate the game using our agent
        result = await game_agent.generate_game(message.content)
        
        if result["success"]:
            # Show the generated game code
            await cl.Message(
                content=f"🎮 **Game Created!**\n\n{result['summary']}",
                elements=[
                    cl.Text(
                        name=result["filename"],
                        content=result["game_code"],
                        display="inline",
                        language="html"
                    )
                ]
            ).send()
            
            await cl.Message(
                content="🚀 **Your game is ready!** Copy the code above and save it as an HTML file to play your game."
            ).send()
            
        else:
            await cl.Message(
                content="❌ Sorry, I couldn't generate the game. Please try again with a different request."
            ).send()
            
    except Exception as e:
        print(f"Error in message handler: {e}")
        await cl.Message(
            content=f"❌ An error occurred while generating the game: {str(e)}"
        ).send()


@cl.on_stop
def on_stop():
    """Handle stop button click"""
    print("The user clicked the stop button!")


@cl.on_chat_end
def on_chat_end():
    """Handle chat session end"""
    print("The chat session has ended")
    # Clean up session data
    try:
        game_agent = cl.user_session.get("game_agent")
        if game_agent:
            # Perform any necessary cleanup
            pass
        # Clear individual session items instead of calling clear()
        session_keys = ["kernel", "service_id", "game_agent", "chat_history"]
        for key in session_keys:
            try:
                cl.user_session.remove(key)
            except (KeyError, AttributeError):
                pass
    except Exception as e:
        print(f"Error during session cleanup: {e}")


if __name__ == "__main__":
    # This allows running the app directly with Python
    # Usually you would run with: chainlit run app.py -w
    cl.run()