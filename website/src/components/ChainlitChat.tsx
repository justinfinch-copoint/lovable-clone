'use client'

import { useEffect, useState } from 'react'
import { RecoilRoot } from 'recoil'
import { useChatSession, useChatMessages, useChatInteract } from '@chainlit/react-client'

interface ChainlitChatProps {
  onGameGenerated?: (gameCode: string, filename: string) => void
}

function ChainlitChatInner({ onGameGenerated }: ChainlitChatProps) {
  const [isConnected, setIsConnected] = useState(false)
  const { connect, disconnect, session } = useChatSession()
  const { messages } = useChatMessages()
  const { sendMessage } = useChatInteract()

  useEffect(() => {
    const connectToChainlit = async () => {
      try {
        await connect({
          chainlitServer: 'http://localhost:8000',
          userEnv: {},
          // Optional: Add authentication if needed
          // accessToken: 'Bearer YOUR_TOKEN'
        })
        setIsConnected(true)
      } catch (error) {
        console.error('Failed to connect to Chainlit:', error)
        setIsConnected(false)
      }
    }

    connectToChainlit()

    return () => {
      disconnect()
      setIsConnected(false)
    }
  }, [connect, disconnect])

  // Extract game code from messages when a game is generated
  useEffect(() => {
    const latestMessage = messages[messages.length - 1]
    if (latestMessage && latestMessage.elements) {
      const codeElement = latestMessage.elements.find(
        (element: any) => element.type === 'text' && element.language === 'html'
      )
      if (codeElement && onGameGenerated) {
        onGameGenerated(codeElement.content, codeElement.name || 'game.html')
      }
    }
  }, [messages, onGameGenerated])

  const handleSendMessage = async (text: string) => {
    if (!isConnected || !text.trim()) return
    
    try {
      await sendMessage({
        content: text,
        type: 'user_message'
      })
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  if (!isConnected) {
    return (
      <div className="flex items-center justify-center p-8 text-green-400">
        <div className="animate-pulse">
          Connecting to Game Developer Agent...
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-black border border-green-500 rounded">
      {/* Messages Display */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={message.id || index}
            className={`flex ${
              message.type === 'user_message' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.type === 'user_message'
                  ? 'bg-green-900 text-green-100'
                  : 'bg-gray-900 text-green-400 border border-green-700'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {/* Render code elements */}
              {message.elements?.map((element: any, idx: number) => (
                <div key={idx} className="mt-2">
                  {element.type === 'text' && element.language === 'html' && (
                    <div className="bg-gray-800 p-3 rounded border border-green-600">
                      <div className="text-xs text-green-300 mb-2">
                        📄 {element.name}
                      </div>
                      <pre className="text-xs text-green-200 overflow-x-auto">
                        {element.content.substring(0, 200)}...
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="border-t border-green-500 p-4">
        <MessageInput onSendMessage={handleSendMessage} />
      </div>
    </div>
  )
}

interface MessageInputProps {
  onSendMessage: (message: string) => void
}

function MessageInput({ onSendMessage }: MessageInputProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      onSendMessage(message)
      setMessage('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Describe the game you want to create..."
        className="flex-1 bg-black border border-green-500 rounded px-3 py-2 text-green-400 placeholder-green-600 focus:outline-none focus:border-green-400"
      />
      <button
        type="submit"
        className="bg-green-900 hover:bg-green-800 text-green-100 px-4 py-2 rounded border border-green-500 transition-colors"
      >
        Generate
      </button>
    </form>
  )
}

export function ChainlitChat({ onGameGenerated }: ChainlitChatProps) {
  return (
    <RecoilRoot>
      <ChainlitChatInner onGameGenerated={onGameGenerated} />
    </RecoilRoot>
  )
}