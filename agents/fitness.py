"""
Fitness Agent - Handles exercise tracking and fitness coaching with RAG.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import add_exercise, get_exercises
from utils.prompts import get_fitness_prompt
from utils.helpers import parse_exercise_input, format_exercise_data, estimate_exercise_calories

# RAG import
try:
    from rag.medical_knowledge import MedicalKnowledgeRAG
except:
    MedicalKnowledgeRAG = None

# Load environment variables
load_dotenv()

class FitnessAgent:
    """Handles fitness tracking and workout coaching with exercise safety RAG."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.8):
        """
        Initialize the Fitness Agent with GPT-4o-mini + RAG for safe exercise guidance.
        
        Args:
            model_name: OpenAI model to use (default: gpt-4o-mini)
            temperature: Controls creativity (higher = more varied suggestions)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize RAG
        if MedicalKnowledgeRAG:
            try:
                self.rag = MedicalKnowledgeRAG()
                print(f"✅ Fitness Agent initialized with {model_name} + RAG")
            except Exception as e:
                print(f"⚠️ Fitness Agent initialized with {model_name} (RAG unavailable)")
                self.rag = None
        else:
            self.rag = None
            print(f"✅ Fitness Agent initialized with {model_name} (no RAG)")
    
    def process_message(self, user_id: int, user_message: str) -> str:
        """
        Process user message related to fitness.
        
        Args:
            user_id: The user's ID
            user_message: The user's input message
            
        Returns:
            Agent's response
        """
        # Check if user wants to log exercise
        exercise_data = parse_exercise_input(user_message)
        
        if exercise_data:
            activity, duration = exercise_data
            
            # Estimate calories burned
            calories = estimate_exercise_calories(activity, duration)
            
            # Log the exercise
            exercise_id = add_exercise(
                user_id=user_id,
                activity_type=activity,
                duration=duration,
                calories_burned=calories,
                intensity="moderate"  # Default
            )
            
            # Create encouraging response
            response = f"🎉 **Great workout!** You just logged:\n\n"
            response += f"💪 **Activity**: {activity.title()}\n"
            response += f"⏱️ **Duration**: {duration} minutes\n"
            response += f"🔥 **Est. Calories Burned**: {calories} cal\n\n"
            
            # Add motivational message
            if duration >= 45:
                response += "Outstanding effort! That's a solid workout! 🌟"
            elif duration >= 30:
                response += "Awesome! You're crushing your fitness goals! 💪"
            elif duration >= 15:
                response += "Nice work! Every minute counts! 🚀"
            else:
                response += "Great start! Keep building that momentum! ⚡"
            
            return response
        
        # If not logging, get recent data and ask LLM for coaching
        recent_exercises = get_exercises(user_id, limit=10)
        exercise_data_str = format_exercise_data(recent_exercises)
        
        # Get RAG context for exercise safety
        rag_context = ""
        if self.rag:
            try:
                rag_context = self.rag.get_context(f"exercise safety diabetes {user_message}", n_results=1)
            except Exception as e:
                print(f"RAG retrieval error: {e}")
                rag_context = ""
        
        # Get AI response with context + RAG
        prompt = get_fitness_prompt(user_message, exercise_data_str)
        
        if rag_context:
            prompt += f"\n\n{rag_context}\n\nUse these safety guidelines when recommending exercise."
        
        messages = [
            SystemMessage(content="You are an enthusiastic fitness coach. Always consider diabetes exercise safety guidelines."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I'm having trouble processing that right now. Error: {str(e)}"
    
    def get_weekly_summary(self, user_id: int) -> str:
        """
        Get a summary of this week's exercise.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Summary text
        """
        exercises = get_exercises(user_id, limit=50)  # Get more for weekly view
        
        if not exercises:
            return "No exercise logged this week. Ready to get started? 💪"
        
        # Calculate totals
        total_minutes = sum(ex['duration'] for ex in exercises)
        total_calories = sum(ex.get('calories_burned', 0) for ex in exercises)
        workout_count = len(exercises)
        
        # Get unique activities
        activities = set(ex['activity_type'] for ex in exercises)
        
        summary = f"""📊 **Weekly Fitness Summary**

🏃 **Total Workouts**: {workout_count}
⏱️ **Total Time**: {total_minutes} minutes ({total_minutes/60:.1f} hours)
🔥 **Total Calories**: {total_calories} cal
💪 **Activities**: {', '.join(activities)}

"""
        
        # Add motivational feedback
        if total_minutes >= 150:
            summary += "🌟 Amazing! You've exceeded the recommended 150 minutes of activity per week (ADA guidelines)!"
        elif total_minutes >= 100:
            summary += "💪 Great progress! Keep pushing toward that 150-minute weekly goal!"
        elif total_minutes >= 50:
            summary += "👍 Good start! Try to add a few more sessions this week."
        else:
            summary += "🚀 Let's step it up! Aim for at least 150 minutes of activity per week."
        
        return summary