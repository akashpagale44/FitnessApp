import json
import math
import sqlite3
from pathlib import Path
from openpyxl import load_workbook

from database import create_database, get_connection


BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "data" / "Anuvaad_INDB_2024.11.xlsx"
SOURCE_NAME = "Anuvaad INDB"


def clean_value(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    return value


def classify_food(name):
    name_lower = name.lower()

    beverage_words = (
        "tea", "coffee", "juice", "drink", "beverage",
        "lassi", "sherbet", "smoothie", "milkshake",
        "aam panna", "soup"
    )

    if any(word in name_lower for word in beverage_words):
        return "Beverages"

    return "Indian Recipes & Prepared Foods"


def create_indb_tables(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS food_external_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER NOT NULL,
            source_name TEXT NOT NULL,
            external_id TEXT NOT NULL,
            UNIQUE(source_name, external_id),
            FOREIGN KEY(food_id) REFERENCES foods(id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS food_nutrition_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER NOT NULL UNIQUE,
            source_name TEXT NOT NULL,
            primary_source TEXT,
            nutrients_json TEXT,
            serving_unit TEXT,
            serving_nutrition_json TEXT,
            FOREIGN KEY(food_id) REFERENCES foods(id)
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_food_external_source
        ON food_external_sources(source_name, external_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_food_details_food
        ON food_nutrition_details(food_id)
    """)


def main():
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"INDB Excel file not found: {EXCEL_FILE}"
        )

    create_database()

    workbook = load_workbook(
        EXCEL_FILE,
        read_only=True,
        data_only=True
    )
    sheet = workbook.active

    headers = [
        str(cell).strip() if cell is not None else ""
        for cell in next(sheet.iter_rows(values_only=True))
    ]

    connection = get_connection()

    imported = 0
    linked_existing = 0
    already_processed = 0

    try:
        create_indb_tables(connection)

        connection.execute("""
            INSERT INTO food_categories (name, description)
            VALUES (?, ?)
            ON CONFLICT(name) DO NOTHING
        """, (
            "Indian Recipes & Prepared Foods",
            "Indian dishes, prepared foods and recipes from INDB"
        ))

        connection.execute("""
            INSERT INTO food_categories (name, description)
            VALUES (?, ?)
            ON CONFLICT(name) DO NOTHING
        """, (
            "Beverages",
            "Indian beverages and drinks from INDB"
        ))

        category_ids = {
            row["name"]: row["id"]
            for row in connection.execute(
                "SELECT id, name FROM food_categories"
            ).fetchall()
        }

        for values in sheet.iter_rows(
            min_row=2,
            values_only=True
        ):
            row = dict(zip(headers, values))

            food_code = clean_value(row.get("food_code"))
            food_name = clean_value(row.get("food_name"))

            if food_code is None or not food_name:
                continue

            external_id = str(food_code)

            existing_source = connection.execute("""
                SELECT food_id
                FROM food_external_sources
                WHERE source_name = ? AND external_id = ?
            """, (SOURCE_NAME, external_id)).fetchone()

            if existing_source:
                already_processed += 1
                continue

            category = classify_food(str(food_name))
            category_id = category_ids[category]

            existing_food = connection.execute("""
                SELECT id
                FROM foods
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
                LIMIT 1
            """, (str(food_name),)).fetchone()

            if existing_food:
                food_id = existing_food["id"]
                linked_existing += 1
            else:
                calories = float(row["energy_kcal"] or 0)
                protein = float(row["protein_g"] or 0)
                carbs = float(row["carb_g"] or 0)
                fats = float(row["fat_g"] or 0)

                cursor = connection.execute("""
                    INSERT INTO foods (
                        name, category_id, measurement_unit,
                        calories, protein, carbs, fats,
                        food_state, data_source, is_approximate
                    )
                    VALUES (?, ?, 'g', ?, ?, ?, ?,
                            'prepared', ?, 0)
                """, (
                    str(food_name).strip(),
                    category_id,
                    calories,
                    protein,
                    carbs,
                    fats,
                    SOURCE_NAME
                ))

                food_id = cursor.lastrowid
                imported += 1

            connection.execute("""
                INSERT INTO food_external_sources (
                    food_id, source_name, external_id
                )
                VALUES (?, ?, ?)
            """, (food_id, SOURCE_NAME, external_id))

            nutrients = {
                key: clean_value(value)
                for key, value in row.items()
                if key and (
                    key.endswith(("_mg", "_ug", "_g"))
                    or key in ("energy_kj", "energy_kcal")
                )
            }

            serving_nutrition = {
                key: clean_value(value)
                for key, value in row.items()
                if key.startswith("unit_serving_")
            }

            connection.execute("""
                INSERT OR IGNORE INTO food_nutrition_details (
                    food_id, source_name, primary_source,
                    nutrients_json, serving_unit,
                    serving_nutrition_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                food_id,
                SOURCE_NAME,
                clean_value(row.get("primarysource")),
                json.dumps(nutrients, ensure_ascii=False),
                clean_value(row.get("servings_unit")),
                json.dumps(serving_nutrition, ensure_ascii=False)
            ))

        connection.commit()

        total_foods = connection.execute(
            "SELECT COUNT(*) FROM foods"
        ).fetchone()[0]

        total_details = connection.execute(
            "SELECT COUNT(*) FROM food_nutrition_details"
        ).fetchone()[0]

        print("\nINDB IMPORT COMPLETED")
        print("---------------------")
        print("New foods imported:", imported)
        print("Existing foods linked:", linked_existing)
        print("Already processed:", already_processed)
        print("Total foods in library:", total_foods)
        print("Detailed nutrition records:", total_details)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
        workbook.close()


if __name__ == "__main__":
    main()
