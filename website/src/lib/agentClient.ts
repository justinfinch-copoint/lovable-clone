/**
 * Client for interacting with the Semantic Kernel agents service
 */

import { BuildResult } from '../types/agent';

export interface AgentGameRequest {
  prompt: string;
  project_name?: string;
  game_type?: 'basic' | 'platformer' | 'shooter' | 'puzzle' | 'arcade';
}

export interface AgentGameResponse {
  success: boolean;
  game_code?: string;
  filename?: string;
  summary?: string;
  project_name?: string;
  error?: string;
  session_id?: string;
}

export interface AgentReviewRequest {
  game_code: string;
  feedback: string;
}

export interface AgentReviewResponse {
  success: boolean;
  improved_code?: string;
  changes_summary?: string;
  error?: string;
}

export interface AgentHealthResponse {
  status: string;
  version: string;
  features: {
    game_generation: boolean;
    file_operations: boolean;
    phaser_tools: boolean;
  };
}

export class AgentClient {
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl: string = 'http://localhost:8001', timeout: number = 60000) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }

  /**
   * Generate a new Phaser 3 game
   */
  async generateGame(request: AgentGameRequest, abortSignal?: AbortSignal): Promise<AgentGameResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: abortSignal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return {
          success: false,
          error: 'Request was aborted'
        };
      }
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Review and improve existing game code
   */
  async reviewGame(request: AgentReviewRequest, abortSignal?: AbortSignal): Promise<AgentReviewResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: abortSignal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return {
          success: false,
          error: 'Request was aborted'
        };
      }
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Get a game template
   */
  async getTemplate(gameType: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/templates/${gameType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Failed to get template');
    }
  }

  /**
   * Check service health
   */
  async healthCheck(): Promise<AgentHealthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Health check failed');
    }
  }

  /**
   * List all projects
   */
  async listProjects(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/projects`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Failed to list projects');
    }
  }

  /**
   * Create a new project
   */
  async createProject(projectName: string, includeAssets: boolean = true): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_name: projectName,
          include_assets: includeAssets
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Failed to create project');
    }
  }

  /**
   * Get project files
   */
  async getProjectFiles(projectName: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/projects/${projectName}/files`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Failed to get project files');
    }
  }

  /**
   * Get a specific file from a project
   */
  async getProjectFile(projectName: string, filename: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/projects/${projectName}/files/${filename}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Failed to get project file');
    }
  }
}

// Default client instance
export const agentClient = new AgentClient();


/**
 * Legacy compatibility function that wraps the agent client
 * to match the original buildWithClaude interface
 */
export async function buildWithAgent(
  prompt: string,
  abortSignal?: AbortSignal
): Promise<BuildResult> {
  try {
    const response = await agentClient.generateGame({
      prompt,
      game_type: 'basic'
    }, abortSignal);

    if (response.success && response.game_code) {
      return {
        success: true,
        messages: [
          {
            type: 'assistant',
            message: {
              content: response.summary || 'Game generated successfully'
            }
          }
        ],
        filesCreated: [response.filename || 'game.html'],
        codeGenerated: {
          [response.filename || 'game.html']: response.game_code
        },
        summary: response.summary || 'Game generated successfully'
      };
    } else {
      return {
        success: false,
        error: response.error || 'Failed to generate game',
        messages: [],
        filesCreated: [],
        codeGenerated: {},
        summary: ''
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      messages: [],
      filesCreated: [],
      codeGenerated: {},
      summary: ''
    };
  }
}