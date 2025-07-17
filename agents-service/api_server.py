import os
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import uvicorn

# Load environment variables
load_dotenv()

# Import our agents and plugins
from agents.game_developer_agent import GameDeveloperAgent
from plugins.file_operations import FileOperationsPlugin
from plugins.phaser_tools import PhaserToolsPlugin
from plugins.claude_code_bridge import ClaudeCodeBridge

# Initialize FastAPI app
app = FastAPI(
    title="Phaser Game Generator API",
    description="Semantic Kernel-based API for generating Phaser 3 games",
    version="1.0.0"
)

# Add CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class GameGenerationRequest(BaseModel):
    prompt: str = Field(..., description="The game description prompt")
    project_name: Optional[str] = Field(None, description="Optional project name")
    game_type: Optional[str] = Field("basic", description="Type of game (basic, platformer, shooter, puzzle, arcade)")

class GameGenerationResponse(BaseModel):
    success: bool
    game_code: Optional[str] = None
    filename: Optional[str] = None
    summary: Optional[str] = None
    project_name: Optional[str] = None
    error: Optional[str] = None
    session_id: Optional[str] = None

class GameReviewRequest(BaseModel):
    game_code: str = Field(..., description="The game code to review")
    feedback: str = Field(..., description="Feedback for improvement")

class GameReviewResponse(BaseModel):
    success: bool
    improved_code: Optional[str] = None
    changes_summary: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    features: Dict[str, bool]

# Global kernel and agent instances
kernel: Optional[Kernel] = None
game_agent: Optional[GameDeveloperAgent] = None
file_ops_plugin: Optional[FileOperationsPlugin] = None
phaser_tools_plugin: Optional[PhaserToolsPlugin] = None
claude_code_bridge: Optional[ClaudeCodeBridge] = None

def initialize_services():
    """Initialize Semantic Kernel and agents"""
    global kernel, game_agent, file_ops_plugin, phaser_tools_plugin, claude_code_bridge
    
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found in environment variables")
    
    # Initialize kernel
    kernel = Kernel()
    
    # Add OpenAI service
    service_id = "game_developer"
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
        )
    )
    
    # Initialize plugins
    file_ops_plugin = FileOperationsPlugin(output_dir=os.getenv("OUTPUT_DIR", "./generated_games"))
    phaser_tools_plugin = PhaserToolsPlugin()
    claude_code_bridge = ClaudeCodeBridge()
    
    # Add plugins to kernel
    kernel.add_plugin(file_ops_plugin, plugin_name="FileOperations")
    kernel.add_plugin(phaser_tools_plugin, plugin_name="PhaserTools")
    kernel.add_plugin(claude_code_bridge, plugin_name="ClaudeCode")
    
    # Initialize game developer agent
    game_agent = GameDeveloperAgent(kernel, service_id)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        initialize_services()
        print(" Semantic Kernel services initialized successfully")
    except Exception as e:
        print(f"L Failed to initialize services: {e}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if kernel and game_agent else "unhealthy",
        version="1.0.0",
        features={
            "game_generation": kernel is not None and game_agent is not None,
            "file_operations": file_ops_plugin is not None,
            "phaser_tools": phaser_tools_plugin is not None,
            "claude_code_sdk": claude_code_bridge is not None,
        }
    )

@app.post("/api/generate", response_model=GameGenerationResponse)
async def generate_game(request: GameGenerationRequest):
    """Generate a Phaser 3 game based on the prompt"""
    if not game_agent:
        raise HTTPException(status_code=503, detail="Game generation service not available")
    
    try:
        # Generate the game
        result = await game_agent.generate_game(request.prompt)
        
        if result["success"]:
            # Save the game file if project name is provided
            if request.project_name and file_ops_plugin:
                await file_ops_plugin.save_game_file(
                    filename=result["filename"],
                    content=result["game_code"],
                    project_name=request.project_name
                )
            
            return GameGenerationResponse(
                success=True,
                game_code=result["game_code"],
                filename=result["filename"],
                summary=result["summary"],
                project_name=request.project_name,
                session_id=f"session_{asyncio.current_task().get_name() if asyncio.current_task() else 'unknown'}"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate game")
            
    except Exception as e:
        return GameGenerationResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/review", response_model=GameReviewResponse)
async def review_game(request: GameReviewRequest):
    """Review and improve existing game code"""
    if not game_agent:
        raise HTTPException(status_code=503, detail="Game review service not available")
    
    try:
        result = await game_agent.review_game(request.game_code, request.feedback)
        
        if result["success"]:
            return GameReviewResponse(
                success=True,
                improved_code=result["improved_code"],
                changes_summary=result["changes_summary"]
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to review game")
            
    except Exception as e:
        return GameReviewResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/templates/{game_type}")
async def get_game_template(game_type: str):
    """Get a Phaser 3 game template"""
    if not phaser_tools_plugin:
        raise HTTPException(status_code=503, detail="Phaser tools service not available")
    
    try:
        result = await phaser_tools_plugin.get_game_template(game_type)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def list_projects():
    """List all game projects"""
    if not file_ops_plugin:
        raise HTTPException(status_code=503, detail="File operations service not available")
    
    try:
        result = await file_ops_plugin.list_project_files()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_name}/files")
async def list_project_files(project_name: str):
    """List files in a specific project"""
    if not file_ops_plugin:
        raise HTTPException(status_code=503, detail="File operations service not available")
    
    try:
        result = await file_ops_plugin.list_project_files(project_name)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_name}/files/{filename}")
async def get_project_file(project_name: str, filename: str):
    """Get a specific file from a project"""
    if not file_ops_plugin:
        raise HTTPException(status_code=503, detail="File operations service not available")
    
    try:
        result = await file_ops_plugin.read_game_file(filename, project_name)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects")
async def create_project(request: dict):
    """Create a new game project structure"""
    if not file_ops_plugin:
        raise HTTPException(status_code=503, detail="File operations service not available")
    
    project_name = request.get("project_name")
    if not project_name:
        raise HTTPException(status_code=400, detail="project_name is required")
    
    try:
        result = await file_ops_plugin.create_project_structure(
            project_name=project_name,
            include_assets=request.get("include_assets", True)
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

def run_server():
    """Run the FastAPI server"""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()