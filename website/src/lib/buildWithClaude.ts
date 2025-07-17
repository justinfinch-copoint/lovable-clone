import { query, type SDKMessage } from "@anthropic-ai/claude-code";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

interface BuildResult {
  success: boolean;
  messages: SDKMessage[];
  filesCreated: string[];
  codeGenerated: Record<string, string>;
  summary: string;
  error?: string;
}

/**
 * Simple function that takes a prompt and builds code using Claude Code SDK
 * @param prompt - The code generation prompt (e.g., "Build a React todo app")
 * @param abortSignal - Optional AbortSignal to cancel the request
 * @returns Promise with the generated code and any file operations performed
 */
export async function buildWithClaude(
  prompt: string,
  abortSignal?: AbortSignal
): Promise<BuildResult> {
  // Ensure API key is set
  if (!process.env.ANTHROPIC_API_KEY) {
    return {
      success: false,
      error: "ANTHROPIC_API_KEY not found in environment variables. Please set it in your .env file.",
      messages: [],
      filesCreated: [],
      codeGenerated: {},
      summary: ""
    };
  }

  // Create abort controller if not provided
  const abortController = abortSignal 
    ? new AbortController() 
    : new AbortController();
  
  if (abortSignal) {
    abortSignal.addEventListener('abort', () => abortController.abort());
  }

  // Collect all messages from the query
  const messages: SDKMessage[] = [];
  const filesCreated: string[] = [];
  const codeGenerated: Map<string, string> = new Map();
  
  try {
    // Stream messages from Claude Code using the latest SDK pattern
    for await (const message of query({
      prompt,
      abortController,
      options: {
        // Set max turns to allow multi-step operations
        maxTurns: 10,
        
        // Working directory
        cwd: process.cwd(),
        
        // JavaScript runtime (optional)
        executable: "node" as const,
        
        // Path to Claude Code executable (optional)
        pathToClaudeCodeExecutable: process.env.CLAUDE_CODE_PATH,
        
        // Model to use (optional - defaults to claude-3-5-sonnet-20241022)
        model: process.env.CLAUDE_MODEL,
        
        // System prompt to guide Claude's behavior
        customSystemPrompt: `You are a Phaser 3 game development specialist. Your role is to create complete, functional HTML5 games using the Phaser 3 framework.

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

Always create a complete, playable game that demonstrates the requested concept using Phaser 3 framework.`,
        
        // Permission mode to bypass confirmations
        permissionMode: "bypassPermissions" as const,
      }
    })) {
      messages.push(message);
      
      // Track different message types
      switch (message.type) {
        case "assistant":
          // Track assistant messages that might contain file operations info
          if ('message' in message && message.message?.content) {
            const content = message.message.content;
            if (typeof content === 'string') {
              // Simple heuristic to detect file creation
              const fileMatches = content.match(/(?:created?|wrote|saved?)\s+(?:file\s+)?([^\s]+\.(html|js|ts|css|json|md))/gi);
              if (fileMatches) {
                fileMatches.forEach(match => {
                  const filename = match.split(/\s+/).pop();
                  if (filename && !filesCreated.includes(filename)) {
                    filesCreated.push(filename);
                  }
                });
              }
            }
          }
          break;
          
        case "result":
          // Handle result messages which contain final status
          if ('subtype' in message) {
            if (message.subtype === 'error_max_turns' || message.subtype === 'error_during_execution') {
              throw new Error(`Claude Code execution failed: ${message.subtype}`);
            }
          }
          break;
      }
    }
    
    // Return results
    return {
      success: true,
      messages,
      filesCreated,
      codeGenerated: Object.fromEntries(codeGenerated),
      summary: extractSummary(messages)
    };
    
  } catch (error) {
    // Handle abort separately
    if (error instanceof Error && error.name === 'AbortError') {
      return {
        success: false,
        error: "Request was aborted",
        messages,
        filesCreated,
        codeGenerated: Object.fromEntries(codeGenerated),
        summary: extractSummary(messages)
      };
    }
    
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
      messages,
      filesCreated,
      codeGenerated: Object.fromEntries(codeGenerated),
      summary: ""
    };
  }
}

// Helper to extract summary from messages
function extractSummary(messages: SDKMessage[]): string {
  // Find the last assistant message for summary
  const assistantMessages = messages.filter(m => m.type === "assistant");
  if (assistantMessages.length > 0) {
    const lastMessage = assistantMessages[assistantMessages.length - 1];
    if ('message' in lastMessage && lastMessage.message?.content) {
      const content = lastMessage.message.content;
      if (typeof content === 'string') {
        return content.substring(0, 500); // Limit summary length
      }
    }
  }
  
  // Check for result message as fallback
  const resultMessage = messages.find(m => m.type === "result");
  if (resultMessage && 'result' in resultMessage && typeof resultMessage.result === 'string') {
    return resultMessage.result;
  }
  
  return "";
}

// Helper function to get session info from messages
export function getSessionInfo(messages: SDKMessage[]) {
  const resultMessage = messages.find(m => m.type === "result") as any;
  if (resultMessage) {
    return {
      sessionId: resultMessage.session_id,
      duration: resultMessage.duration_ms,
      apiDuration: resultMessage.duration_api_ms,
      totalCost: resultMessage.total_cost_usd,
      usage: resultMessage.usage,
      numTurns: resultMessage.num_turns
    };
  }
  return null;
}