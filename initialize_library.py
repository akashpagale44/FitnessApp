from pathlib import Path
import runpy

from database import create_database, get_connection
from import_indb import main as import_food_library


def run_project_script(filename):
    script_path = Path(__file__).resolve().parent / filename
    runpy.run_path(str(script_path), run_name="__main__")


def initialize_library():
    connection = get_connection()
    try:
        existing_tables = {
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        required_tables = {
            "users", "auth_sessions", "nutrition_logs", "workout_logs",
            "weight_logs", "quiz_logs", "food_categories", "foods",
            "muscle_groups", "exercises", "exercise_muscles",
            "food_external_sources", "food_nutrition_details"
        }
        schema_ready = required_tables.issubset(existing_tables)
    finally:
        connection.close()

    if schema_ready:
        print("Database schema already exists. Skipping table creation.", flush=True)
    else:
        print("Database schema incomplete. Initializing tables.", flush=True)
        create_database()

    connection = get_connection()

    try:
        food_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(foods)"
            ).fetchall()
        }

        if "fibre" not in food_columns:
            connection.execute(
                "ALTER TABLE foods ADD COLUMN fibre REAL"
            )
            print("Added missing fibre column to foods table.")

        log_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(nutrition_logs)"
            ).fetchall()
        }

        if "fibre" not in log_columns:
            connection.execute(
                "ALTER TABLE nutrition_logs ADD COLUMN fibre REAL"
            )
            print("Added missing fibre column to nutrition_logs table.")

        connection.commit()

        food_tables_exist = connection.execute("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN (
                  'food_nutrition_details',
                  'food_external_sources'
              )
        """).fetchone()[0] == 2

        food_count = connection.execute(
            "SELECT COUNT(*) FROM foods"
        ).fetchone()[0]

        exercise_count = connection.execute(
            "SELECT COUNT(*) FROM exercises"
        ).fetchone()[0]

        missing_guidance_count = connection.execute("""
            SELECT COUNT(*)
            FROM exercises
            WHERE is_active = 1
              AND (
                  instructions IS NULL OR TRIM(instructions) = ''
                  OR common_mistakes IS NULL OR TRIM(common_mistakes) = ''
              )
        """).fetchone()[0]

    finally:
        connection.close()

    print(f'INIT_DIAG: foods={food_count}, exercises={exercise_count}, missing_guidance={missing_guidance_count}', flush=True)
    if not food_tables_exist or food_count == 0:
        print("Initializing food library...")
        import_food_library()

    if exercise_count == 0:
        print("Initializing original exercise library...")
        run_project_script("seed_exercises.py")

    if exercise_count < 53:
        print("Ensuring expanded exercise library...")
        run_project_script("add_more_exercises.py")
    else:
        print("Exercise library already populated. Skipping expansion.")

    if missing_guidance_count > 0:
        print("Applying detailed exercise guidance...")
        run_project_script("update_exercise_guidance.py")
    else:
        print("Exercise guidance already complete. Skipping updates.")

    connection = get_connection()
    try:
        connection.execute("""
            UPDATE foods
            SET calories = 155.0,
                protein = 12.58,
                carbs = 1.12,
                fats = 10.61,
                fibre = 0.0
            WHERE id = (
                SELECT food_id
                FROM food_external_sources
                WHERE source_name = 'Anuvaad INDB'
                  AND external_id = 'ASC056'
                LIMIT 1
            )
        """)
        connection.commit()
    finally:
        connection.close()

    print("Library initialization completed.")


if __name__ == "__main__":
    initialize_library()

