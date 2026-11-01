from pathlib import Path
import runpy

from database import create_database, get_connection
from import_indb import main as import_food_library


def run_project_script(filename):
    script_path = Path(__file__).resolve().parent / filename
    runpy.run_path(str(script_path), run_name="__main__")


def initialize_library():
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

    finally:
        connection.close()

    if not food_tables_exist or food_count == 0:
        print("Initializing food library...")
        import_food_library()

    if exercise_count == 0:
        print("Initializing original exercise library...")
        run_project_script("seed_exercises.py")

    print("Ensuring expanded exercise library...")
    run_project_script("add_more_exercises.py")

    print("Applying detailed exercise guidance...")
    run_project_script("update_exercise_guidance.py")

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
