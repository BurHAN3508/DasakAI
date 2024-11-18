import os
import signal
import sys
from agent import AutonomousAgent
from dotenv import load_dotenv
from datetime import datetime

def signal_handler(sig, frame):
    """Handle graceful shutdown on CTRL+C"""
    print("\nSaving agent memory before exit...")
    if 'agent' in globals():
        agent.save_memory(backup_to_github=True)
    print("Goodbye!")
    sys.exit(0)

def main():
    # Initialize the agent
    global agent
    agent = AutonomousAgent(name="DasakAI")
    
    # Load previous memories if they exist
    agent.load_memory()
    
    # Set initial goals
    initial_goals = [
        "Learn from trending AI repositories",
        "Analyze and understand user's coding patterns",
        "Build knowledge base from GitHub interactions",
        "Assist in code development and problem-solving"
    ]
    agent.set_goals(initial_goals)
    
    # Initial GitHub learning
    print(f" {agent.name} is starting up and learning from GitHub...")
    learning_result = agent.learn_from_github(topics=["artificial-intelligence", "machine-learning", "autonomous-agents"])
    
    print(f"\n {agent.name} has learned from {len(learning_result.get('trending_repos', [])) if learning_result else 0} repositories")
    
    # Start interaction loop
    while True:
        try:
            # Get user input
            user_input = input(f"\n What would you like {agent.name} to do? (type 'exit' to quit): ")
            
            if user_input.lower() in ['exit', 'quit']:
                break
                
            # Let the agent think about the input
            context = {
                "user_input": user_input,
                "current_time": datetime.now().isoformat()
            }
            
            thought = agent.think(context)
            print(f"\n Thinking: {thought}")
            
            # Execute relevant GitHub actions based on thought
            if "github" in thought.lower():
                result = agent.interact_with_github("learn")
                print(f"\n Learning Result: {result}")
            
            # Save memory periodically
            agent.save_memory()
            
        except Exception as e:
            print(f"\n Error: {str(e)}")
            continue

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load environment variables
    load_dotenv()
    
    # Ensure required environment variables are set
    required_vars = ["HUGGINGFACE_API_KEY", "GITHUB_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f" Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        sys.exit(1)
    
    print(" Starting DasakAI - Autonomous Agent")
    main()
