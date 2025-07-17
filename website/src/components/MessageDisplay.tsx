'use client'

import { SDKMessage } from "@anthropic-ai/claude-code"

interface MessageDisplayProps {
  messages: SDKMessage[]
  isGenerating: boolean
  error?: string | null
  buildResult?: {
    success: boolean
    filesCreated: string[]
    codeGenerated: Record<string, string>
    summary: string
  } | null
}

export function MessageDisplay({ messages, isGenerating, error, buildResult }: MessageDisplayProps) {
  if (messages.length === 0 && !isGenerating && !error) {
    return null
  }

  return (
    <div className="mt-8 space-y-4">
      {/* Messages Display */}
      <div className="p-4 max-h-96 overflow-y-auto">
          {/* Error Display */}
          {error && (
            <div className="mb-4">
              <div className="text-red-400 text-xs mb-2">[ERROR]</div>
              <div className="text-red-300 text-sm">{error}</div>
            </div>
          )}

          {/* Messages */}
          {messages.map((message, index) => (
            <div key={index} className="mb-4">
              {message.type === 'assistant' && 'message' in message && message.message?.content && (
                <div>
                  <div className="text-amber-400 text-xs mb-2">[ASSISTANT MESSAGE {index + 1}]</div>
                  <div className="terminal-text text-sm whitespace-pre-wrap">
                    {typeof message.message.content === 'string' 
                      ? message.message.content 
                      : JSON.stringify(message.message.content, null, 2)}
                  </div>
                </div>
              )}
              
              {message.type === 'result' && (
                <div>
                  <div className="text-cyan-400 text-xs mb-2">[RESULT]</div>
                  <div className="terminal-text text-sm">
                    {'result' in message && message.result && (
                      <div>{typeof message.result === 'string' ? message.result : JSON.stringify(message.result, null, 2)}</div>
                    )}
                  </div>
                </div>
              )}

              {message.type === 'user' && 'message' in message && message.message?.content && (
                <div>
                  <div className="text-green-400 text-xs mb-2">[USER INPUT]</div>
                  <div className="terminal-text text-sm">
                    {typeof message.message.content === 'string' 
                      ? message.message.content 
                      : JSON.stringify(message.message.content, null, 2)}
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Loading indicator */}
          {isGenerating && (
            <div className="flex items-center space-x-2">
              <div className="text-amber-400 text-xs">CLAUDE IS THINKING</div>
              <div className="flex space-x-1">
                <div className="w-1 h-1 bg-amber-400 rounded-full animate-pulse"></div>
                <div className="w-1 h-1 bg-amber-400 rounded-full animate-pulse delay-75"></div>
                <div className="w-1 h-1 bg-amber-400 rounded-full animate-pulse delay-150"></div>
              </div>
            </div>
          )}
        </div>

      {/* Build Results */}
      {buildResult && buildResult.success && (
        <div className="p-4 space-y-4">
            {/* Files Created */}
            {buildResult.filesCreated.length > 0 && (
              <div>
                <div className="text-amber-400 text-xs mb-2">[FILES CREATED]</div>
                <div className="space-y-1">
                  {buildResult.filesCreated.map((file, index) => (
                    <div key={index} className="text-cyan-400 text-sm">
                      <span className="text-green-400">+</span> {file}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Code Generated */}
            {Object.keys(buildResult.codeGenerated).length > 0 && (
              <div>
                <div className="text-amber-400 text-xs mb-2">[CODE GENERATED]</div>
                <div className="space-y-2">
                  {Object.entries(buildResult.codeGenerated).map(([filename, code], index) => (
                    <div key={index} className="border border-green-800 rounded">
                      <div className="bg-green-900 px-2 py-1 text-xs text-green-300">
                        {filename}
                      </div>
                      <div className="p-2 text-xs terminal-text overflow-x-auto">
                        <pre className="whitespace-pre-wrap">{code}</pre>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Summary */}
            {buildResult.summary && (
              <div>
                <div className="text-amber-400 text-xs mb-2">[SUMMARY]</div>
                <div className="terminal-text text-sm whitespace-pre-wrap">
                  {buildResult.summary}
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  )
}