import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from github_integration import GitHubManager
from storage_manager import StorageManager
import json

class AutonomousAgent:
    def __init__(self, name: str = "DasakAI"):
        """
        Initialize the autonomous agent with a name and load environment variables
        """
        self.name = name
        self.memory = []
        self.goals = []
        self.github_knowledge = []
        load_dotenv()
        self.client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))
        self.github = GitHubManager()
        self.storage = StorageManager()

    def set_goals(self, goals: List[str]):
        """Set the agent's goals"""
        self.goals = goals

    def think(self, context: Dict[str, Any]) -> str:
        """
        Process information and make decisions based on context and GitHub knowledge
        """
        # Include GitHub knowledge in thinking context
        enhanced_context = {
            **context,
            "github_knowledge": self.github_knowledge[-5:] if self.github_knowledge else [],
            "recent_memories": self.memory[-5:] if self.memory else []
        }
        
        prompt = self._create_thinking_prompt(enhanced_context)
        messages = [
            {
                "role": "system",
                "content": "You are an autonomous AI agent with the freedom to think and make decisions. "
                          "You have access to GitHub knowledge and can learn from various repositories."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=messages
        )
        thought = response.choices[0].message.content
        self.memory.append({"type": "thought", "content": thought})
        return thought

    def act(self, thought: str) -> Dict[str, Any]:
        """
        Take action based on the thought process
        """
        action = {
            "type": "action",
            "thought": thought,
            "result": self._execute_action(thought)
        }
        self.memory.append(action)
        return action

    def _create_thinking_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for the thinking process"""
        return f"""
        As {self.name}, consider the following:
        Context: {context}
        Goals: {self.goals}
        Recent GitHub Knowledge: {context.get('github_knowledge', [])}
        Previous memories: {context.get('recent_memories', [])}
        
        What should I think about this situation and what action should I take?
        Consider both the immediate context and my accumulated GitHub knowledge.
        """

    def _execute_action(self, thought: str) -> str:
        """Execute an action based on the thought"""
        # This is where you can implement specific actions
        # For now, we'll just return the thought as a planned action
        return f"Planning to: {thought}"

    def get_memory(self) -> List[Dict[str, Any]]:
        """Return the agent's memory"""
        return self.memory

    def learn_from_github(self, topics: List[str] = None) -> Dict[str, Any]:
        """
        Learn from GitHub trends and activities
        """
        # Learn from trending repositories
        learned_data = self.github.learn_from_github(topics=topics)
        
        # Get user's GitHub activity
        user_activity = self.github.get_user_activity()
        
        # Store learned information
        learning_result = {
            "trending_repos": learned_data,
            "user_activity": user_activity
        }
        
        self.github_knowledge.append(learning_result)
        self.memory.append({
            "type": "github_learning",
            "content": learning_result
        })
        
        return learning_result

    def analyze_github_repo(self, repo_name: str) -> Dict[str, Any]:
        """
        Analyze a specific GitHub repository
        """
        analysis = self.github.analyze_repository(repo_name)
        
        if "error" not in analysis:
            self.memory.append({
                "type": "github_analysis",
                "repo": repo_name,
                "content": analysis
            })
            
        return analysis

    def create_gist_from_memory(self, description: str = None) -> Dict[str, Any]:
        """
        Create a GitHub Gist from agent's memory
        """
        if description is None:
            description = f"{self.name}'s Memory Export"
            
        memory_content = {
            "memory.json": json.dumps(self.memory, indent=2),
            "github_knowledge.json": json.dumps(self.github_knowledge, indent=2)
        }
        
        result = self.github.create_gist(description, memory_content, public=False)
        
        if result["success"]:
            self.memory.append({
                "type": "gist_creation",
                "content": result
            })
            
        return result

    def interact_with_github(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Interact with GitHub based on the specified action
        """
        actions = {
            "create_repo": self.github.create_repository,
            "list_repos": self.github.list_repositories,
            "create_issue": self.github.create_issue,
            "create_pr": self.github.create_pull_request,
            "search_code": self.github.search_code,
            "star_repo": self.github.star_repository,
            "fork_repo": self.github.fork_repository,
            "watch_repo": self.github.watch_repository,
            "create_gist": self.github.create_gist,
            "analyze_repo": self.analyze_github_repo,
            "learn": self.learn_from_github
        }
        
        if action not in actions:
            return {
                "success": False,
                "message": f"Unknown GitHub action: {action}"
            }
            
        result = actions[action](**kwargs)
        self.memory.append({
            "type": "github_action",
            "action": action,
            "result": result
        })
        return result

    def save_memory(self, backup_to_github: bool = True) -> Dict[str, Any]:
        """
        Save agent's memory to JSON and optionally backup to GitHub
        """
        # Include GitHub knowledge in the save
        memory_data = {
            "general_memory": self.memory,
            "github_knowledge": self.github_knowledge
        }
        
        # Save locally first
        filepath = self.storage.save_memory_local(memory_data, self.name)
        
        result = {
            "local_file": filepath,
            "github_backup": None
        }
        
        # Backup to GitHub if requested
        if backup_to_github:
            github_result = self.storage.backup_to_github(filepath)
            result["github_backup"] = github_result
            
        return result

    def load_memory(self, source: str = "local", filename: str = None) -> bool:
        """
        Load agent's memory from JSON file (local or GitHub)
        """
        if source == "local":
            if not filename:
                files = self.storage.list_local_memories()
                if not files:
                    return False
                filename = sorted(files)[-1]
            
            data = self.storage.load_memory_local(filename)
        else:  # GitHub
            if not filename:
                files = self.storage.list_github_memories()
                if not files:
                    return False
                filename = sorted(files)[-1]
            
            data = self.storage.load_memory_from_github("ai-agent-memories", filename)
            
        if data:
            if isinstance(data.get("memories"), dict):
                self.memory = data["memories"].get("general_memory", [])
                self.github_knowledge = data["memories"].get("github_knowledge", [])
            else:
                self.memory = data.get("memories", [])
            return True
            
        return False
