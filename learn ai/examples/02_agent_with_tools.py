#!/usr/bin/env python3
"""
Agent with Tools - Intermediate Example

This example demonstrates:
- Tool definition and registration
- Tool execution within agent reasoning
- More sophisticated conversation handling
- Error handling and validation
"""

import json
import requests
from typing import Dict, Any, List, Callable
from datetime import datetime

class Tool:
    """Base class for agent tools."""
    
    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function
    
    def execute(self, *args, **kwargs):
        """Execute the tool function."""
        try:
            return self.function(*args, **kwargs)
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"

class ToolAgent:
    """An agent that can use various tools to accomplish tasks."""
    
    def __init__(self, name: str = "Tool Agent"):
        self.name = name
        self.tools = {}
        self.conversation_history = []
        
        # Register default tools
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register the default set of tools."""
        
        # Time tool
        time_tool = Tool(
            name="get_time",
            description="Get the current date and time",
            function=self._get_current_time
        )
        self.register_tool(time_tool)
        
        # Calculator tool
        calc_tool = Tool(
            name="calculate",
            description="Perform basic mathematical calculations",
            function=self._calculate
        )
        self.register_tool(calc_tool)
        
        # Web search simulation tool
        search_tool = Tool(
            name="search",
            description="Search for information (simulated)",
            function=self._search_info
        )
        self.register_tool(search_tool)
    
    def register_tool(self, tool: Tool):
        """Register a new tool with the agent."""
        self.tools[tool.name] = tool
    
    def _get_current_time(self) -> str:
        """Tool: Get current date and time."""
        now = datetime.now()
        return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def _calculate(self, expression: str) -> str:
        """Tool: Safely evaluate mathematical expressions."""
        try:
            # Simple whitelist of allowed operations
            allowed_chars = set('0123456789+-*/().%^ ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Expression contains invalid characters"
            
            # Replace ^ with ** for Python exponentiation
            expression = expression.replace('^', '**')
            
            result = eval(expression)
            return f"Result: {expression} = {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _search_info(self, query: str) -> str:
        """Tool: Simulate web search (in real implementation, use actual search API)."""
        # This is a simulation - in real ADK, you'd use actual search APIs
        responses = {
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "ai": "Artificial Intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence.",
            "weather": "Weather information requires real-time data from weather APIs. This is a simulated response.",
            "default": f"Search results for '{query}' would appear here in a real implementation."
        }
        
        query_lower = query.lower()
        for key, response in responses.items():
            if key in query_lower:
                return response
        
        return responses["default"]
    
    def process_message(self, message: str) -> str:
        """Process user message and determine if tools are needed."""
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Simple keyword-based tool detection
        response = self._reason_and_act(message)
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _reason_and_act(self, message: str) -> str:
        """Reason about the message and decide which tools to use."""
        
        message_lower = message.lower()
        
        # Time-related queries
        if any(word in message_lower for word in ["time", "date", "when", "clock"]):
            tool_result = self.tools["get_time"].execute()
            return f"I'll check the time for you. {tool_result}"
        
        # Math-related queries
        elif any(word in message_lower for word in ["calculate", "math", "solve", "+", "-", "*", "/"]):
            # Extract potential math expression
            # In a real implementation, you'd use more sophisticated parsing
            math_expressions = []
            words = message.split()
            for word in words:
                if any(char in word for char in "+-*/"):
                    math_expressions.append(word)
            
            if math_expressions:
                tool_result = self.tools["calculate"].execute(math_expressions[0])
                return f"I'll calculate that for you. {tool_result}"
            else:
                return "I can help with calculations! Please provide a mathematical expression like '2 + 2' or '10 * 5'."
        
        # Search-related queries
        elif any(word in message_lower for word in ["search", "find", "what is", "tell me about"]):
            # Extract search query (simplified)
            search_query = message
            if "what is" in message_lower:
                search_query = message_lower.split("what is")[-1].strip()
            elif "tell me about" in message_lower:
                search_query = message_lower.split("tell me about")[-1].strip()
            
            tool_result = self.tools["search"].execute(search_query)
            return f"I'll search for information about that. {tool_result}"
        
        # Tool listing
        elif "tools" in message_lower or "capabilities" in message_lower:
            tool_list = ", ".join(self.tools.keys())
            return f"I have access to these tools: {tool_list}. I can help with time queries, calculations, and searching for information!"
        
        # Default response
        else:
            return f"I'm a tool-enabled agent! I can help with time, calculations, and searching. What would you like me to do?"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get detailed agent information."""
        return {
            "name": self.name,
            "type": "Tool-Enabled Agent",
            "available_tools": list(self.tools.keys()),
            "tool_descriptions": {name: tool.description for name, tool in self.tools.items()},
            "conversation_length": len(self.conversation_history)
        }

def main():
    """Demonstrate the Tool Agent in action."""
    
    print("🛠️ Tool Agent Demo - Agent with Capabilities")
    print("=" * 50)
    
    # Create agent instance
    agent = ToolAgent("My Tool Agent")
    
    # Sample conversation showcasing different tools
    test_messages = [
        "Hello! What can you do?",
        "What time is it?",
        "Can you calculate 15 * 8 + 23?",
        "Tell me about Python programming",
        "What tools do you have available?",
        "Search for information about AI"
    ]
    
    for message in test_messages:
        print(f"\n👤 User: {message}")
        response = agent.process_message(message)
        print(f"🤖 Agent: {response}")
    
    # Show detailed agent info
    print(f"\n📊 Agent Information:")
    info = agent.get_agent_info()
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
