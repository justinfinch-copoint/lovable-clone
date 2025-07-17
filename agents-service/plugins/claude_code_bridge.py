import os
import json
import asyncio
import subprocess
from typing import Dict, List, Optional, Any
from semantic_kernel.functions import kernel_function
from pathlib import Path


class ClaudeCodeBridge:
    """Bridge plugin that calls the existing TypeScript Claude Code implementation"""
    
    def __init__(self, 
                 website_path: Optional[str] = None,
                 node_executable: str = "node"):
        # Default to the website directory in the same repo
        self.website_path = website_path or str(Path(__file__).parent.parent.parent / "website")
        self.node_executable = node_executable
        
        # Verify the website path exists
        if not os.path.exists(self.website_path):
            raise ValueError(f"Website path not found: {self.website_path}")
    
    @kernel_function(
        name="generate_game_with_claude_code",
        description="Generate a Phaser 3 game using the existing Claude Code TypeScript implementation"
    )
    async def generate_game_with_claude_code(
        self,
        prompt: str,
        max_turns: int = 10
    ) -> Dict[str, Any]:
        """Generate a game using the existing buildWithClaude TypeScript function"""
        
        try:
            # Create a Node.js script that calls the buildWithClaude function
            script_content = f"""
const {{ buildWithClaude }} = require('./src/lib/buildWithClaude.ts');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

async function generateGame() {{
    try {{
        const result = await buildWithClaude(`{self._escape_js_string(prompt)}`);
        console.log('RESULT_START');
        console.log(JSON.stringify(result, null, 2));
        console.log('RESULT_END');
    }} catch (error) {{
        console.log('ERROR_START');
        console.log(JSON.stringify({{
            success: false,
            error: error.message || String(error),
            messages: [],
            filesCreated: [],
            codeGenerated: {{}},
            summary: ''
        }}, null, 2));
        console.log('ERROR_END');
    }}
}}

generateGame();
"""
            
            # Write the script to a temporary file
            script_path = os.path.join(self.website_path, 'temp_claude_code_bridge.js')
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            try:
                # Execute the Node.js script
                process = await asyncio.create_subprocess_exec(
                    self.node_executable, script_path,
                    cwd=self.website_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                # Clean up the temporary script
                os.remove(script_path)
                
                if process.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Node.js execution failed: {stderr.decode()}",
                        "game_code": "",
                        "files_created": [],
                        "summary": ""
                    }
                
                # Parse the output
                output = stdout.decode()
                result = self._parse_node_output(output)
                
                # Transform the result to match our expected format
                if result.get("success"):
                    # Extract game code from codeGenerated
                    code_generated = result.get("codeGenerated", {})
                    game_code = ""
                    filename = "game.html"
                    
                    if code_generated:
                        # Get the first HTML file
                        for file, content in code_generated.items():
                            if file.endswith('.html'):
                                game_code = content
                                filename = file
                                break
                        
                        # If no HTML file, take the first file
                        if not game_code and code_generated:
                            filename, game_code = next(iter(code_generated.items()))
                    
                    return {
                        "success": True,
                        "game_code": game_code,
                        "filename": filename,
                        "files_created": result.get("filesCreated", []),
                        "summary": result.get("summary", "Game generated successfully using Claude Code SDK"),
                        "messages": result.get("messages", [])
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Unknown error from Claude Code"),
                        "game_code": "",
                        "files_created": [],
                        "summary": ""
                    }
                
            except Exception as e:
                # Clean up the script if it still exists
                if os.path.exists(script_path):
                    os.remove(script_path)
                raise e
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute Claude Code bridge: {str(e)}",
                "game_code": "",
                "files_created": [],
                "summary": ""
            }
    
    @kernel_function(
        name="check_claude_code_availability",
        description="Check if Claude Code SDK is available and properly configured"
    )
    async def check_claude_code_availability(self) -> Dict[str, Any]:
        """Check if the Claude Code bridge is working"""
        
        try:
            # Check if Node.js is available
            process = await asyncio.create_subprocess_exec(
                self.node_executable, '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "available": False,
                    "error": "Node.js not found or not working",
                    "node_version": None
                }
            
            node_version = stdout.decode().strip()
            
            # Check if the buildWithClaude file exists
            build_file = os.path.join(self.website_path, 'src', 'lib', 'buildWithClaude.ts')
            if not os.path.exists(build_file):
                return {
                    "available": False,
                    "error": f"buildWithClaude.ts not found at {build_file}",
                    "node_version": node_version
                }
            
            # Check if package.json exists
            package_json = os.path.join(self.website_path, 'package.json')
            if not os.path.exists(package_json):
                return {
                    "available": False,
                    "error": f"package.json not found at {package_json}",
                    "node_version": node_version
                }
            
            return {
                "available": True,
                "node_version": node_version,
                "website_path": self.website_path,
                "build_file": build_file
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "node_version": None
            }
    
    def _escape_js_string(self, s: str) -> str:
        """Escape a string for use in JavaScript"""
        return s.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
    
    def _parse_node_output(self, output: str) -> Dict[str, Any]:
        """Parse the output from the Node.js script"""
        try:
            # Look for the result between markers
            if 'RESULT_START' in output and 'RESULT_END' in output:
                start = output.find('RESULT_START') + len('RESULT_START')
                end = output.find('RESULT_END')
                json_str = output[start:end].strip()
                return json.loads(json_str)
            
            # Look for error between markers
            elif 'ERROR_START' in output and 'ERROR_END' in output:
                start = output.find('ERROR_START') + len('ERROR_START')
                end = output.find('ERROR_END')
                json_str = output[start:end].strip()
                return json.loads(json_str)
            
            else:
                # Try to parse the entire output as JSON
                return json.loads(output)
                
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"Failed to parse Node.js output: {output}",
                "messages": [],
                "filesCreated": [],
                "codeGenerated": {},
                "summary": ""
            }