
import sqlite3
from pathlib import Path


# ============================================================
# DATABASE LOCATION AND CONNECTION
# ============================================================

DATABASE_PATH = Path(__file__).resolve().parent / "data" / "fitness.db"


def get_connection():
    """Connect to Turso when configured; otherwise use local SQLite."""
    try:
        import streamlit as st
        turso_url = st.secrets["TURSO_DATABASE_URL"]
        turso_token = st.secrets["TURSO_AUTH_TOKEN"]
    except (ImportError, KeyError, FileNotFoundError):
        turso_url = None
        turso_token = None

    if turso_url and turso_token:
        import turso_serverless

        connection = turso_serverless.connect(
            turso_url,
            auth_token=turso_token
        )
        class CompatibleRow(turso_serverless.Row):
            def get(self, key, default=None):
                try:
                    return self[key]
                except KeyError:
                    return default

        connection.row_factory = CompatibleRow
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# ============================================================
# CREATE AND INITIALIZE DATABASE
# ============================================================

def create_database():
    """Create all existing and expanded database tables."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # ---------------- USERS ----------------

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

        # ---------------- USER ACCOUNT MIGRATION ----------------

        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {
            column["name"] for column in cursor.fetchall()
        }

        if "email" not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")

        if "password_hash" not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique
            ON users(LOWER(email))
            WHERE email IS NOT NULL AND TRIM(email) != ''
        """)

        # ---------------- PERSISTENT LOGIN SESSIONS ----------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id
            ON auth_sessions(user_id)
        """)

        # ---------------- NUTRITION LOGS ----------------

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

        # ---------------- WORKOUT LOGS ----------------

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

        # ---------------- WEIGHT LOGS ----------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                weight REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ---------------- QUIZ LOGS ----------------
        # Preserves the existing quiz history table.

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                score INTEGER,
                total_questions INTEGER,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ====================================================
        # EXPANDED FOOD DATABASE
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                brand TEXT,
                variant TEXT,
                measurement_unit TEXT NOT NULL DEFAULT 'g',
                calories REAL NOT NULL DEFAULT 0,
                protein REAL NOT NULL DEFAULT 0,
                carbs REAL NOT NULL DEFAULT 0,
                fats REAL NOT NULL DEFAULT 0,
                food_state TEXT NOT NULL DEFAULT 'standard',
                data_source TEXT,
                is_approximate INTEGER NOT NULL DEFAULT 1,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (category_id)
                    REFERENCES food_categories(id)
            )
        """)

        # ====================================================
        # EXPANDED EXERCISE DATABASE
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS muscle_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                equipment TEXT NOT NULL DEFAULT 'Other',
                difficulty TEXT NOT NULL DEFAULT 'Beginner',
                recommended_sets INTEGER DEFAULT 3,
                rep_range TEXT,
                hold_seconds INTEGER,
                description TEXT,
                instructions TEXT,
                common_mistakes TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_muscles (
                exercise_id INTEGER NOT NULL,
                muscle_group_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'primary',

                PRIMARY KEY (exercise_id, muscle_group_id),

                FOREIGN KEY (exercise_id)
                    REFERENCES exercises(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (muscle_group_id)
                    REFERENCES muscle_groups(id)
                    ON DELETE CASCADE,

                CHECK (role IN ('primary', 'secondary'))
            )
        """)

        # ---------------- INDEXES ----------------

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nutrition_user_date
            ON nutrition_logs(user_id, date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_workout_user_date
            ON workout_logs(user_id, date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_foods_name
            ON foods(name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_foods_category
            ON foods(category_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exercises_name
            ON exercises(name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exercise_muscles_muscle
            ON exercise_muscles(muscle_group_id)
        """)

        # ---------------- FOOD CATEGORIES ----------------

        categories = [
            ("Dairy", "Milk and dairy products"),
            ("Eggs", "Eggs and egg products"),
            ("Meat and Fish", "Chicken, meat and seafood"),
            ("Grains and Cereals", "Rice, oats and wheat products"),
            ("Pulses and Legumes", "Dal, beans and legumes"),
            ("Fruits", "Fresh and dried fruits"),
            ("Vegetables", "Vegetables and tubers"),
            ("Nuts and Seeds", "Nuts and seeds"),
            ("Other", "Other foods and ingredients")
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO food_categories
            (name, description)
            VALUES (?, ?)
        """, categories)

        # ---------------- MUSCLE GROUPS ----------------

        muscles = [
            "Chest", "Back", "Shoulders", "Biceps",
            "Triceps", "Forearms", "Abdominals", "Obliques",
            "Quadriceps", "Hamstrings", "Glutes", "Calves",
            "Traps", "Lower Back"
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO muscle_groups (name)
            VALUES (?)
        """, [(muscle,) for muscle in muscles])

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# USER FUNCTIONS
# ============================================================

