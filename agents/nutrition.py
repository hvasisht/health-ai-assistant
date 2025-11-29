"""
Nutrition Agent - Handles meal tracking and nutrition guidance with RAG.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.db_manager import add_meal, get_meals
from utils.prompts import get_nutrition_prompt
from utils.helpers import parse_meal_input, format_meal_data, estimate_meal_calories

# RAG import
try:
    from rag.medical_knowledge import MedicalKnowledgeRAG
except:
    MedicalKnowledgeRAG = None

# Load environment variables
load_dotenv()

class NutritionAgent:
    """Handles nutrition tracking and dietary guidance with GI database RAG."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the Nutrition Agent with GPT-3.5-turbo + RAG for GI data.
        
        Args:
            model_name: OpenAI model to use (default: gpt-3.5-turbo)
            temperature: Controls response variety
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
                print(f"✅ Nutrition Agent initialized with {model_name} + RAG")
            except Exception as e:
                print(f"⚠️ Nutrition Agent initialized with {model_name} (RAG unavailable)")
                self.rag = None
        else:
            self.rag = None
            print(f"✅ Nutrition Agent initialized with {model_name} (no RAG)")
    
    def process_message(self, user_id: int, user_message: str) -> str:
        """
        Process user message related to nutrition.
        
        Args:
            user_id: The user's ID
            user_message: The user's input message
            
        Returns:
            Agent's response
        """
        # Check if user wants to log a meal
        meal_name = parse_meal_input(user_message)
        
        if meal_name:
            # Estimate nutritional values
            nutrition = estimate_meal_calories(meal_name)
            
            # Determine meal type from time or keywords
            meal_type = self._determine_meal_type(user_message)
            
            # Log the meal
            meal_id = add_meal(
                user_id=user_id,
                meal_name=meal_name,
                meal_type=meal_type,
                calories=nutrition['calories'],
                carbs=nutrition['carbs'],
                protein=nutrition['protein'],
                fats=nutrition['fats']
            )
            
            # Create informative response
            response = f"✅ **Meal logged successfully!**\n\n"
            response += f"🍽️ **Meal**: {meal_name.title()}\n"
            if meal_type:
                response += f"⏰ **Type**: {meal_type.title()}\n"
            response += f"\n📊 **Estimated Nutrition**:\n"
            response += f"- Calories: {nutrition['calories']} cal\n"
            response += f"- Carbs: {nutrition['carbs']}g\n"
            response += f"- Protein: {nutrition['protein']}g\n"
            response += f"- Fats: {nutrition['fats']}g\n\n"
            
            # Add nutritional insight
            if nutrition['protein'] >= 20:
                response += "💪 Great protein content! Excellent for muscle maintenance."
            elif nutrition['carbs'] > 60:
                response += "🌾 High in carbs. Pair with protein for balanced energy."
            elif nutrition['calories'] < 300:
                response += "🥗 Light meal! Perfect for a healthy snack or light eating."
            else:
                response += "👍 Well-balanced meal! Keep up the healthy eating!"
            
            return response
        
        # If not logging, get recent data and ask LLM for advice
        recent_meals = get_meals(user_id, limit=10)
        meal_data_str = format_meal_data(recent_meals)
        
        # Get RAG context for nutrition
        rag_context = ""
        if self.rag:
            try:
                # Search for glycemic index info
                rag_context = self.rag.get_context(f"glycemic index nutrition {user_message}", n_results=1)
            except Exception as e:
                print(f"RAG retrieval error: {e}")
                rag_context = ""
        
        # Get AI response with context + RAG
        prompt = get_nutrition_prompt(user_message, meal_data_str)
        
        if rag_context:
            prompt += f"\n\n{rag_context}\n\nUse this glycemic index data to provide accurate nutritional guidance. Mention GI values when relevant."
        
        messages = [
            SystemMessage(content="You are a supportive nutrition guide with access to glycemic index data. Use GI information when discussing food choices for diabetes."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I'm having trouble processing that right now. Error: {str(e)}"
    
    def _determine_meal_type(self, message: str) -> str:
        """Determine meal type from message."""
        message_lower = message.lower()
        
        if 'breakfast' in message_lower:
            return 'breakfast'
        elif 'lunch' in message_lower:
            return 'lunch'
        elif 'dinner' in message_lower:
            return 'dinner'
        elif 'snack' in message_lower:
            return 'snack'
        else:
            return None
    
    def get_daily_summary(self, user_id: int) -> str:
        """
        Get a summary of today's nutrition.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Summary text
        """
        meals = get_meals(user_id, limit=20)  # Get recent meals
        
        if not meals:
            return "No meals logged today. Let's start tracking your nutrition! 🥗"
        
        # Calculate totals
        total_calories = sum(m.get('calories', 0) for m in meals if m.get('calories'))
        total_carbs = sum(m.get('carbs', 0) for m in meals if m.get('carbs'))
        total_protein = sum(m.get('protein', 0) for m in meals if m.get('protein'))
        total_fats = sum(m.get('fats', 0) for m in meals if m.get('fats'))
        meal_count = len(meals)
        
        summary = f"""📊 **Daily Nutrition Summary**

🍽️ **Meals Logged**: {meal_count}
🔥 **Total Calories**: {total_calories} cal
🌾 **Carbs**: {total_carbs:.1f}g
💪 **Protein**: {total_protein:.1f}g
🥑 **Fats**: {total_fats:.1f}g

"""
        
        # Add nutritional feedback
        if total_protein < 50:
            summary += "💡 Try to include more protein-rich foods (chicken, fish, beans, eggs)."
        elif total_protein > 100:
            summary += "💪 Excellent protein intake! Great for muscle maintenance and recovery."
        
        if total_calories < 1200:
            summary += "\n⚠️ Calories seem low. Make sure you're eating enough to fuel your body."
        elif total_calories > 2500:
            summary += "\n📝 High calorie intake today. Balance with activity or lighter meals tomorrow."
        else:
            summary += "\n✅ Good calorie balance for the day!"
        
        return summary