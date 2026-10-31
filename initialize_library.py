from pathlib import Path
import runpy

from database import create_database, get_connection
from import_indb import main as import_food_library


def initialize_library():
    create_database()

    connection = get_connection()

    try:
        # Add fibre to foods if it is missing.
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

        # Add fibre to nutrition logs if it is missing.
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
        print("Initializing exercise library...")
        runpy.run_path(
            str(Path(__file__).resolve().parent / "seed_exercises.py"),
            run_name="__main__"
        )


if __name__ == "__main__":
    initialize_library()
