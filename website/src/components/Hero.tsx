'use client'

import { useState, useEffect } from 'react'
import { ChainlitChat } from './ChainlitChat'

export function Hero() {
  const [bootSequence, setBootSequence] = useState(0)
  const [generatedGame, setGeneratedGame] = useState<{
    code: string
    filename: string
  } | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      if (bootSequence < 3) {
        setBootSequence(bootSequence + 1)
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [bootSequence])

  const handleGameGenerated = (gameCode: string, filename: string) => {
    setGeneratedGame({ code: gameCode, filename })
  }

  const downloadGame = () => {
    if (!generatedGame) return
    
    const blob = new Blob([generatedGame.code], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = generatedGame.filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen">
      {/* Terminal Header */}
      <div className="p-6 sm:p-8 lg:p-12">
        {/* Boot Sequence */}
        <div className="mb-8 text-xs sm:text-sm terminal-text opacity-70">
          {bootSequence >= 1 && <div>INITIALIZING SYSTEM...</div>}
          {bootSequence >= 2 && <div>LOADING AI MODULES...</div>}
          {bootSequence >= 3 && <div>SYSTEM READY. GAME DEVELOPER AGENT ONLINE.</div>}
        </div>

        {/* ASCII Art Logo */}
        <div className="mb-8">
          <pre className="ascii-art text-xs sm:text-sm">
{`
  ____    __    __  __  ____    __    ____  __    ____ 
 (  _ \\  /__\  (  \\/  )( ___)  /__\  (  _ \\(  )  ( ___)
  )(_) )/(__)\\ )    (  )__)  /(__)\\ ) _ ( )(____) )__) 
 (____/(__)(__)(_/\\_)(____)(__)(__)(_____)(____)(____)
                                                       
           G A M E A B L E   v2.0.0                   
`}
          </pre>
        </div>

        {/* Game Generation Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Chainlit Chat Interface */}
          <div className="h-96 lg:h-[600px]">
            <h3 className="text-green-400 mb-4 font-mono">🤖 AI Game Developer</h3>
            <ChainlitChat onGameGenerated={handleGameGenerated} />
          </div>

          {/* Generated Game Preview */}
          <div className="h-96 lg:h-[600px]">
            <h3 className="text-green-400 mb-4 font-mono">🎮 Generated Game</h3>
            {generatedGame ? (
              <div className="h-full bg-black border border-green-500 rounded p-4">
                <div className="flex justify-between items-center mb-4">
                  <span className="text-green-300 text-sm">📄 {generatedGame.filename}</span>
                  <button
                    onClick={downloadGame}
                    className="bg-green-900 hover:bg-green-800 text-green-100 px-3 py-1 rounded border border-green-500 text-sm transition-colors"
                  >
                    ⬇️ Download
                  </button>
                </div>
                
                {/* Game Preview - render the HTML in an iframe */}
                <iframe
                  srcDoc={generatedGame.code}
                  className="w-full h-[calc(100%-60px)] border border-green-600 rounded bg-white"
                  title="Generated Game Preview"
                  sandbox="allow-scripts"
                />
              </div>
            ) : (
              <div className="h-full bg-black border border-green-500 rounded flex items-center justify-center">
                <div className="text-green-600 text-center">
                  <div className="text-4xl mb-4">🎮</div>
                  <div>Your generated game will appear here</div>
                  <div className="text-sm mt-2">Start chatting with the AI to create a game!</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* System Status */}
        <div className="mt-8 text-xs terminal-text opacity-50 flex justify-between">
          <span>AGENTS: ONLINE | MEMORY: 89% | CPU: 45%</span>
          <span>CHAINLIT v2.0 | PHASER v3.70</span>
        </div>
      </div>
    </div>
  )
}