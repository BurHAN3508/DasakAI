from typing import Dict, Any, List
import random

class Environment:
    def __init__(self):
        """Initialize the environment with some basic state"""
        self.state = {
            "time": 0,
            "events": [],
            "resources": {
                "energy": 100,
                "knowledge": 0
            },
            "entities": []
        }
        
    def add_entity(self, entity: Dict[str, Any]):
        """Add an entity to the environment"""
        self.state["entities"].append(entity)
        
    def update(self) -> Dict[str, Any]:
        """Update the environment state"""
        self.state["time"] += 1
        
        # Generate random events
        if random.random() < 0.3:  # 30% chance of new event
            self.state["events"].append(self._generate_random_event())
            
        # Update resources
        self.state["resources"]["energy"] = max(0, self.state["resources"]["energy"] - 1)
        self.state["resources"]["knowledge"] += len(self.state["events"]) * 0.1
        
        return self.get_state()
    
    def get_state(self) -> Dict[str, Any]:
        """Return the current state of the environment"""
        return self.state
    
    def _generate_random_event(self) -> Dict[str, Any]:
        """Generate a random event in the environment"""
        event_types = [
            "new_information",
            "resource_discovery",
            "environmental_change",
            "interaction_opportunity"
        ]
        
        return {
            "type": random.choice(event_types),
            "time": self.state["time"],
            "impact": random.uniform(0, 1)
        }
    
    def interact(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process an interaction from an agent"""
        response = {
            "success": True,
            "message": f"Processed action: {action}",
            "state_change": {}
        }
        
        # Process the action and update state accordingly
        if action.get("type") == "gather_information":
            response["state_change"]["knowledge"] = random.uniform(0, 1)
        elif action.get("type") == "use_resource":
            if self.state["resources"]["energy"] >= 10:
                self.state["resources"]["energy"] -= 10
                response["state_change"]["result"] = "Resource used successfully"
            else:
                response["success"] = False
                response["message"] = "Insufficient energy"
                
        return response
