#!/usr/bin/env python3
"""
Your First ADK Agent - Hello World Example

This is a simple agent that demonstrates:
- Basic agent setup
- Simple conversation handling
- Tool integration basics
"""

import os
from typing import Dict, Any

# Note: These imports will need to be updated based on the actual ADK API
# This is a conceptual example based on typical agent frameworks

class HelloAgent:
    """A simple greeting agent that demonstrates basic ADK concepts."""
    
    def __init__(self, name: str = "Hello Agent"):
        self.name = name
        self.conversation_history = []
        
    def process_message(self, message: str) -> str:
        """Process a user message and return a response."""
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Simple reasoning - check for greeting patterns
        if any(greeting in message.lower() for greeting in ["hello", "hi", "hey"]):
            response = f"Hello! I'm {self.name}, an AI agent built with Google ADK. How can I help you today?"
        elif "time" in message.lower():
            response = self._get_current_time()
        elif "weather" in message.lower():
            response = "I'd love to help with weather information! In a more advanced version, I could use a weather API tool."
        elif "bye" in message.lower() or "goodbye" in message.lower():
            response = "Goodbye! It was nice chatting with you."
        else:
            response = f"Interesting question! As a simple agent, I'm still learning. You said: '{message}'"
            
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _get_current_time(self) -> str:
        """Tool function to get current time."""
        import datetime
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "type": "Hello Agent",
            "capabilities": [
                "Basic conversation",
                "Time queries",
                "Simple greetings"
            ],
            "conversation_length": len(self.conversation_history)
        }

def main():
    """Demonstrate the Hello Agent in action."""
    
    print("🤖 Hello Agent Demo - Your First ADK Agent")
    print("=" * 50)
    
    # Create agent instance
    agent = HelloAgent("My First Agent")
    
    # Sample conversation
    test_messages = [
        "Hello there!",
        "What time is it?",
        "Can you tell me the weather?",
        "What can you do?",
        "Goodbye!"
    ]
    
    for message in test_messages:
        print(f"\n👤 User: {message}")
        response = agent.process_message(message)
        print(f"🤖 Agent: {response}")
    
    # Show agent info
    print(f"\n📊 Agent Information:")
    info = agent.get_agent_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
