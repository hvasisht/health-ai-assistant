"""
Diabetes Agent - Handles glucose tracking and diabetes management.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from database.db_manager import add_glucose_reading, get_glucose_readings, get_glucose_stats
from utils.prompts import get_diabetes_prompt
from utils.helpers import parse_glucose_input, format_glucose_data, get_glucose_status

# Load environment variables
load_dotenv()

class DiabetesAgent:
    """Handles diabetes management and glucose tracking."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the Diabetes Agent with GPT-3.5-turbo for fast, cost-effective responses.
        
        Args:
            model_name: OpenAI model to use (default: gpt-3.5-turbo)
            temperature: Controls randomness (0-1)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        print(f"✅ Diabetes Agent initialized with {model_name}")
    
    def process_message(self, user_id: int, user_message: str) -> str:
        """
        Process user message related to diabetes management.
        
        Args:
            user_id: The user's ID
            user_message: The user's input message
            
        Returns:
            Agent's response
        """
        # Check if user wants to log glucose
        glucose_value = parse_glucose_input(user_message)
        
        if glucose_value:
            # Log the glucose reading
            reading_id = add_glucose_reading(user_id, glucose_value)
            
            # Get status
            status, color = get_glucose_status(glucose_value)
            
            # Create response
            response = f"✅ Logged glucose reading: **{glucose_value} mg/dL**\n\n{status}\n\n"
            
            # Add context-aware feedback based on ADA guidelines
            if glucose_value < 70:
                response += "🚨 **This is hypoglycemia (low blood sugar).** Treat immediately with 15g of fast-acting carbs (juice, glucose tablets, or candy). Recheck in 15 minutes. If symptoms persist, seek medical help."
            elif glucose_value < 80:
                response += "⚠️ This is on the lower end. Consider a small snack to prevent hypoglycemia, especially if you're about to exercise or it's been a while since eating."
            elif glucose_value <= 130:
                response += "✅ **Excellent!** This is in the normal **before-meal range (80-130 mg/dL)**. Keep up the great work! 💪"
            elif glucose_value <= 180:
                response += "✅ **Good!** This is within the target **after-meal range (less than 180 mg/dL)**. Your glucose is well managed!"
            elif glucose_value <= 250:
                response += "⚠️ **This is elevated.** Stay hydrated, avoid additional carbs for now, and consider light activity like a 15-minute walk. If consistently high, contact your healthcare provider."
            else:
                response += "🚨 **This is very high.** Drink plenty of water, avoid food temporarily, and contact your healthcare provider if this persists or if you feel unwell (nausea, vomiting, confusion)."
            
            return response
        
        # If not logging, get recent data and ask LLM for insights
        recent_readings = get_glucose_readings(user_id, limit=10)
        glucose_data = format_glucose_data(recent_readings)
        
        # Get stats if available
        stats = get_glucose_stats(user_id, days=7)
        if stats.get('reading_count', 0) > 0:
            avg = stats.get('avg_glucose', 0)
            glucose_data += f"\n7-day average: {avg:.1f} mg/dL"
        
        # Get AI response with context
        prompt = get_diabetes_prompt(user_message, glucose_data)
        
        messages = [
            SystemMessage(content="You are a helpful diabetes management assistant. Use ADA guidelines: before-meal target 80-130 mg/dL, after-meal less than 180 mg/dL."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I'm having trouble processing that right now. Error: {str(e)}"
    
    def get_glucose_summary(self, user_id: int, days: int = 7) -> str:
        """
        Get a summary of glucose readings for the past N days.
        
        Args:
            user_id: The user's ID
            days: Number of days to include
            
        Returns:
            Summary text
        """
        stats = get_glucose_stats(user_id, days=days)
        
        if stats.get('reading_count', 0) == 0:
            return f"No glucose readings found in the last {days} days."
        
        avg = stats.get('avg_glucose', 0)
        min_val = stats.get('min_glucose', 0)
        max_val = stats.get('max_glucose', 0)
        count = stats.get('reading_count', 0)
        
        summary = f"""📊 **Glucose Summary (Last {days} Days)**

📈 **Average**: {avg:.1f} mg/dL
📉 **Lowest**: {min_val:.1f} mg/dL
📊 **Highest**: {max_val:.1f} mg/dL
🔢 **Total Readings**: {count}

**Target Ranges (ADA Guidelines)**:
- Before meals: 80-130 mg/dL
- After meals: Less than 180 mg/dL

"""
        
        # Add interpretation based on ADA guidelines
        if avg < 80:
            summary += "⚠️ Your average is **low**. Discuss with your healthcare provider about adjusting medications or meal timing to prevent hypoglycemia."
        elif avg <= 130:
            summary += "✅ **Excellent control!** Your average is in the ideal before-meal range (80-130 mg/dL). Keep up the great work!"
        elif avg <= 154:
            summary += "✅ **Good control!** Your average suggests well-managed glucose levels. Continue monitoring regularly."
        elif avg <= 180:
            summary += "⚠️ Your average is **slightly elevated**. Consider reviewing your diet, physical activity, and medication adherence with your healthcare provider."
        else:
            summary += "🚨 Your average is **high**. Please consult with your healthcare provider about adjusting your diabetes management plan."
        
        # Add context about highs and lows
        if min_val < 70:
            summary += f"\n\n⚠️ **Note**: You had at least one low reading ({min_val:.1f} mg/dL). Be cautious of hypoglycemia."
        
        if max_val > 180:
            summary += f"\n\n⚠️ **Note**: You had at least one high reading ({max_val:.1f} mg/dL). Monitor for patterns."
        
        return summary