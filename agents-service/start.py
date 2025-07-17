#!/usr/bin/env python3
"""
Startup script for the Phaser Game Generator agents service.
This script can run both Chainlit UI and FastAPI server.
"""

import os
import sys
import subprocess
import threading
import signal
from pathlib import Path

def run_chainlit():
    """Run the Chainlit application"""
    print("🚀 Starting Chainlit UI...")
    try:
        subprocess.run([
            sys.executable, "-m", "chainlit", "run", "app.py", "-w",
            "--port", os.getenv("CHAINLIT_PORT", "8000")
        ])
    except KeyboardInterrupt:
        print("⛔ Chainlit UI stopped")

def run_fastapi():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        subprocess.run([sys.executable, "api_server.py"])
    except KeyboardInterrupt:
        print("⛔ FastAPI server stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n⛔ Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    # Parse command line arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    if mode == "chainlit":
        run_chainlit()
    elif mode == "fastapi":
        run_fastapi()
    elif mode == "both":
        print("🚀 Starting both Chainlit UI and FastAPI server...")
        print("📱 Chainlit UI will be available at: http://localhost:8000")
        print("🔌 FastAPI server will be available at: http://localhost:8001")
        print("📚 API docs will be available at: http://localhost:8001/docs")
        print("\nPress Ctrl+C to stop both services\n")
        
        # Start both services in separate threads
        chainlit_thread = threading.Thread(target=run_chainlit, daemon=True)
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        
        chainlit_thread.start()
        fastapi_thread.start()
        
        try:
            # Wait for both threads
            chainlit_thread.join()
            fastapi_thread.join()
        except KeyboardInterrupt:
            print("\n⛔ Shutting down services...")
            sys.exit(0)
    else:
        print("Usage: python start.py [chainlit|fastapi|both]")
        print("  chainlit - Run only Chainlit UI")
        print("  fastapi  - Run only FastAPI server")
        print("  both     - Run both services (default)")
        sys.exit(1)

if __name__ == "__main__":
    main()