def save_user(
    name, age, gender, height, weight,
    goal_weight, fitness_goal, activity_level
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (
                name, age, gender, height, weight,
                goal_weight, fitness_goal, activity_level
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, age, gender, height, weight,
            goal_weight, fitness_goal, activity_level
        ))

        user_id = cursor.lastrowid
        connection.commit()

        return user_id

    finally:
        connection.close()


def get_user(user_id):
    connection = get_connection()

    try:
        return connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    finally:
        connection.close()


# ============================================================


# ============================================================
# USER ACCOUNT FUNCTIONS
# ============================================================

def _create_password_hash(password):
    import hashlib
    import secrets

    iterations = 600000
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations
    )

    return (
        f"pbkdf2_sha256${iterations}"
        f"${salt.hex()}${password_hash.hex()}"
    )


def _verify_password(password, stored_hash):
    import hashlib
    import hmac

    try:
        algorithm, iterations, salt_hex, hash_hex = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations)
        )

        return hmac.compare_digest(
            calculated_hash.hex(),
            hash_hex
        )

    except (ValueError, TypeError, AttributeError):
        return False


def get_user_by_email(email):
    connection = get_connection()

    try:
        return connection.execute(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?)",
            (email.strip(),)
        ).fetchone()

    finally:
        connection.close()


def set_user_credentials(user_id, email, password):
    if not email or not email.strip() or "@" not in email:
        raise ValueError("Enter a valid email address.")

    if not password or len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    email = email.strip().lower()
    password_hash = _create_password_hash(password)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        existing_email = cursor.execute(
            "SELECT id FROM users WHERE LOWER(email) = LOWER(?)",
            (email,)
        ).fetchone()

        if existing_email:
            raise ValueError("This email is already registered.")

        cursor.execute("""
            UPDATE users
            SET email = ?, password_hash = ?
            WHERE id = ?
              AND email IS NULL
              AND password_hash IS NULL
        """, (email, password_hash, user_id))

        if cursor.rowcount != 1:
            raise ValueError(
                "This profile cannot be linked. It may already have login credentials."
            )

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def register_user(
    name, email, password,
    age=None, gender=None, height=None, weight=None,
    goal_weight=None, fitness_goal=None, activity_level=None
):
    if not name or not name.strip():
        raise ValueError("Name is required.")

    if not email or not email.strip() or "@" not in email:
        raise ValueError("Enter a valid email address.")

    if not password or len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    email = email.strip().lower()
    password_hash = _create_password_hash(password)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (
                name, age, gender, height, weight,
                goal_weight, fitness_goal, activity_level,
                email, password_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name.strip(), age, gender, height, weight,
            goal_weight, fitness_goal, activity_level,
            email, password_hash
        ))

        user_id = cursor.lastrowid
        connection.commit()
        return user_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def authenticate_user(email, password):
    if not email or not password:
        print("LOGIN_DIAG: credentials_supplied=False")
        return None

    user = get_user_by_email(email.strip())
    user_found = user is not None
    hash_present = bool(user and user["password_hash"])
    password_match = bool(
        hash_present and _verify_password(password, user["password_hash"])
    )

    print(
        f"LOGIN_DIAG: user_found={user_found}, "
        f"hash_present={hash_present}, password_match={password_match}"
    )
    return user if password_match else None

# PERSISTENT LOGIN SESSION FUNCTIONS
# ============================================================

