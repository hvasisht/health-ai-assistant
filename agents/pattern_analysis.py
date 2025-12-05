"""
Pattern Analysis Agent - Discovers user-specific patterns and correlations.
Addresses TA concern: "Logged data must provide actionable insights"
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from database.db_manager import get_glucose_readings, get_meals, get_exercises
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.helpers import get_openai_key

load_dotenv()

class PatternAnalysisAgent:
    """Analyzes historical data to find user-specific patterns and correlations."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.5):
        """
        Initialize Pattern Analysis Agent with GPT-4o-mini for analytical reasoning.
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=get_openai_key()
        )
        print(f"✅ Pattern Analysis Agent initialized with {model_name}")
    
    def analyze_patterns(self, user_id: int) -> str:
        """
        Comprehensive pattern analysis across all health data.
        
        Returns:
            Detailed analysis of user-specific patterns
        """
        patterns = []
        
        # Get all user data
        glucose_data = get_glucose_readings(user_id, limit=100)
        meal_data = get_meals(user_id, limit=100)
        exercise_data = get_exercises(user_id, limit=100)
        
        if not glucose_data:
            return "Not enough data yet. Log more glucose readings to see patterns."
        
        # Analysis 1: Exercise-Glucose Correlation
        exercise_pattern = self._analyze_exercise_glucose_correlation(
            user_id, glucose_data, exercise_data
        )
        if exercise_pattern:
            patterns.append(exercise_pattern)
        
        # Analysis 2: Meal-Glucose Correlation
        meal_pattern = self._analyze_meal_glucose_correlation(
            user_id, glucose_data, meal_data
        )
        if meal_pattern:
            patterns.append(meal_pattern)
        
        # Analysis 3: Time-of-Day Patterns
        time_pattern = self._analyze_time_patterns(glucose_data)
        if time_pattern:
            patterns.append(time_pattern)
        
        # Analysis 4: Exercise Timing Optimization
        timing_pattern = self._analyze_exercise_timing(
            user_id, glucose_data, exercise_data
        )
        if timing_pattern:
            patterns.append(timing_pattern)
        
        # Synthesize findings
        if not patterns:
            return "I need more data to find meaningful patterns. Keep logging for at least 7 days!"
        
        # Use LLM to create natural language summary
        analysis_text = "\n\n".join(patterns)
        
        prompt = f"""You are a health pattern analyst. Here are the patterns I found in the user's data:

{analysis_text}

Create a friendly, actionable summary that:
1. Highlights the most important patterns
2. Provides specific, personalized recommendations
3. Uses the user's actual data to be credible
4. Sounds encouraging and supportive

Keep it concise but impactful."""

        messages = [
            SystemMessage(content="You are a health data analyst providing personalized insights."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _analyze_exercise_glucose_correlation(self, user_id, glucose_data, exercise_data):
        """Find correlation between exercise and glucose levels."""
        if not exercise_data or len(exercise_data) < 3:
            return None
        
        # Convert to DataFrames
        glucose_df = pd.DataFrame(glucose_data)
        exercise_df = pd.DataFrame(exercise_data)
        
        glucose_df['timestamp'] = pd.to_datetime(glucose_df['timestamp'], format='mixed')
        exercise_df['timestamp'] = pd.to_datetime(exercise_df['timestamp'], format='mixed')
        
        # Get dates with and without exercise
        exercise_dates = exercise_df['timestamp'].dt.date.unique()
        glucose_df['date'] = glucose_df['timestamp'].dt.date
        
        # Calculate average glucose on exercise vs non-exercise days
        exercise_days_glucose = glucose_df[
            glucose_df['date'].isin(exercise_dates)
        ]['glucose_level'].mean()
        
        non_exercise_days_glucose = glucose_df[
            ~glucose_df['date'].isin(exercise_dates)
        ]['glucose_level'].mean()
        
        if pd.isna(exercise_days_glucose) or pd.isna(non_exercise_days_glucose):
            return None
        
        difference = non_exercise_days_glucose - exercise_days_glucose
        
        if abs(difference) > 10:  # Significant difference
            return f"""🏃 **Exercise-Glucose Correlation**:
Your glucose is {abs(difference):.0f} mg/dL {"lower" if difference > 0 else "higher"} on days you exercise.
- Exercise days: {exercise_days_glucose:.0f} mg/dL average
- Non-exercise days: {non_exercise_days_glucose:.0f} mg/dL average
- Pattern strength: {"Strong" if abs(difference) > 20 else "Moderate"}"""
        
        return None
    
    def _analyze_meal_glucose_correlation(self, user_id, glucose_data, meal_data):
        """Find which meals cause highest glucose spikes."""
        if not meal_data or len(meal_data) < 5:
            return None
        
        meal_df = pd.DataFrame(meal_data)
        glucose_df = pd.DataFrame(glucose_data)
        
        meal_df['timestamp'] = pd.to_datetime(meal_df['timestamp'], format='mixed')
        glucose_df['timestamp'] = pd.to_datetime(glucose_df['timestamp'], format='mixed')
        
        # For each meal, find glucose reading 1-2 hours later
        meal_impacts = []
        
        for _, meal in meal_df.iterrows():
            meal_time = meal['timestamp']
            # Look for glucose reading 1-2 hours after meal
            post_meal_readings = glucose_df[
                (glucose_df['timestamp'] > meal_time + timedelta(hours=1)) &
                (glucose_df['timestamp'] < meal_time + timedelta(hours=3))
            ]
            
            if not post_meal_readings.empty:
                avg_post_meal = post_meal_readings['glucose_level'].mean()
                meal_impacts.append({
                    'meal': meal['meal_name'],
                    'carbs': meal.get('carbs', 0),
                    'post_glucose': avg_post_meal
                })
        
        if len(meal_impacts) < 3:
            return None
        
        # Find meals with highest glucose response
        impacts_df = pd.DataFrame(meal_impacts)
        high_impact = impacts_df.nlargest(2, 'post_glucose')
        low_impact = impacts_df.nsmallest(2, 'post_glucose')
        
        high_meals = high_impact['meal'].tolist()
        low_meals = low_impact['meal'].tolist()
        
        return f"""🍽️ **Meal-Glucose Impact**:
