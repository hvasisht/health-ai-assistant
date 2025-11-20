-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_demo BOOLEAN DEFAULT 0  -- 0 for real users, 1 for demo user
);

-- Glucose Readings Table
CREATE TABLE IF NOT EXISTS glucose_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    glucose_level REAL NOT NULL,  -- mg/dL
    notes TEXT,
    is_demo_data BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Meals Table
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    meal_name TEXT NOT NULL,
    meal_type TEXT,  -- breakfast, lunch, dinner, snack
    calories INTEGER,
    carbs REAL,  -- grams
    protein REAL,  -- grams
    fats REAL,  -- grams
    notes TEXT,
    is_demo_data BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Exercise Table
CREATE TABLE IF NOT EXISTS exercise (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    activity_type TEXT NOT NULL,  -- running, walking, yoga, etc.
    duration INTEGER NOT NULL,  -- minutes
    calories_burned INTEGER,
    intensity TEXT,  -- low, moderate, high
    notes TEXT,
    is_demo_data BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_glucose_user_time ON glucose_readings(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_meals_user_time ON meals(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_exercise_user_time ON exercise(user_id, timestamp);
