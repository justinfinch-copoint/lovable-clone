# Phaser Game Generator - Agents Service

A Semantic Kernel-based agent system for generating Phaser 3 games with Chainlit UI and FastAPI backend.

## Features

- **Semantic Kernel Agents**: Specialized AI agents for game development
- **Chainlit UI**: Rich conversational interface for game generation
- **FastAPI Backend**: REST API for integration with external applications
- **Plugin System**: Extensible tools for file operations and Phaser development
- **Multi-Agent Architecture**: Collaborative agents for complex game development

## Architecture

```
agents-service/
├── app.py                 # Chainlit application
├── api_server.py          # FastAPI server
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── agents/               # AI agents
│   ├── game_developer_agent.py
│   ├── code_reviewer_agent.py
│   └── orchestrator_agent.py
├── plugins/              # Semantic Kernel plugins
│   ├── file_operations.py
│   ├── phaser_tools.py
│   ├── code_generation.py
│   └── project_management.py
└── generated_games/      # Output directory for games
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Required Environment Variables**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: (Optional) Your Anthropic API key
   - `DEFAULT_MODEL`: AI model to use (default: gpt-4o-mini)
   - `OUTPUT_DIR`: Directory for generated games (default: ./generated_games)

## Usage

### Chainlit UI (Recommended)

Run the conversational interface:
```bash
chainlit run app.py -w
```

Access the UI at: http://localhost:8000

### FastAPI Server

Run the API server:
```bash
python api_server.py
```

Access the API at: http://localhost:8001
API docs at: http://localhost:8001/docs

### Both Services

Run both services simultaneously:
```bash
# Terminal 1
chainlit run app.py -w

# Terminal 2
python api_server.py
```

## API Endpoints

### Game Generation
- `POST /api/generate` - Generate a new game
- `POST /api/review` - Review and improve existing game code

### Templates
- `GET /api/templates/{game_type}` - Get game template

### Project Management
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{project_name}/files` - List project files
- `GET /api/projects/{project_name}/files/{filename}` - Get specific file

### Health Check
- `GET /health` - Service health status

## Game Types Supported

- **Basic**: Simple movement and interaction
- **Platformer**: Physics-based jumping and platform collision
- **Shooter**: Projectile mechanics and enemy systems
- **Puzzle**: Grid-based logic and match detection
- **Arcade**: Fast-paced action with scoring

## Example Usage

### Chainlit UI
1. Open http://localhost:8000
2. Type: "Create a platformer game with jumping mechanics"
3. The agent will generate a complete Phaser 3 game
4. Copy the HTML code and save as a file to play

### API Request
```bash
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a space shooter game with asteroids",
    "project_name": "space_shooter",
    "game_type": "shooter"
  }'
```

## Development

### Adding New Agents
1. Create agent class in `agents/` directory
2. Import and register in `app.py` and `api_server.py`

### Adding New Plugins
1. Create plugin class in `plugins/` directory
2. Add `@kernel_function` decorators to methods
3. Register plugin in kernel initialization

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## Integration with Website

The FastAPI server provides endpoints that can be used by your existing Next.js application:

1. Update your `buildWithClaude.ts` to call the API service
2. Replace the current implementation with HTTP requests to the agent service
3. Handle streaming responses for better user experience

## Deployment

### Docker (Recommended)
```bash
# Build image
docker build -t phaser-game-generator .

# Run container
docker run -p 8000:8000 -p 8001:8001 --env-file .env phaser-game-generator
```

### Manual Deployment
1. Set up Python environment on server
2. Install dependencies
3. Configure environment variables
4. Run services with process manager (PM2, systemd)

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `OPENAI_API_KEY` is set in `.env`
   - Verify the key is valid and has sufficient credits

2. **Import Errors**
   - Check Python version (3.8+ required)
   - Verify all dependencies are installed

3. **Port Conflicts**
   - Change ports in `.env` file
   - Check if ports are already in use

4. **Agent Not Responding**
   - Check model availability
   - Verify API key permissions
   - Review logs for error messages

## License

MIT License - see LICENSE file for details