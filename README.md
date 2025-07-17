# Claude Code SDK Integration

This project demonstrates how to integrate the Claude Code SDK to power code generation features in a lovable clone.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file by copying `.env.example`:
```bash
cp .env.example .env
```

3. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Basic Code Generation

```typescript
import { buildWithClaude } from "./buildWithClaude.js";

const result = await buildWithClaude("Create a tic-tac-toe game in HTML");

if (result.success) {
  console.log("Files created:", result.filesCreated);
  console.log("Summary:", result.summary);
}
```

### Running the Test

```bash
npm test
```

This will attempt to generate a tic-tac-toe game using the Claude Code SDK.

## How It Works

The `buildWithClaude` function:
1. Takes a prompt as input
2. Uses the Claude Code SDK to generate code
3. Allows Claude to automatically create and edit files
4. Returns information about created files and operations

## Configuration

The SDK is configured with:
- `maxTurns: 10` - Allows multi-step operations
- `permissionMode: "bypassPermissions"` - Auto-approves file operations
- Custom system prompt for code generation focus

## Notes

- Make sure Claude Code CLI is installed globally (`npm install -g @anthropic-ai/claude-code`)
- The SDK spawns a Claude Code subprocess, so it requires proper authentication
- File operations are performed in the current working directory