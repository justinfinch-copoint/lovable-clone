'use client'

import { useState, useEffect } from 'react'
import { CodeInput } from './CodeInput'
import { MessageDisplay } from './MessageDisplay'
import { SDKMessage } from '@anthropic-ai/claude-code'

interface BuildResult {
  success: boolean
  messages: SDKMessage[]
  filesCreated: string[]
  codeGenerated: Record<string, string>
  summary: string
  error?: string
}

export function Hero() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [bootSequence, setBootSequence] = useState(0)
  const [messages, setMessages] = useState<SDKMessage[]>([])
  const [buildResult, setBuildResult] = useState<BuildResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      if (bootSequence < 3) {
        setBootSequence(bootSequence + 1)
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [bootSequence])

  const handleGenerate = async (prompt: string) => {
    setIsGenerating(true)
    setError(null)
    setMessages([])
    setBuildResult(null)
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to generate code')
      }

      const result: BuildResult = await response.json()
      
      if (result.success) {
        setMessages(result.messages)
        setBuildResult(result)
      } else {
        setError(result.error || 'Generation failed')
      }
    } catch (error) {
      console.error('Error generating code:', error)
      setError(error instanceof Error ? error.message : 'Unknown error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="min-h-screen">
      {/* Terminal Body */}
      <div className="p-6 sm:p-8 lg:p-12 min-h-screen">
              {/* Boot Sequence */}
              <div className="mb-8 text-xs sm:text-sm terminal-text opacity-70">
                {bootSequence >= 1 && <div>INITIALIZING SYSTEM...</div>}
                {bootSequence >= 2 && <div>LOADING AI MODULES...</div>}
                {bootSequence >= 3 && <div>SYSTEM READY. TYPE 'HELP' FOR COMMANDS.</div>}
              </div>

              {/* ASCII Art Logo */}
              <div className="mb-8">
                <pre className="ascii-art text-xs sm:text-sm">
{`
  ____    __    __  __  ____    __    ____  __    ____ 
 (  _ \\  /__\  (  \/  )( ___)  /__\  (  _ \\(  )  ( ___)
  )(_) )/(__)\\ )    (  )__)  /(__)\\ ) _ ( )(____) )__) 
 (____/(__)(__)(_/\\_)(____)(__)(__)(_____)(____)(____)
                                                       
           G A M E A B L E   v1.0.0                   
`}
                </pre>
              </div>

              {/* Code Input */}
              <div className="mb-8">
                <CodeInput 
                  onGenerate={handleGenerate} 
                  isLoading={isGenerating}
                />
              </div>

              {/* Message Display */}
              <MessageDisplay 
                messages={messages}
                isGenerating={isGenerating}
                error={error}
                buildResult={buildResult}
              />

              {/* System Status */}
              <div className="mt-12 text-xs opacity-50">
                <div>CPU: 98.2% | MEM: 16.7GB | UPTIME: 99.99%</div>
              </div>
      </div>
    </div>
  )
}