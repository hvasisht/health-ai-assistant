"""
Insights Coordinator Agent - Orchestrates multi-agent collaboration for complex queries.
Addresses TA concern: "How is this different from a single LLM?"

This agent coordinates multiple specialized agents to answer complex questions
that require insights from multiple health domains.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

class InsightsCoordinatorAgent:
    """Coordinates multiple agents for complex health queries."""
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.7):
        """
        Initialize Insights Coordinator with GPT-4o for complex reasoning.
        
        Args:
            model_name: OpenAI model (GPT-4o for best coordination)
            temperature: Controls creativity
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        print(f"✅ Insights Coordinator initialized with {model_name}")
    
    def coordinate_analysis(self, user_id: int, question: str, agents: dict) -> str:
        """
        Coordinate multiple agents to answer complex questions.
        
        Args:
            user_id: User's ID
            question: Complex question requiring multiple agents
            agents: Dictionary of all available agents
            
        Returns:
            Comprehensive coordinated response
        """
        print(f"\n🔄 Coordinating multi-agent analysis for: '{question}'")
        
        # Step 1: Get insights from Pattern Analysis Agent
        print("  → Calling Pattern Analysis Agent...")
        pattern_insights = agents['pattern'].analyze_patterns(user_id)
        
        # Step 2: Get domain-specific insights based on question
        diabetes_insights = ""
        nutrition_insights = ""
        fitness_insights = ""
        
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['glucose', 'sugar', 'blood', 'diabetes', 'high', 'low']):
            print("  → Calling Diabetes Agent...")
            diabetes_insights = agents['diabetes'].process_message(user_id, question)
        
        if any(word in question_lower for word in ['food', 'meal', 'eat', 'diet', 'nutrition', 'carb']):
            print("  → Calling Nutrition Agent...")
            nutrition_insights = agents['nutrition'].process_message(user_id, question)
        
        if any(word in question_lower for word in ['exercise', 'workout', 'activity', 'tired', 'energy']):
            print("  → Calling Fitness Agent...")
            fitness_insights = agents['fitness'].process_message(user_id, question)
        
        # Step 3: Synthesize all insights
        print("  → Synthesizing insights...")
        
        synthesis_prompt = f"""You are a health insights coordinator. Multiple specialized AI agents have analyzed a user's question.

USER QUESTION: {question}

AGENT FINDINGS:

**Pattern Analysis Agent:**
{pattern_insights}

**Diabetes Agent:**
{diabetes_insights if diabetes_insights else "Not consulted for this query"}

**Nutrition Agent:**
{nutrition_insights if nutrition_insights else "Not consulted for this query"}

**Fitness Agent:**
{fitness_insights if fitness_insights else "Not consulted for this query"}

YOUR TASK:
Synthesize these findings into ONE comprehensive, actionable response that:
1. Directly answers the user's question
2. Combines insights from multiple agents coherently
3. Provides specific, personalized recommendations based on their data
4. Uses actual numbers and patterns mentioned by agents
5. Is encouraging and supportive

Focus on the MOST relevant insights. Don't just list what each agent said - weave them together into a cohesive answer."""

        messages = [
            SystemMessage(content="You are an expert at synthesizing multi-agent health insights into actionable advice."),
            HumanMessage(content=synthesis_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            coordinated_response = response.content
            
            # Add indicator that this was multi-agent coordination
            coordinated_response += "\n\n---\n*💡 This response coordinated insights from multiple specialized agents with your personal health data.*"
            
            return coordinated_response
            
        except Exception as e:
            return f"I'm having trouble coordinating the analysis. Error: {str(e)}"
    
    def should_coordinate(self, question: str) -> bool:
        """
        Determine if a question requires multi-agent coordination.
        
        Complex questions that need coordination:
        - "Why" questions (require causal analysis)
        - Questions mentioning multiple health aspects
        - Questions asking for optimization or improvement
        
        Returns:
            True if coordination needed, False otherwise
        """
        question_lower = question.lower()
        
        # "Why" questions often need multi-agent analysis
        if question_lower.startswith('why'):
            return True
        
        # Questions with multiple health domains
        domain_count = 0
        if any(word in question_lower for word in ['glucose', 'sugar', 'diabetes']):
            domain_count += 1
        if any(word in question_lower for word in ['food', 'meal', 'eat', 'nutrition']):
            domain_count += 1
        if any(word in question_lower for word in ['exercise', 'workout', 'activity']):
            domain_count += 1
        
        if domain_count >= 2:
            return True
        
        # Optimization/improvement questions
        if any(word in question_lower for word in ['improve', 'better', 'optimize', 'reduce', 'increase', 'how can i']):
            return True
        
        return False


# Testing
if __name__ == "__main__":
    from database.db_manager import get_all_users
    from agents.router import RouterAgent
    from agents.diabetes import DiabetesAgent
    from agents.fitness import FitnessAgent
    from agents.nutrition import NutritionAgent
    from agents.pattern_analysis import PatternAnalysisAgent
    
    print("Testing Insights Coordinator Agent...\n")
    
    # Initialize all agents
    agents = {
        'router': RouterAgent(),
        'diabetes': DiabetesAgent(),
        'fitness': FitnessAgent(),
        'nutrition': NutritionAgent(),
        'pattern': PatternAnalysisAgent()
    }
    
    coordinator = InsightsCoordinatorAgent()
    
    # Get test user
    users = get_all_users()
    if users:
        test_user = users[0]
        print(f"Testing with user: {test_user['name']} (ID: {test_user['id']})\n")
        
        # Test complex questions
        test_questions = [
            "Why is my glucose high in the afternoon?",
            "How can I improve my glucose control?",
            "What's the relationship between my meals and glucose?"
        ]
        
        for question in test_questions:
            print("\n" + "="*70)
            print(f"QUESTION: {question}")
            print("="*70)
            
            if coordinator.should_coordinate(question):
                print("✅ Multi-agent coordination needed")
                response = coordinator.coordinate_analysis(test_user['id'], question, agents)
            else:
                print("ℹ️ Single agent sufficient")
                response = "Single agent would handle this"
            
            print("\nRESPONSE:")
            print(response)
            print()