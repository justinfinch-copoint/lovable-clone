import os
import json
import aiofiles
from typing import Dict, List, Optional
from datetime import datetime
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments


class FileOperationsPlugin:
    """Plugin for file operations in the game development process"""
    
    def __init__(self, output_dir: str = "./generated_games"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    @kernel_function(
        name="save_game_file",
        description="Save a game file to the file system"
    )
    async def save_game_file(
        self,
        filename: str,
        content: str,
        project_name: Optional[str] = None
    ) -> Dict[str, str]:
        """Save a game file to the file system"""
        # Create project directory if specified
        if project_name:
            project_dir = os.path.join(self.output_dir, project_name)
            os.makedirs(project_dir, exist_ok=True)
            file_path = os.path.join(project_dir, filename)
        else:
            file_path = os.path.join(self.output_dir, filename)
        
        # Save the file
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        return {
            "status": "success",
            "file_path": file_path,
            "filename": filename,
            "size": len(content),
            "timestamp": datetime.now().isoformat()
        }
    
    @kernel_function(
        name="read_game_file",
        description="Read a game file from the file system"
    )
    async def read_game_file(
        self,
        filename: str,
        project_name: Optional[str] = None
    ) -> Dict[str, str]:
        """Read a game file from the file system"""
        if project_name:
            file_path = os.path.join(self.output_dir, project_name, filename)
        else:
            file_path = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "error": f"File not found: {file_path}"
            }
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        return {
            "status": "success",
            "content": content,
            "file_path": file_path,
            "filename": filename
        }
    
    @kernel_function(
        name="list_project_files",
        description="List all files in a project directory"
    )
    async def list_project_files(
        self,
        project_name: Optional[str] = None
    ) -> Dict[str, any]:
        """List all files in a project directory"""
        if project_name:
            search_dir = os.path.join(self.output_dir, project_name)
        else:
            search_dir = self.output_dir
        
        if not os.path.exists(search_dir):
            return {
                "status": "error",
                "error": f"Directory not found: {search_dir}"
            }
        
        files = []
        for root, dirs, filenames in os.walk(search_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, search_dir)
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "path": rel_path,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return {
            "status": "success",
            "directory": search_dir,
            "files": files,
            "count": len(files)
        }
    
    @kernel_function(
        name="create_project_structure",
        description="Create a project directory structure for a game"
    )
    async def create_project_structure(
        self,
        project_name: str,
        include_assets: bool = True
    ) -> Dict[str, any]:
        """Create a project directory structure for a game"""
        project_dir = os.path.join(self.output_dir, project_name)
        
        # Create directory structure
        directories = [
            project_dir,
            os.path.join(project_dir, "js"),
            os.path.join(project_dir, "css"),
        ]
        
        if include_assets:
            directories.extend([
                os.path.join(project_dir, "assets"),
                os.path.join(project_dir, "assets", "images"),
                os.path.join(project_dir, "assets", "sounds"),
                os.path.join(project_dir, "assets", "sprites"),
            ])
        
        created_dirs = []
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            created_dirs.append(directory)
        
        # Create a project info file
        project_info = {
            "name": project_name,
            "created": datetime.now().isoformat(),
            "structure": created_dirs,
            "type": "phaser3-game"
        }
        
        info_path = os.path.join(project_dir, "project.json")
        async with aiofiles.open(info_path, 'w') as f:
            await f.write(json.dumps(project_info, indent=2))
        
        return {
            "status": "success",
            "project_dir": project_dir,
            "created_directories": created_dirs,
            "project_info": project_info
        }
    
    @kernel_function(
        name="delete_file",
        description="Delete a file from the file system"
    )
    async def delete_file(
        self,
        filename: str,
        project_name: Optional[str] = None
    ) -> Dict[str, str]:
        """Delete a file from the file system"""
        if project_name:
            file_path = os.path.join(self.output_dir, project_name, filename)
        else:
            file_path = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "error": f"File not found: {file_path}"
            }
        
        try:
            os.remove(file_path)
            return {
                "status": "success",
                "message": f"File deleted: {file_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    @kernel_function(
        name="get_file_metadata",
        description="Get metadata about a file"
    )
    async def get_file_metadata(
        self,
        filename: str,
        project_name: Optional[str] = None
    ) -> Dict[str, any]:
        """Get metadata about a file"""
        if project_name:
            file_path = os.path.join(self.output_dir, project_name, filename)
        else:
            file_path = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "error": f"File not found: {file_path}"
            }
        
        stat = os.stat(file_path)
        
        # Determine file type
        file_ext = os.path.splitext(filename)[1].lower()
        file_type = {
            ".html": "HTML",
            ".js": "JavaScript",
            ".css": "CSS",
            ".json": "JSON",
            ".png": "Image",
            ".jpg": "Image",
            ".jpeg": "Image",
            ".gif": "Image",
            ".mp3": "Audio",
            ".wav": "Audio",
            ".ogg": "Audio"
        }.get(file_ext, "Unknown")
        
        return {
            "status": "success",
            "filename": filename,
            "path": file_path,
            "size": stat.st_size,
            "size_readable": self._format_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "type": file_type,
            "extension": file_ext
        }
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"