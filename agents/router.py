"""
Router Agent - Routes user messages to the appropriate specialized agent.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from utils.prompts import get_router_prompt

# Load environment variables
load_dotenv()

class RouterAgent:
    """Routes user messages to appropriate specialized agents."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.3):
        """
        Initialize the Router Agent.
        
        Args:
            model_name: OpenAI model to use
            temperature: Lower = more consistent, Higher = more creative
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def route(self, user_message: str) -> str:
        """
        Analyze user message and route to appropriate agent.
        
        Args:
            user_message: The user's input message
            
        Returns:
            Agent name: "DIABETES_AGENT", "FITNESS_AGENT", "NUTRITION_AGENT", or "GENERAL"
        """
        # Get the router prompt with user message
        prompt = get_router_prompt(user_message)
        
        # Create messages for LLM
        messages = [
            SystemMessage(content="You are a routing assistant. Respond with only ONE word."),
            HumanMessage(content=prompt)
        ]
        
        try:
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Extract the route (clean up response)
            route = response.content.strip().upper()
            
            # Validate route
            valid_routes = ["DIABETES_AGENT", "FITNESS_AGENT", "NUTRITION_AGENT", "GENERAL"]
            
            if route in valid_routes:
                return route
            else:
                # Default to GENERAL if unclear
                return "GENERAL"
                
        except Exception as e:
            print(f"Error in routing: {e}")
            return "GENERAL"
    
    def get_route_explanation(self, route: str) -> str:
        """
        Get a human-readable explanation of the route.
        
        Args:
            route: The agent route name
            
        Returns:
            Explanation string
        """
        explanations = {
            "DIABETES_AGENT": "🩸 Routing to Diabetes Management...",
            "FITNESS_AGENT": "💪 Routing to Fitness Coach...",
            "NUTRITION_AGENT": "🥗 Routing to Nutrition Guide...",
            "GENERAL": "👋 General response..."
        }
        
        return explanations.get(route, "Processing...")


# Example usage and testing
if __name__ == "__main__":
    # Test the router
    router = RouterAgent()
    
    test_messages = [
        "Log my glucose: 125",
        "I went for a 30 minute run",
        "I ate chicken salad for lunch",
        "Hello, how are you?",
        "What's my average blood sugar?",
        "Should I exercise today?",
        "How many calories in an apple?"
    ]
    
    print("Testing Router Agent:\n")
    for msg in test_messages:
        route = router.route(msg)
        explanation = router.get_route_explanation(route)
        print(f"Message: '{msg}'")
        print(f"Route: {route} - {explanation}\n")