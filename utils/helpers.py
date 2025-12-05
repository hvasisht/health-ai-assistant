"""
Helper utility functions for the Health AI Assistant.
Functions for parsing user input, formatting data, and other common tasks.
"""

"""
Helper utility functions for the Health AI Assistant.
Functions for parsing user input, formatting data, and other common tasks.
"""

import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import streamlit as st

def get_openai_key():
    """Get OpenAI API key from environment or Streamlit secrets."""
    # Try Streamlit secrets first (for deployment)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        # Fall back to environment variable (for local)
        return os.getenv("OPENAI_API_KEY")

# ============= INPUT PARSING =============

def parse_glucose_input(user_message: str) -> Optional[float]:
    """
    Extract glucose reading from user message.
    Examples: "Log glucose: 120", "My blood sugar is 135", "150 mg/dL"
    """
    # Look for numbers between 50-400 (reasonable glucose range)
    patterns = [
        r'(\d{2,3})\s*(?:mg/dl|mg/dL|mgdl)?',  # "120 mg/dL" or "120"
        r'glucose[:\s]+(\d{2,3})',              # "glucose: 120"
        r'blood sugar[:\s]+(\d{2,3})',          # "blood sugar: 120"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            if 50 <= value <= 400:  # Reasonable range
                return value
    
    return None

def parse_meal_input(user_message: str) -> Optional[str]:
    """
    Extract meal name from user message.
    Examples: "I ate chicken salad", "Log meal: oatmeal", "Had pizza for lunch"
    """
    # Remove common prefixes
    message = user_message.lower()
    
    prefixes = [
        'i ate ', 'i had ', 'i just ate ', 'i just had ',
        'log meal: ', 'log meal ', 'ate ', 'had ',
        'meal: ', 'for breakfast ', 'for lunch ', 'for dinner '
    ]
    
    for prefix in prefixes:
        if prefix in message:
            meal = message.split(prefix, 1)[1].strip()
            # Remove trailing punctuation
            meal = meal.rstrip('.,!?')
            return meal
    
    return None

def parse_exercise_input(user_message: str) -> Optional[Tuple[str, int]]:
    """
    Extract exercise type and duration from user message.
    Examples: "I ran for 30 minutes", "30 min walk", "Yoga 45 minutes"
    Returns: (activity_type, duration_minutes)
    """
    message = user_message.lower()
    
    # Look for duration
    duration_patterns = [
        r'(\d+)\s*(?:min|minute|minutes)',
        r'for\s*(\d+)\s*(?:min|minute|minutes)',
    ]
    
    duration = None
    for pattern in duration_patterns:
        match = re.search(pattern, message)
        if match:
            duration = int(match.group(1))
            break
    
    # Look for activity type
    activities = [
        'run', 'running', 'jog', 'jogging',
        'walk', 'walking',
        'yoga', 'pilates',
        'swim', 'swimming',
        'bike', 'biking', 'cycling',
        'gym', 'workout', 'exercise',
        'strength', 'weights', 'lifting'
    ]
    
    activity = None
    for act in activities:
        if act in message:
            activity = act
            break
    
    if activity and duration:
        return (activity, duration)
    
    return None

def estimate_meal_calories(meal_name: str) -> Dict[str, float]:
    """
    Provide rough estimates for common meals.
    Returns: {calories, carbs, protein, fats}
    """
    meal = meal_name.lower()
    
    # Simple estimation based on keywords
    estimates = {
        'salad': {'calories': 200, 'carbs': 15, 'protein': 10, 'fats': 10},
        'chicken': {'calories': 350, 'carbs': 5, 'protein': 40, 'fats': 15},
        'oatmeal': {'calories': 300, 'carbs': 50, 'protein': 10, 'fats': 6},
        'eggs': {'calories': 150, 'carbs': 2, 'protein': 12, 'fats': 10},
        'yogurt': {'calories': 150, 'carbs': 20, 'protein': 10, 'fats': 3},
        'sandwich': {'calories': 400, 'carbs': 45, 'protein': 20, 'fats': 15},
        'pizza': {'calories': 500, 'carbs': 60, 'protein': 20, 'fats': 20},
        'pasta': {'calories': 450, 'carbs': 70, 'protein': 15, 'fats': 10},
        'rice': {'calories': 350, 'carbs': 75, 'protein': 7, 'fats': 1},
        'burger': {'calories': 600, 'carbs': 45, 'protein': 30, 'fats': 30},
    }
    
    # Check for keywords in meal name
    for keyword, values in estimates.items():
        if keyword in meal:
            return values
    
    # Default if no match
    return {'calories': 300, 'carbs': 40, 'protein': 15, 'fats': 10}

def estimate_exercise_calories(activity: str, duration: int) -> int:
    """
    Estimate calories burned based on activity and duration.
    Returns: estimated calories burned
    """
    # Calories per minute (rough estimates for average person)
    calorie_rates = {
        'run': 10,
        'running': 10,
        'jog': 8,
        'jogging': 8,
        'walk': 4,
        'walking': 4,
        'yoga': 3,
        'swim': 9,
        'swimming': 9,
        'bike': 8,
        'biking': 8,
        'cycling': 8,
        'strength': 5,
        'weights': 5,
        'gym': 6,
        'workout': 6,
    }
    
    rate = calorie_rates.get(activity.lower(), 5)  # Default 5 cal/min
    return rate * duration

# ============= DATA FORMATTING =============

def format_glucose_data(readings: List[Dict]) -> str:
    """Format glucose readings for display to AI agent."""
    if not readings:
        return "No recent glucose readings."
    
    formatted = "Recent glucose readings:\n"
    for reading in readings[:5]:  # Show last 5
        timestamp = reading['timestamp']
        level = reading['glucose_level']
        formatted += f"- {timestamp}: {level} mg/dL\n"
    
    return formatted

def format_meal_data(meals: List[Dict]) -> str:
    """Format meal data for display to AI agent."""
    if not meals:
        return "No recent meals logged."
    
    formatted = "Recent meals:\n"
    for meal in meals[:5]:  # Show last 5
        timestamp = meal['timestamp']
        name = meal['meal_name']
        cals = meal.get('calories', 'N/A')
        formatted += f"- {timestamp}: {name} ({cals} cal)\n"
    
    return formatted

def format_exercise_data(exercises: List[Dict]) -> str:
    """Format exercise data for display to AI agent."""
    if not exercises:
        return "No recent exercise logged."
    
    formatted = "Recent exercise:\n"
    for exercise in exercises[:5]:  # Show last 5
        timestamp = exercise['timestamp']
        activity = exercise['activity_type']
        duration = exercise['duration']
        formatted += f"- {timestamp}: {activity} for {duration} min\n"
    
    return formatted

def get_glucose_status(level: float) -> Tuple[str, str]:
    """
    Get status and color for glucose level (ADA guidelines).
    Returns: (status_text, color)
    """
    if level < 70:
        return ("🔴 Too Low - Hypoglycemia Risk", "red")
    elif level < 80:
        return ("⚠️ Low - Monitor Closely", "orange")
    elif level <= 130:
        return ("✅ Normal (Before Meal Range)", "green")
    elif level <= 180:
        return ("✅ Good (After Meal Range)", "green")
    elif level <= 250:
        return ("⚠️ High - Take Action", "orange")
    else:
        return ("🔴 Very High - Seek Medical Advice", "red")

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for better display."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%b %d, %I:%M %p")  # "Nov 14, 02:30 PM"
    except:
        return timestamp_str

# ============= VALIDATION =============

def is_valid_glucose(value: float) -> bool:
    """Check if glucose value is in reasonable range."""
    return 20 <= value <= 600  # Extreme but possible range

def is_valid_duration(minutes: int) -> bool:
    """Check if exercise duration is reasonable."""
    return 1 <= minutes <= 480  # Max 8 hours

def is_valid_calories(calories: int) -> bool:
    """Check if calorie count is reasonable."""
    return 1 <= calories <= 5000  # Per meal