def create_auth_session(user_id, duration_days=7):
    """Create a random session token and store only its SHA-256 hash."""
    import hashlib
    import secrets
    import time

    if not user_id or duration_days <= 0:
        raise ValueError("A valid user and session duration are required.")

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = int(time.time() + duration_days * 24 * 60 * 60)

    connection = get_connection()

    try:
        connection.execute(
            "DELETE FROM auth_sessions WHERE expires_at <= ?",
            (int(time.time()),)
        )

        connection.execute("""
            INSERT INTO auth_sessions (token_hash, user_id, expires_at)
            VALUES (?, ?, ?)
        """, (token_hash, user_id, expires_at))

        connection.commit()
        return token

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_user_by_session_token(token):
    """Return the user for a valid, unexpired session token."""
    import hashlib

    if not token:
        return None

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    connection = get_connection()

    try:
        return connection.execute("""
            SELECT users.*
            FROM users
            INNER JOIN auth_sessions
                ON users.id = auth_sessions.user_id
            WHERE auth_sessions.token_hash = ?
              AND auth_sessions.expires_at > strftime('%s', 'now')
        """, (token_hash,)).fetchone()

    finally:
        connection.close()


def revoke_auth_session(token):
    """Revoke a session token without affecting other user data."""
    import hashlib

    if not token:
        return

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    connection = get_connection()

    try:
        connection.execute(
            "DELETE FROM auth_sessions WHERE token_hash = ?",
            (token_hash,)
        )
        connection.commit()

    finally:
        connection.close()


# WORKOUT LOG FUNCTIONS
# ============================================================

def get_today_workout_count(user_id):
    connection = get_connection()

    try:
        result = connection.execute("""
            SELECT COUNT(*)
            FROM workout_logs
            WHERE user_id = ?
            AND date = DATE('now')
        """, (user_id,)).fetchone()

        return result[0]

    finally:
        connection.close()


def save_workout_log(
    user_id, exercise_name, sets, reps, weight, notes
):
    connection = get_connection()

    try:
        connection.execute("""
            INSERT INTO workout_logs (
                user_id, date, exercise_name,
                sets, reps, weight, notes
            )
            VALUES (?, DATE('now'), ?, ?, ?, ?, ?)
        """, (
            user_id, exercise_name, sets,
            reps, weight, notes
        ))

        connection.commit()

    finally:
        connection.close()


# ============================================================
# EXISTING FOOD NUTRITION DATABASE
# Approximate values per 100 g
# ============================================================

