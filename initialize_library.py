from pathlib import Path
import runpy

from database import create_database, get_connection
from import_indb import main as import_food_library


def initialize_library():
    create_database()

    connection = get_connection()

    try:
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
