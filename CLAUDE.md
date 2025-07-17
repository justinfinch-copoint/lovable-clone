## Project Ideas

- I am building a lovable clone for generating phaser games using Chainlit React integration with Python agents

## Development Notes

- The project now uses Chainlit React for the UI instead of separate Claude Code SDK calls
- Run `npm run dev:full` to start both the website and agent services together
- Website runs on port 3000, Chainlit agent on port 8000, FastAPI on port 8001

## Architecture

- **Frontend**: Next.js with Chainlit React client integration
- **Backend**: Python agents service with Semantic Kernel and Chainlit
- **Game Generation**: Conversational interface through Chainlit chat

## Git Workflow

- Dont include claude code as an author when making git commits
