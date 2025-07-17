'use client'

import { useState, useEffect } from 'react'
import { CodeInput } from './CodeInput'

export function Hero() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [bootSequence, setBootSequence] = useState(0)

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
    try {
      // TODO: Integrate with buildWithClaude function
      console.log('Generating code for:', prompt)
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
    } catch (error) {
      console.error('Error generating code:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="min-h-screen relative">
      {/* Terminal Container */}
      <div className="min-h-screen p-4 sm:p-6 lg:p-8">
        <div className="max-w-6xl mx-auto">
          {/* Terminal Window */}
          <div className="terminal-window shadow-2xl">
            {/* Terminal Header */}
            <div className="terminal-header flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <div className="text-xs">GAMEABLE v1.0.0</div>
              <div className="text-xs">[SYSTEM READY]</div>
            </div>

            {/* Terminal Body */}
            <div className="p-6 sm:p-8 lg:p-12 min-h-[calc(100vh-8rem)]">
              {/* Boot Sequence */}
              <div className="mb-8 text-xs sm:text-sm terminal-text opacity-70">
                {bootSequence >= 1 && <div>INITIALIZING SYSTEM...</div>}
                {bootSequence >= 2 && <div>LOADING AI MODULES...</div>}
                {bootSequence >= 3 && <div>SYSTEM READY. TYPE 'HELP' FOR COMMANDS.</div>}
              </div>

              {/* ASCII Art Logo */}
              <div className="mb-8 text-center">
                <pre className="ascii-art text-xs sm:text-sm inline-block">
{`
  ____    __    __  __  ____    __    ____  __    ____ 
 (  _ \\  /__\  (  \/  )( ___)  /__\  (  _ \\(  )  ( ___)
  )(_) )/(__)\\ )    (  )__)  /(__)\\ ) _ ( )(____) )__) 
 (____/(__)(__)(_/\\_)(____)(__)(__)(_____)(____)(____)
                                                       
           G A M E A B L E   v1.0.0                   
`}
                </pre>
              </div>

              {/* Main Content */}
              <div className="text-center mb-12">
                <div className="mb-6">
                  <div className="terminal-prompt text-lg sm:text-xl mb-2">
                    SYSTEM INITIALIZED
                  </div>
                  <div className="text-amber-400 text-sm sm:text-base mb-4">
                    PHASER GAME DEVELOPMENT TERMINAL
                  </div>
                </div>

                <div className="max-w-2xl mx-auto mb-8">
                  <p className="terminal-text text-sm sm:text-base leading-relaxed mb-4">
                    ENTER YOUR GAME DESCRIPTION TO GENERATE PHASER CODE.
                  </p>
                  <p className="terminal-text text-xs sm:text-sm opacity-70">
                    POWERED BY PHASER 3 | JAVASCRIPT | TYPESCRIPT | HTML5 CANVAS
                  </p>
                </div>

                {/* Code Input */}
                <div className="mb-12">
                  <CodeInput 
                    onGenerate={handleGenerate} 
                    isLoading={isGenerating}
                  />
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                  <div className="terminal-window">
                    <div className="p-4">
                      <div className="flex items-center mb-2">
                        <span className="text-amber-400 mr-2">[FEATURE]</span>
                        <span className="text-xs opacity-70">001</span>
                      </div>
                      <h3 className="terminal-text font-bold mb-2">RAPID PROTOTYPING</h3>
                      <p className="text-xs opacity-70">
                        GENERATE PLAYABLE GAMES IN SECONDS
                      </p>
                    </div>
                  </div>

                  <div className="terminal-window">
                    <div className="p-4">
                      <div className="flex items-center mb-2">
                        <span className="text-amber-400 mr-2">[FEATURE]</span>
                        <span className="text-xs opacity-70">002</span>
                      </div>
                      <h3 className="terminal-text font-bold mb-2">PHASER OPTIMIZED</h3>
                      <p className="text-xs opacity-70">
                        BUILT FOR PHASER 3 GAME DEVELOPMENT
                      </p>
                    </div>
                  </div>

                  <div className="terminal-window">
                    <div className="p-4">
                      <div className="flex items-center mb-2">
                        <span className="text-amber-400 mr-2">[FEATURE]</span>
                        <span className="text-xs opacity-70">003</span>
                      </div>
                      <h3 className="terminal-text font-bold mb-2">GAME READY</h3>
                      <p className="text-xs opacity-70">
                        COMPLETE GAMES WITH PHYSICS & ASSETS
                      </p>
                    </div>
                  </div>
                </div>

                {/* System Status */}
                <div className="mt-12 text-xs opacity-50 text-center">
                  <div>CPU: 98.2% | MEM: 16.7GB | UPTIME: 99.99%</div>
                  <div className="mt-1">
                    <span className="cursor"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}