Your glucose responds differently to different meals:
- Higher spikes: {', '.join(high_meals[:2])} (avg {high_impact['post_glucose'].mean():.0f} mg/dL)
- Lower spikes: {', '.join(low_meals[:2])} (avg {low_impact['post_glucose'].mean():.0f} mg/dL)
- Recommendation: Stick to meals similar to {low_meals[0]} for better control"""
    
    def _analyze_time_patterns(self, glucose_data):
        """Find time-of-day patterns in glucose levels."""
        if len(glucose_data) < 10:
            return None
        
        df = pd.DataFrame(glucose_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
        df['hour'] = df['timestamp'].dt.hour
        
        # Group by time periods
        morning = df[df['hour'].between(6, 11)]['glucose_level'].mean()
        afternoon = df[df['hour'].between(12, 17)]['glucose_level'].mean()
        evening = df[df['hour'].between(18, 23)]['glucose_level'].mean()
        
        times = {'Morning': morning, 'Afternoon': afternoon, 'Evening': evening}
        times = {k: v for k, v in times.items() if not pd.isna(v)}
        
        if not times:
            return None
        
        highest_time = max(times, key=times.get)
        lowest_time = min(times, key=times.get)
        
        difference = times[highest_time] - times[lowest_time]
        
        if difference > 20:
            return f"""⏰ **Time-of-Day Pattern**:
Your glucose varies by time of day:
- {highest_time}: {times[highest_time]:.0f} mg/dL (highest)
- {lowest_time}: {times[lowest_time]:.0f} mg/dL (lowest)
- Difference: {difference:.0f} mg/dL
- Focus on managing {highest_time.lower()} levels"""
        
        return None
    
    def _analyze_exercise_timing(self, user_id, glucose_data, exercise_data):
        """Find optimal exercise timing for glucose control."""
        if not exercise_data or len(exercise_data) < 3:
            return None
        
        glucose_df = pd.DataFrame(glucose_data)
        exercise_df = pd.DataFrame(exercise_data)
        
        glucose_df['timestamp'] = pd.to_datetime(glucose_df['timestamp'], format='mixed')
        exercise_df['timestamp'] = pd.to_datetime(exercise_df['timestamp'], format='mixed')
        exercise_df['hour'] = exercise_df['timestamp'].dt.hour
        
        # Categorize exercise times
        morning_exercises = exercise_df[exercise_df['hour'].between(5, 11)]
        evening_exercises = exercise_df[exercise_df['hour'].between(17, 21)]
        
        if morning_exercises.empty and evening_exercises.empty:
            return None
        
        # Find glucose on days with morning vs evening exercise
        if not morning_exercises.empty:
            morning_dates = morning_exercises['timestamp'].dt.date.unique()
            glucose_df['date'] = glucose_df['timestamp'].dt.date
            morning_glucose = glucose_df[
                glucose_df['date'].isin(morning_dates)
            ]['glucose_level'].mean()
        else:
            morning_glucose = None
        
        if not evening_exercises.empty:
            evening_dates = evening_exercises['timestamp'].dt.date.unique()
            glucose_df['date'] = glucose_df['timestamp'].dt.date
            evening_glucose = glucose_df[
                glucose_df['date'].isin(evening_dates)
            ]['glucose_level'].mean()
        else:
            evening_glucose = None
        
        if morning_glucose and evening_glucose and abs(morning_glucose - evening_glucose) > 15:
            better_time = "morning" if morning_glucose < evening_glucose else "evening"
            better_avg = min(morning_glucose, evening_glucose)
            worse_avg = max(morning_glucose, evening_glucose)
            
            return f"""🕐 **Exercise Timing Insight**:
Your {better_time} workouts show better results:
- {better_time.title()} exercise: {better_avg:.0f} mg/dL average glucose
- {"Evening" if better_time == "morning" else "Morning"} exercise: {worse_avg:.0f} mg/dL average
- Recommendation: Try exercising in the {better_time} more often"""
        
        return None
    
    def get_specific_insight(self, user_id: int, question: str) -> str:
        """
        Answer specific questions about patterns.
        """
        # Get all patterns
        patterns_text = self.analyze_patterns(user_id)
        
        prompt = f"""Based on this user's health patterns:

{patterns_text}

User's question: {question}

Provide a specific, actionable answer using their actual data. Be direct and helpful."""

        messages = [
            SystemMessage(content="You are a health analyst answering specific questions about user patterns."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


# Testing
if __name__ == "__main__":
    from database.db_manager import get_all_users
    
    print("Testing Pattern Analysis Agent...\n")
    
    users = get_all_users()
    if users:
        test_user = users[0]
        print(f"Analyzing patterns for: {test_user['name']}\n")
        
        agent = PatternAnalysisAgent()
        patterns = agent.analyze_patterns(test_user['id'])
        
        print("="*60)
        print("PATTERN ANALYSIS RESULTS")
        print("="*60)
        print(patterns)