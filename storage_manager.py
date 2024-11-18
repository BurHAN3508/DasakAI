import os
import json
from datetime import datetime
from github import Github
from pathlib import Path

class StorageManager:
    def __init__(self):
        """Initialize the storage manager with GitHub integration"""
        self.github = Github(os.getenv("GITHUB_TOKEN"))
        self.repo_name = "DasakAI"
        self.user = self.github.get_user()
        self._ensure_repository_exists()

    def _ensure_repository_exists(self):
        """Ensure the GitHub repository exists, create if it doesn't"""
        try:
            self.repo = self.user.get_repo(self.repo_name)
        except Exception:
            self.repo = self.user.create_repo(
                self.repo_name,
                description="DasakAI - Autonomous AI Agent with Advanced Learning Capabilities",
                private=False,
                has_wiki=True,
                has_issues=True,
                auto_init=True
            )
            # Create initial repository structure
            self._create_initial_structure()

    def _create_initial_structure(self):
        """Create initial repository structure with necessary directories"""
        directories = [
            "memory",
            "learning_data",
            "models",
            "configs"
        ]
        
        readme_content = """# DasakAI

An autonomous AI agent with advanced GitHub learning capabilities.

## Features

- Autonomous learning from GitHub repositories
- Memory persistence and backup
- Advanced GitHub integration
- Goal-oriented behavior
- Natural language interaction

## Directory Structure

- `/memory`: Agent's memory storage
- `/learning_data`: Accumulated learning data
- `/models`: Model configurations and weights
- `/configs`: Configuration files

## Environment Setup

1. Clone the repository
2. Create a `.env` file with required API keys:
   - `HUGGINGFACE_API_KEY`
   - `GITHUB_TOKEN`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the agent: `python main.py`

## License

MIT License
"""
        
        for directory in directories:
            self._create_file(f"{directory}/.gitkeep", "")
            
        self._create_file("README.md", readme_content)

    def _create_file(self, path: str, content: str):
        """Create a file in the GitHub repository"""
        try:
            self.repo.create_file(
                path=path,
                message=f"Initialize {path}",
                content=content
            )
        except Exception as e:
            print(f"Error creating {path}: {str(e)}")

    def save_memory_local(self, memory_data: dict, agent_name: str) -> str:
        """Save memory data locally"""
        memory_dir = Path("memory")
        memory_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"memory_{agent_name}_{timestamp}.json"
        filepath = memory_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"memories": memory_data}, f, indent=2, ensure_ascii=False)
            
        return str(filepath)

    def backup_to_github(self, local_file: str) -> dict:
        """Backup memory file to GitHub"""
        try:
            with open(local_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            github_path = f"memory/{os.path.basename(local_file)}"
            
            # Check if file exists
            try:
                file = self.repo.get_contents(github_path)
                self.repo.update_file(
                    path=github_path,
                    message=f"Update memory backup {datetime.now().isoformat()}",
                    content=content,
                    sha=file.sha
                )
            except Exception:
                self.repo.create_file(
                    path=github_path,
                    message=f"Create memory backup {datetime.now().isoformat()}",
                    content=content
                )
                
            return {
                "success": True,
                "message": f"Backed up to GitHub: {github_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"GitHub backup failed: {str(e)}"
            }

    def save_learning_data(self, data: dict, category: str) -> dict:
        """Save learning data to GitHub"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            github_path = f"learning_data/{category}_{timestamp}.json"
            
            content = json.dumps(data, indent=2, ensure_ascii=False)
            
            self.repo.create_file(
                path=github_path,
                message=f"Add learning data for {category}",
                content=content
            )
            
            return {
                "success": True,
                "message": f"Saved learning data: {github_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to save learning data: {str(e)}"
            }

    def list_local_memories(self) -> list:
        """List local memory files"""
        memory_dir = Path("memory")
        if not memory_dir.exists():
            return []
            
        return sorted([str(f) for f in memory_dir.glob("*.json")])

    def list_github_memories(self) -> list:
        """List memory files in GitHub repository"""
        try:
            contents = self.repo.get_contents("memory")
            return [content.path for content in contents if content.path.endswith('.json')]
        except Exception:
            return []

    def load_memory_local(self, filename: str) -> dict:
        """Load memory from local file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def load_memory_from_github(self, repo_name: str, file_path: str) -> dict:
        """Load memory from GitHub"""
        try:
            content = self.repo.get_contents(file_path)
            content_str = content.decoded_content.decode('utf-8')
            return json.loads(content_str)
        except Exception:
            return None

    def sync_with_github(self) -> dict:
        """Sync local memory with GitHub"""
        try:
            # Get all GitHub memories
            github_memories = self.list_github_memories()
            
            # Download each memory file
            for memory_path in github_memories:
                content = self.repo.get_contents(memory_path)
                
                local_path = Path("memory") / os.path.basename(memory_path)
                local_path.parent.mkdir(exist_ok=True)
                
                with open(local_path, 'wb') as f:
                    f.write(content.decoded_content)
                    
            return {
                "success": True,
                "message": f"Synced {len(github_memories)} memory files"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Sync failed: {str(e)}"
            }
