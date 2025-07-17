'use client'

import { useState, useRef, useEffect } from 'react'

interface CodeInputProps {
  onGenerate: (prompt: string) => Promise<void>
  isLoading: boolean
}

export function CodeInput({ onGenerate, isLoading }: CodeInputProps) {
  const [prompt, setPrompt] = useState('')
  const [history, setHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [cursorPosition, setCursorPosition] = useState({ line: 0, column: 0 })
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    const updateCursorPosition = () => {
      if (inputRef.current) {
        const { selectionStart } = inputRef.current
        const textBeforeCursor = prompt.substring(0, selectionStart)
        const lines = textBeforeCursor.split('\n')
        const currentLine = lines.length - 1
        const currentColumn = lines[lines.length - 1].length
        setCursorPosition({ line: currentLine, column: currentColumn })
      }
    }
    updateCursorPosition()
  }, [prompt])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim() || isLoading) return
    
    setHistory([...history, prompt.trim()])
    setHistoryIndex(-1)
    await onGenerate(prompt.trim())
    setPrompt('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    } else if (e.key === 'ArrowUp' && e.ctrlKey) {
      e.preventDefault()
      if (historyIndex < history.length - 1) {
        const newIndex = historyIndex + 1
        setHistoryIndex(newIndex)
        setPrompt(history[history.length - 1 - newIndex])
      }
    } else if (e.key === 'ArrowDown' && e.ctrlKey) {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setPrompt(history[history.length - 1 - newIndex])
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setPrompt('')
      }
    }
  }

  const commands = [
    { cmd: "generate", desc: "CREATE A NEW APPLICATION" },
    { cmd: "help", desc: "SHOW AVAILABLE COMMANDS" },
    { cmd: "clear", desc: "CLEAR TERMINAL HISTORY" },
    { cmd: "examples", desc: "SHOW EXAMPLE PROMPTS" }
  ]

  return (
    <div className="w-full">
      {/* Terminal Input */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="terminal-window">
          <div className="p-4">
            <div className="flex items-start">
              <span className="terminal-prompt mr-2 mt-1">root@lovable</span>
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onKeyUp={() => {
                    if (inputRef.current) {
                      const { selectionStart } = inputRef.current
                      const textBeforeCursor = prompt.substring(0, selectionStart)
                      const lines = textBeforeCursor.split('\n')
                      const currentLine = lines.length - 1
                      const currentColumn = lines[lines.length - 1].length
                      setCursorPosition({ line: currentLine, column: currentColumn })
                    }
                  }}
                  onClick={() => {
                    if (inputRef.current) {
                      const { selectionStart } = inputRef.current
                      const textBeforeCursor = prompt.substring(0, selectionStart)
                      const lines = textBeforeCursor.split('\n')
                      const currentLine = lines.length - 1
                      const currentColumn = lines[lines.length - 1].length
                      setCursorPosition({ line: currentLine, column: currentColumn })
                    }
                  }}
                  placeholder="ENTER COMMAND OR PROJECT DESCRIPTION..."
                  className="w-full bg-transparent outline-none resize-none terminal-text placeholder-green-700 min-h-[120px] pr-4"
                  style={{ 
                    lineHeight: '1.5',
                    scrollbarWidth: 'thin',
                    scrollbarColor: 'rgb(var(--term-green-dim)) transparent'
                  }}
                  disabled={isLoading}
                  rows={5}
                />
                {!isLoading && <span className="cursor absolute" style={{ 
                  top: `${cursorPosition.line * 1.5}em`,
                  left: `${cursorPosition.column * 0.6}ch`,
                  height: '1.2em'
                }}></span>}
              </div>
            </div>
            
            {/* Status Line */}
            <div className="mt-2 text-xs opacity-50 flex justify-between">
              <span>[{prompt.length}/2000 CHARS]</span>
              <span>CTRL+↑/↓ FOR HISTORY | ENTER TO EXECUTE</span>
            </div>
          </div>
        </div>
      </form>

      {/* Commands List */}
      <div className="mt-6 terminal-window">
        <div className="p-4">
          <div className="text-amber-400 text-xs mb-3">[AVAILABLE COMMANDS]</div>
          <div className="space-y-1">
            {commands.map((cmd, index) => (
              <div key={index} className="text-xs">
                <span className="text-cyan-400">{cmd.cmd.padEnd(12)}</span>
                <span className="opacity-70">- {cmd.desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Example Prompts */}
      <div className="mt-6 terminal-window">
        <div className="p-4">
          <div className="text-amber-400 text-xs mb-3">[QUICK EXAMPLES]</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {[
              "TODO APP WITH REACT AND LOCAL STORAGE",
              "LANDING PAGE FOR SAAS PRODUCT",
              "TIC-TAC-TOE GAME IN VANILLA JS",
              "CONTACT FORM WITH EMAIL VALIDATION"
            ].map((example, index) => (
              <button
                key={index}
                onClick={() => setPrompt(example)}
                disabled={isLoading}
                className="text-left text-xs p-2 border border-green-800 hover:border-green-400 hover:bg-green-950 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="text-amber-400 mr-2">[{(index + 1).toString().padStart(2, '0')}]</span>
                <span className="terminal-text text-xs">{example}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="mt-6 terminal-window">
          <div className="p-4">
            <div className="text-amber-400 text-xs mb-2">[PROCESSING]</div>
            <div className="flex items-center space-x-2">
              <div className="text-xs terminal-text">GENERATING CODE</div>
              <span className="animate-pulse">...</span>
            </div>
            <div className="mt-2 text-xs opacity-50">
              AI MODULES ACTIVE | ANALYZING REQUEST | ETA: CALCULATING
            </div>
          </div>
        </div>
      )}
    </div>
  )
}