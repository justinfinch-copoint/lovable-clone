/**
 * Local type definitions for agent responses
 * Replaces @anthropic-ai/claude-code types since we're using Python agents
 */

export interface AgentMessage {
  type: 'assistant' | 'user' | 'system';
  message: {
    content: string;
  };
}

export interface BuildResult {
  success: boolean;
  messages: AgentMessage[];
  filesCreated: string[];
  codeGenerated: Record<string, string>;
  summary: string;
  error?: string;
}