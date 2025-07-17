import { NextRequest, NextResponse } from 'next/server'
import { buildWithAgent } from '../../../lib/agentClient'

// LEGACY: This route is no longer used since we migrated to Chainlit React
// Game generation now happens directly through Chainlit WebSocket connection
// Keeping this for backwards compatibility or alternative API access

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json()
    
    if (!prompt || typeof prompt !== 'string') {
      return NextResponse.json(
        { error: 'Prompt is required and must be a string' },
        { status: 400 }
      )
    }

    // Call the buildWithAgent function with raw prompt
    // Python agents already have comprehensive Phaser 3 system prompts
    const result = await buildWithAgent(prompt)

    return NextResponse.json(result)
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        details: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    )
  }
}

// Handle unsupported methods
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405 }
  )
}