def get_food(food_name, measurement_type="standard"):

    foods = {
        "egg": {
            "calories": 155, "protein": 13,
            "carbs": 1.1, "fats": 11
        },
        "boiled egg": {
            "calories": 155, "protein": 13,
            "carbs": 1.1, "fats": 11
        },
        "rice": {
            "raw": {
                "calories": 365, "protein": 7.1,
                "carbs": 80, "fats": 0.7
            },
            "cooked": {
                "calories": 130, "protein": 2.7,
                "carbs": 28, "fats": 0.3
            },
            "standard": {
                "calories": 130, "protein": 2.7,
                "carbs": 28, "fats": 0.3
            }
        },
        "chicken breast": {
            "raw": {
                "calories": 120, "protein": 22.5,
                "carbs": 0, "fats": 2.6
            },
            "cooked": {
                "calories": 165, "protein": 31,
                "carbs": 0, "fats": 3.6
            },
            "standard": {
                "calories": 165, "protein": 31,
                "carbs": 0, "fats": 3.6
            }
        },
        "milk": {
            "calories": 61, "protein": 3.2,
            "carbs": 4.8, "fats": 3.3
        },
        "oats": {
            "calories": 389, "protein": 16.9,
            "carbs": 66.3, "fats": 6.9
        },
        "banana": {
            "calories": 89, "protein": 1.1,
            "carbs": 22.8, "fats": 0.3
        },
        "apple": {
            "calories": 52, "protein": 0.3,
            "carbs": 13.8, "fats": 0.2
        },
        "orange": {
            "calories": 47, "protein": 0.9,
            "carbs": 11.8, "fats": 0.1
        },
        "chapati": {
            "calories": 297, "protein": 8.5,
            "carbs": 50, "fats": 7
        },
        "potato": {
            "calories": 87, "protein": 1.9,
            "carbs": 20.1, "fats": 0.1
        },
        "sweet potato": {
            "calories": 86, "protein": 1.6,
            "carbs": 20.1, "fats": 0.1
        },
        "paneer": {
            "calories": 265, "protein": 18.3,
            "carbs": 1.2, "fats": 20.8
        },
        "curd": {
            "calories": 61, "protein": 3.5,
            "carbs": 4.7, "fats": 3.3
        },
        "dal": {
            "calories": 116, "protein": 9,
            "carbs": 20, "fats": 0.4
        },
        "cooked moong dal": {
            "calories": 105, "protein": 7,
            "carbs": 19, "fats": 0.4
        },
        "moong dal": {
            "calories": 347, "protein": 24,
            "carbs": 63, "fats": 1.2
        },
        "soya chunks": {
            "calories": 345, "protein": 52,
            "carbs": 33, "fats": 0.5
        },
        "roasted chana": {
            "calories": 369, "protein": 22,
            "carbs": 63, "fats": 5
        },
        "besan": {
            "calories": 387, "protein": 22,
            "carbs": 58, "fats": 7
        },
        "peanuts": {
            "calories": 567, "protein": 25.8,
            "carbs": 16.1, "fats": 49.2
        },
        "dates": {
            "calories": 282, "protein": 2.5,
            "carbs": 75, "fats": 0.4
        },
        "poha": {
            "calories": 130, "protein": 2.5,
            "carbs": 28, "fats": 1
        },
        "idli": {
            "calories": 150, "protein": 4,
            "carbs": 30, "fats": 1
        },
        "dosa": {
            "calories": 168, "protein": 4,
            "carbs": 29, "fats": 4
        },
        "upma": {
            "calories": 150, "protein": 4,
            "carbs": 24, "fats": 5
        },
        "bajra flour": {
            "calories": 361, "protein": 11.6,
            "carbs": 67.5, "fats": 5
        },
        "whole wheat flour": {
            "calories": 340, "protein": 13.2,
            "carbs": 72, "fats": 2.5
        },
        "chickpeas": {
            "calories": 364, "protein": 19.3,
            "carbs": 60.7, "fats": 6
        },
        "cooked chickpeas": {
            "calories": 164, "protein": 8.9,
            "carbs": 27.4, "fats": 2.6
        },
        "rajma": {
            "calories": 127, "protein": 8.7,
            "carbs": 22.8, "fats": 0.5
        },
        "tomato": {
            "calories": 18, "protein": 0.9,
            "carbs": 3.9, "fats": 0.2
        },
        "cucumber": {
            "calories": 15, "protein": 0.7,
            "carbs": 3.6, "fats": 0.1
        },
        "carrot": {
            "calories": 41, "protein": 0.9,
            "carbs": 9.6, "fats": 0.2
        },
        "almonds": {
            "calories": 579, "protein": 21.2,
            "carbs": 21.6, "fats": 49.9
        },
        "sweet corn": {
            "calories": 96, "protein": 3.4,
            "carbs": 21, "fats": 1.5
        },
        "sugar": {
            "calories": 387, "protein": 0,
            "carbs": 100, "fats": 0
        }
    }

    key = food_name.strip().lower()
    food = foods.get(key)

    if food is None:
        return None

    if "calories" in food:
        return food

    return food.get(
        measurement_type.lower(),
        food.get("standard")
    )


# ============================================================
# EXPANDED FOOD LIBRARY FUNCTIONS
# ============================================================

