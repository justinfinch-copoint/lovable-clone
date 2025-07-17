import { NextRequest, NextResponse } from 'next/server'
import { buildWithClaude } from '../../../lib/buildWithClaude'

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json()
    
    if (!prompt || typeof prompt !== 'string') {
      return NextResponse.json(
        { error: 'Prompt is required and must be a string' },
        { status: 400 }
      )
    }

    // Enhance the prompt to ensure Phaser 3 game development
    const enhancedPrompt = `Create a Phaser 3 game: ${prompt}

SPECIFIC REQUIREMENTS:
- Build a complete HTML5 game using Phaser 3 framework
- Include proper game structure with scenes, physics, and input handling
- Make the game playable with clear objectives and win/lose conditions
- Ensure responsive design that works on desktop and mobile
- Add basic UI elements like score display and game over screen
- Use appropriate Phaser features for the game type (physics, sprites, animations)
- Include comments explaining the game mechanics

Save the complete game as an HTML file that can be opened directly in a browser.`

    // Call the buildWithClaude function with enhanced prompt
    const result = await buildWithClaude(enhancedPrompt)

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