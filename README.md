# Özgür - Autonomous AI Agent

This project implements an autonomous AI agent named Özgür that can think, make decisions, and interact with its environment independently using the Qwen2.5-Coder model from Hugging Face. The agent can also interact with GitHub repositories and perform various GitHub operations.

## Features

- 🤖 Autonomous decision-making capabilities using Qwen2.5-Coder
- 🧠 Memory system to store experiences and learnings
- 🌍 Dynamic environment with random events
- 🎯 Goal-oriented behavior
- 🔄 Continuous learning and adaptation
- 📦 GitHub Integration:
  - Create and manage repositories
  - Create issues and pull requests
  - Search code across GitHub
  - Star and fork repositories
  - List user repositories

## Setup

1. Create a `.env` file in the project root and add your API keys:
```
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
GITHUB_TOKEN=your_github_token_here
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the agent:
```bash
python main.py
```

## Project Structure

- `agent.py`: Contains the AutonomousAgent class that implements the core agent functionality using Qwen2.5-Coder
- `environment.py`: Implements the Environment class that the agent interacts with
- `github_integration.py`: Provides GitHub integration capabilities
- `main.py`: Entry point of the application, demonstrates agent-environment interaction
- `requirements.txt`: Lists all Python dependencies

## How it Works

1. The agent observes the current state of the environment
2. Based on its observations, it thinks about the situation using Qwen2.5-Coder
3. The agent decides on actions to take, including GitHub operations
4. The environment processes these actions and updates its state
5. The cycle continues, allowing the agent to learn and adapt

## GitHub Integration

The agent can perform various GitHub operations:
- Create new repositories
- List existing repositories
- Create issues and pull requests
- Search for code across GitHub
- Star and fork repositories

Example usage in code:
```python
# Create a new repository
result = agent.interact_with_github("create_repo", 
    name="my-new-repo", 
    description="A new repository created by Özgür")

# Search for code
results = agent.interact_with_github("search_code", 
    query="language:python machine learning")
```

## Customization

You can customize the agent's behavior by:
- Modifying the goals in `main.py`
- Adding new event types in `environment.py`
- Extending the agent's capabilities in `agent.py`
- Trying different Hugging Face models by changing the model parameter
- Adding new GitHub operations in `github_integration.py`

## Note

This is an experimental project demonstrating autonomous AI capabilities. The agent's actions are currently limited to the implemented environment and GitHub operations, but the system is designed to be extensible.
