# Gameable

A powerful Phaser game development terminal built with Next.js and Claude SDK, designed for rapid game prototyping and creation.

## Features

- 🎮 Phaser 3 game development terminal interface
- 🚀 Rapid game prototyping with AI assistance
- 🎯 Game-specific code generation prompts
- ⚡ Fast, responsive retro terminal UI
- 🤖 Powered by Claude SDK for intelligent game creation

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Claude SDK** - AI-powered code generation
- **Phaser 3** - Target framework for game development

## Design Features

- Retro CRT terminal aesthetic
- Green/amber color scheme
- Monospace typography (JetBrains Mono, IBM Plex Mono)
- Scanline and flicker effects
- Blinking cursor animations
- Terminal window styling

## Project Structure

```
src/
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
└── components/
    ├── Hero.tsx
    └── CodeInput.tsx
```

## Next Steps

- Integrate with Claude Code SDK for Phaser game generation
- Add game preview and testing capabilities
- Implement asset management for sprites and sounds
- Add physics configuration options
- Create game export functionality
- Add multiplayer game templates