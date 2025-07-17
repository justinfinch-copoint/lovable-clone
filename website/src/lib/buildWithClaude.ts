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
        customSystemPrompt: "You are a code generator. Create the requested code and save it to appropriate files. Focus on creating clean, working code.",
        
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