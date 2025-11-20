"""
Generate realistic demo data with timestamps spread across 7 different days.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import initialize_database, create_user, get_connection
from datetime import datetime, timedelta
import random

def generate_demo_data():
    print("🎬 Generating demo data...\n")
    initialize_database()
    
    print("Creating demo user 'Sarah'...")
    demo_user_id = create_user("Sarah (Demo)", is_demo=True)
    print(f"✅ Created demo user ID: {demo_user_id}\n")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Generate for EACH of the last 7 days
    for days_ago in range(6, -1, -1):  # 6 days ago to today
        current_date = datetime.now() - timedelta(days=days_ago)
        date_str = current_date.strftime('%Y-%m-%d')
        
        print(f"✓ Generating data for {date_str}")
        
        # Glucose readings for this day
        morning_glucose = random.randint(95, 125)
        morning_time = current_date.replace(hour=7, minute=15, second=0, microsecond=0)
        cursor.execute(
            "INSERT INTO glucose_readings (user_id, timestamp, glucose_level, notes, is_demo_data) VALUES (?, ?, ?, ?, 1)",
            (demo_user_id, morning_time, morning_glucose, "Morning")
        )
        
        post_breakfast = random.randint(130, 160)
        breakfast_time = current_date.replace(hour=9, minute=30, second=0, microsecond=0)
        cursor.execute(
            "INSERT INTO glucose_readings (user_id, timestamp, glucose_level, notes, is_demo_data) VALUES (?, ?, ?, ?, 1)",
            (demo_user_id, breakfast_time, post_breakfast, "After breakfast")
        )
        
        post_lunch = random.randint(140, 170)
        lunch_time = current_date.replace(hour=14, minute=0, second=0, microsecond=0)
        cursor.execute(
            "INSERT INTO glucose_readings (user_id, timestamp, glucose_level, notes, is_demo_data) VALUES (?, ?, ?, ?, 1)",
            (demo_user_id, lunch_time, post_lunch, "After lunch")
        )
        
        evening = random.randint(110, 140)
        evening_time = current_date.replace(hour=21, minute=0, second=0, microsecond=0)
        cursor.execute(
            "INSERT INTO glucose_readings (user_id, timestamp, glucose_level, notes, is_demo_data) VALUES (?, ?, ?, ?, 1)",
            (demo_user_id, evening_time, evening, "Evening")
        )
        
        # Meals
        cursor.execute(
            "INSERT INTO meals (user_id, timestamp, meal_name, meal_type, calories, carbs, protein, fats, is_demo_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (demo_user_id, current_date.replace(hour=7, minute=30), "Oatmeal with berries", "breakfast", 320, 48, 12, 8)
        )
        cursor.execute(
            "INSERT INTO meals (user_id, timestamp, meal_name, meal_type, calories, carbs, protein, fats, is_demo_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (demo_user_id, current_date.replace(hour=12, minute=30), "Chicken salad", "lunch", 420, 18, 35, 22)
        )
        cursor.execute(
            "INSERT INTO meals (user_id, timestamp, meal_name, meal_type, calories, carbs, protein, fats, is_demo_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (demo_user_id, current_date.replace(hour=19, minute=0), "Salmon with vegetables", "dinner", 520, 28, 42, 24)
        )
        
        # Exercise (skip days 2 and 6 - rest days)
        if days_ago not in [2, 6]:
            exercises = [
                ("running", 45), ("yoga", 40), ("running", 30), 
                ("strength training", 35), ("cycling", 50)
            ]
            exercise = exercises[days_ago % 5]
            exercise_time = current_date.replace(hour=17, minute=30, second=0, microsecond=0)
            calories = exercise[1] * 8
            cursor.execute(
                "INSERT INTO exercise (user_id, timestamp, activity_type, duration, calories_burned, intensity, is_demo_data) VALUES (?, ?, ?, ?, ?, ?, 1)",
                (demo_user_id, exercise_time, exercise[0], exercise[1], calories, "moderate")
            )
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ DEMO DATA COMPLETE - 7 DAYS OF DATA CREATED!")
    print("="*60)
    print(f"📊 User ID: {demo_user_id}")
    print(f"📅 Date range: Last 7 days")
    print("👉 Refresh the app and login as 'Sarah (Demo)'")
    print("="*60)

if __name__ == "__main__":
    generate_demo_data()