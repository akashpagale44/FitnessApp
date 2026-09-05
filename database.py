import sqlite3
from pathlib import Path


# Database location
DATABASE_PATH = Path("data") / "fitness.db"


def get_connection():
    """Create and return a database connection."""
    DATABASE_PATH.parent.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def create_database():
    """Create all required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------
    # Users table
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            goal_weight REAL,
            fitness_goal TEXT,
            activity_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # Daily nutrition table
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nutrition_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            food_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            calories REAL DEFAULT 0,
            protein REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fats REAL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # -------------------------
    # Workout logs table
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # -------------------------
    # Weight progress table
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            weight REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def save_user(
    name,
    age,
    gender,
    height,
    weight,
    goal_weight,
    fitness_goal,
    activity_level
):
    """Save a new user and return the user's ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (
            name,
            age,
            gender,
            height,
            weight,
            goal_weight,
            fitness_goal,
            activity_level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        gender,
        height,
        weight,
        goal_weight,
        fitness_goal,
        activity_level
    ))

    user_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return user_id


def get_user(user_id):
    """Get a user by ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()

    connection.close()

    return user


def get_today_workout_count(user_id):
    """Get the number of workouts logged today."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM workout_logs
        WHERE user_id = ?
        AND date = DATE('now')
    """, (user_id,))

    count = cursor.fetchone()[0]

    connection.close()

    return count

def get_food(food_name):
    """Get nutrition information for a food."""

    foods = {
        "egg": {
            "calories": 155,
            "protein": 13,
            "carbs": 1,
            "fats": 11
        },
        "rice": {
            "calories": 130,
            "protein": 2.7,
            "carbs": 28,
            "fats": 0.3
        },
        "chicken breast": {
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fats": 3.6
        },
        "milk": {
            "calories": 61,
            "protein": 3.2,
            "carbs": 4.8,
            "fats": 3.3
        },
        "oats": {
            "calories": 389,
            "protein": 16.9,
            "carbs": 66,
            "fats": 6.9
        },
        "banana": {
            "calories": 89,
            "protein": 1.1,
            "carbs": 23,
            "fats": 0.3
        }
    }

    return foods.get(food_name.lower())

    return foods.get(food_name.lower())


def save_nutrition_log(
    user_id,
    food_name,
    quantity,
    calories,
    protein,
    carbs,
    fats
):
    """Save a food entry to the nutrition log."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO nutrition_logs (
            user_id,
            date,
            food_name,
            quantity,
            calories,
            protein,
            carbs,
            fats
        )
        VALUES (
            ?, DATE('now'), ?, ?, ?, ?, ?, ?
        )
    """, (
        user_id,
        food_name,
        quantity,
        calories,
        protein,
        carbs,
        fats
    ))

    connection.commit()
    connection.close()

def save_workout_log(
    user_id,
    exercise_name,
    sets,
    reps,
    weight,
    notes
):
    """Save a workout entry."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO workout_logs (
            user_id,
            date,
            exercise_name,
            sets,
            reps,
            weight,
            notes
        )
        VALUES (
            ?, DATE('now'), ?, ?, ?, ?, ?
        )
    """, (
        user_id,
        exercise_name,
        sets,
        reps,
        weight,
        notes
    ))

    connection.commit()
    connection.close()