def add_food(
    name,
    category,
    calories,
    protein,
    carbs,
    fats,
    measurement_unit="g",
    brand=None,
    variant=None,
    food_state="standard",
    data_source="User supplied",
    is_approximate=1
):
    """Add a food to the expanded food library."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO food_categories (name)
            VALUES (?)
            ON CONFLICT(name) DO NOTHING
        """, (category,))

        category_id = cursor.execute("""
            SELECT id FROM food_categories WHERE name = ?
        """, (category,)).fetchone()["id"]

        cursor.execute("""
            INSERT INTO foods (
                name, category_id, brand, variant,
                measurement_unit, calories, protein,
                carbs, fats, food_state, data_source,
                is_approximate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, category_id, brand, variant,
            measurement_unit, calories, protein,
            carbs, fats, food_state, data_source,
            is_approximate
        ))

        connection.commit()
        return cursor.lastrowid

    finally:
        connection.close()


def get_food_library():
    """Get all active foods from the expanded food library."""

    connection = get_connection()

    try:
        return connection.execute("""
            SELECT
                foods.*,
                food_categories.name AS category
            FROM foods
            LEFT JOIN food_categories
                ON foods.category_id = food_categories.id
            WHERE foods.is_active = 1
            ORDER BY foods.name
        """).fetchall()

    finally:
        connection.close()


def search_foods(search_term):
    """Search the expanded food library by name."""

    connection = get_connection()

    try:
        return connection.execute("""
            SELECT foods.*, food_categories.name AS category
            FROM foods
            LEFT JOIN food_categories
                ON foods.category_id = food_categories.id
            WHERE foods.is_active = 1
            AND foods.name LIKE ?
            ORDER BY foods.name
        """, (f"%{search_term}%",)).fetchall()

    finally:
        connection.close()


# ============================================================
# EXPANDED EXERCISE LIBRARY FUNCTIONS
# ============================================================

def add_exercise(
    name,
    equipment="Other",
    difficulty="Beginner",
    recommended_sets=3,
    rep_range=None,
    hold_seconds=None,
    description=None,
    instructions=None,
    common_mistakes=None,
    primary_muscles=None,
    secondary_muscles=None
):
    """Add an exercise and its muscle relationships."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO exercises (
                name, equipment, difficulty,
                recommended_sets, rep_range,
                hold_seconds, description,
                instructions, common_mistakes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, equipment, difficulty,
            recommended_sets, rep_range,
            hold_seconds, description,
            instructions, common_mistakes
        ))

        exercise = cursor.execute("""
            SELECT id FROM exercises WHERE name = ?
        """, (name,)).fetchone()

        exercise_id = exercise["id"]

        for muscle_name, role in (
            [(m, "primary") for m in (primary_muscles or [])]
            + [(m, "secondary") for m in (secondary_muscles or [])]
        ):
            cursor.execute("""
                INSERT OR IGNORE INTO muscle_groups (name)
                VALUES (?)
            """, (muscle_name,))

            muscle_id = cursor.execute("""
                SELECT id FROM muscle_groups WHERE name = ?
            """, (muscle_name,)).fetchone()["id"]

            cursor.execute("""
                INSERT OR IGNORE INTO exercise_muscles (
                    exercise_id, muscle_group_id, role
                )
                VALUES (?, ?, ?)
            """, (exercise_id, muscle_id, role))

        connection.commit()
        return exercise_id

    finally:
        connection.close()


def get_exercise_library():
    """Get all active exercises."""

    connection = get_connection()

    try:
        return connection.execute("""
            SELECT *
            FROM exercises
            WHERE is_active = 1
            ORDER BY name
        """).fetchall()

    finally:
        connection.close()


def search_exercises(search_term):
    """Search exercises by name or equipment."""

    connection = get_connection()

    try:
        return connection.execute("""
            SELECT *
            FROM exercises
            WHERE is_active = 1
            AND (
                name LIKE ?
                OR equipment LIKE ?
            )
            ORDER BY name
        """, (
            f"%{search_term}%",
            f"%{search_term}%"
        )).fetchall()

    finally:
        connection.close()



def get_all_exercise_muscles():
    """Get muscle relationships for all exercises in one query."""
    connection = get_connection()

    try:
        return connection.execute("""
            SELECT
                exercise_muscles.exercise_id,
                muscle_groups.name,
                exercise_muscles.role
            FROM exercise_muscles
            JOIN muscle_groups
                ON exercise_muscles.muscle_group_id = muscle_groups.id
            ORDER BY exercise_muscles.role
        """).fetchall()

    finally:
        connection.close()

def get_exercise_muscles(exercise_id):
    """Get primary and secondary muscles for an exercise."""

    connection = get_connection()

    try:
        return connection.execute("""
            SELECT
                muscle_groups.name,
                exercise_muscles.role
            FROM exercise_muscles
            JOIN muscle_groups
                ON exercise_muscles.muscle_group_id = muscle_groups.id
            WHERE exercise_muscles.exercise_id = ?
            ORDER BY exercise_muscles.role
        """, (exercise_id,)).fetchall()

    finally:
        connection.close()


# ============================================================
# NUTRITION LOGGING
# ============================================================

def save_nutrition_log(
    user_id,
    food_name,
    quantity,
    calories,
    protein,
    carbs,
    fats,
    fibre=None
):
    """Save a food entry to the nutrition log."""

    connection = get_connection()

    try:
        connection.execute("""
            INSERT INTO nutrition_logs (
                user_id, date, food_name, quantity,
                calories, protein, carbs, fats, fibre
            )
            VALUES (
                ?, DATE('now', 'localtime'), ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            user_id, food_name, quantity,
            calories, protein, carbs, fats, fibre
        ))

        connection.commit()

    finally:
        connection.close()
