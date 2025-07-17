import { buildWithClaude, getSessionInfo } from "./buildWithClaude.js";
import { type SDKMessage } from "@anthropic-ai/claude-code";

// Helper to format messages for debugging
function formatMessage(message: SDKMessage, index: number): string {
  const divider = "─".repeat(80);
  let output = `\n${divider}\nMessage ${index + 1} [${message.type.toUpperCase()}]:\n${divider}\n`;
  
  switch (message.type) {
    case "user":
      if ('message' in message && message.message) {
        output += `👤 User: ${message.message.content || '(no content)'}`;
      }
      break;
      
    case "assistant":
      if ('message' in message && message.message) {
        const content = message.message.content;
        if (typeof content === 'string') {
          // Truncate very long messages but show enough to understand
          const maxLength = 1000;
          if (content.length > maxLength) {
            output += `🤖 Assistant: ${content.substring(0, maxLength)}...\n[Message truncated - ${content.length} total characters]`;
          } else {
            output += `🤖 Assistant: ${content}`;
          }
          
          // Show tool uses if any
          if (message.message.tool_calls && message.message.tool_calls.length > 0) {
            output += `\n\n🔧 Tool Calls:`;
            message.message.tool_calls.forEach((toolCall: any) => {
              output += `\n  - ${toolCall.type}: ${JSON.stringify(toolCall.function || toolCall.id)}`;
            });
          }
        }
      }
      break;
      
    case "system":
      output += `⚙️  System: ${JSON.stringify(message)}`;
      break;
      
    case "result":
      if ('subtype' in message) {
        output += `📊 Result (${message.subtype}):`;
        if ('result' in message && message.result) {
          output += `\n  Result: ${message.result}`;
        }
        if ('duration_ms' in message) {
          output += `\n  Duration: ${message.duration_ms}ms`;
        }
        if ('total_cost_usd' in message) {
          output += `\n  Cost: $${message.total_cost_usd}`;
        }
        if ('is_error' in message && message.is_error) {
          output += `\n  ⚠️  Error occurred during execution`;
        }
      }
      break;
      
    default:
      output += `❓ Unknown message type: ${JSON.stringify(message)}`;
  }
  
  return output;
}

async function testTicTacToe() {
  console.log("🚀 Testing Claude Code SDK integration...");
  console.log("📝 Prompt: Create a complete tic-tac-toe game in a single HTML file\n");
  
  const prompt = `Create a complete tic-tac-toe game in a single HTML file called tic-tac-toe.html. 
The game should:
- Have a 3x3 grid
- Allow two players to take turns (X and O)
- Detect win conditions
- Show whose turn it is
- Have a reset button
- Use inline CSS for styling
- Use inline JavaScript for game logic
Make it colorful and fun!`;

  // Create abort controller for timeout
  const abortController = new AbortController();
  const timeout = setTimeout(() => abortController.abort(), 60000); // 60 second timeout

  try {
    const result = await buildWithClaude(prompt, abortController.signal);
    clearTimeout(timeout);
    
    console.log("\n🔍 Debug Info:");
    console.log(`Total messages: ${result.messages.length}`);
    console.log(`Success: ${result.success}`);
    if (result.error) {
      console.log(`Error: ${result.error}`);
    }
    
    // Get session info
    const sessionInfo = getSessionInfo(result.messages);
    if (sessionInfo) {
      console.log(`\n📊 Session Stats:`);
      console.log(`Session ID: ${sessionInfo.sessionId}`);
      console.log(`Duration: ${sessionInfo.duration}ms`);
      console.log(`API Duration: ${sessionInfo.apiDuration}ms`);
      console.log(`Total Cost: $${sessionInfo.totalCost?.toFixed(4) || '0.0000'}`);
      console.log(`Turns: ${sessionInfo.numTurns}`);
    }
    
    // Log message types
    const messageTypes = result.messages.reduce((acc, msg) => {
      acc[msg.type] = (acc[msg.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    console.log(`\nMessage types:`, messageTypes);
    
    // Show detailed conversation flow
    console.log("\n\n💬 CONVERSATION FLOW:");
    console.log("=" + "=".repeat(79));
    result.messages.forEach((msg, i) => {
      console.log(formatMessage(msg, i));
    });
    console.log("=" + "=".repeat(79));
    
    if (result.success) {
      console.log("\n✅ Code generation successful!");
      console.log("\n📁 Files created:");
      result.filesCreated.forEach(file => console.log(`   - ${file}`));
      
      console.log("\n📋 Summary:");
      console.log(result.summary);
      
      console.log("\n💡 You can now open the created files to see the result!");
    } else {
      console.error("\n❌ Code generation failed:", result.error);
    }
  } catch (error) {
    clearTimeout(timeout);
    console.error("❌ Unexpected error:", error);
  }
}

// Run the test
testTicTacToe();