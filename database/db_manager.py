import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'health_data.db')

def get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def initialize_database():
    """Initialize the database with schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# ============= USER OPERATIONS =============

def create_user(name: str, is_demo: bool = False) -> int:
    """Create a new user and return their ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users (name, is_demo) VALUES (?, ?)",
        (name, 1 if is_demo else 0)
    )
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id

def get_user(user_id: int) -> Optional[Dict]:
    """Get user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

def get_all_users() -> List[Dict]:
    """Get all users."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()
    
    return [dict(user) for user in users]

# ============= GLUCOSE OPERATIONS =============

def add_glucose_reading(user_id: int, glucose_level: float, notes: str = "", is_demo: bool = False) -> int:
    """Add a glucose reading."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO glucose_readings (user_id, glucose_level, notes, is_demo_data)
           VALUES (?, ?, ?, ?)""",
        (user_id, glucose_level, notes, 1 if is_demo else 0)
    )
    
    reading_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return reading_id

def get_glucose_readings(user_id: int, limit: int = 10) -> List[Dict]:
    """Get recent glucose readings for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM glucose_readings 
           WHERE user_id = ? 
           ORDER BY timestamp DESC 
           LIMIT ?""",
        (user_id, limit)
    )
    
    readings = cursor.fetchall()
    conn.close()
    
    return [dict(reading) for reading in readings]

# ============= MEAL OPERATIONS =============

def add_meal(user_id: int, meal_name: str, meal_type: str = None, 
             calories: int = None, carbs: float = None, protein: float = None, 
             fats: float = None, notes: str = "", is_demo: bool = False) -> int:
    """Add a meal entry."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO meals (user_id, meal_name, meal_type, calories, carbs, protein, fats, notes, is_demo_data)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, meal_name, meal_type, calories, carbs, protein, fats, notes, 1 if is_demo else 0)
    )
    
    meal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return meal_id

def get_meals(user_id: int, limit: int = 10) -> List[Dict]:
    """Get recent meals for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM meals 
           WHERE user_id = ? 
           ORDER BY timestamp DESC 
           LIMIT ?""",
        (user_id, limit)
    )
    
    meals = cursor.fetchall()
    conn.close()
    
    return [dict(meal) for meal in meals]

# ============= EXERCISE OPERATIONS =============

def add_exercise(user_id: int, activity_type: str, duration: int, 
                 calories_burned: int = None, intensity: str = None, 
                 notes: str = "", is_demo: bool = False) -> int:
    """Add an exercise entry."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO exercise (user_id, activity_type, duration, calories_burned, intensity, notes, is_demo_data)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, activity_type, duration, calories_burned, intensity, notes, 1 if is_demo else 0)
    )
    
    exercise_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return exercise_id

def get_exercises(user_id: int, limit: int = 10) -> List[Dict]:
    """Get recent exercises for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM exercise 
           WHERE user_id = ? 
           ORDER BY timestamp DESC 
           LIMIT ?""",
        (user_id, limit)
    )
    
    exercises = cursor.fetchall()
    conn.close()
    
    return [dict(exercise) for exercise in exercises]

# ============= ANALYTICS =============

def get_glucose_stats(user_id: int, days: int = 7) -> Dict:
    """Get glucose statistics for the last N days."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT 
               AVG(glucose_level) as avg_glucose,
               MIN(glucose_level) as min_glucose,
               MAX(glucose_level) as max_glucose,
               COUNT(*) as reading_count
           FROM glucose_readings 
           WHERE user_id = ? 
           AND timestamp >= datetime('now', '-' || ? || ' days')""",
        (user_id, days)
    )
    
    stats = cursor.fetchone()
    conn.close()
    
    return dict(stats) if stats else {}

if __name__ == "__main__":
    # Test database initialization
    initialize_database()
