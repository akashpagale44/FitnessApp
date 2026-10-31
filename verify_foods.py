from database import get_connection

connection = get_connection()

try:
    print("FOOD CATEGORY COUNTS")
    rows = connection.execute("""
        SELECT food_categories.name, COUNT(foods.id) AS total
        FROM food_categories
        LEFT JOIN foods ON foods.category_id = food_categories.id
        GROUP BY food_categories.id
        ORDER BY food_categories.name
    """).fetchall()

    for row in rows:
        print(row["name"], ":", row["total"])

    print("\nRAW AND COOKED VARIANTS")
    rows = connection.execute("""
        SELECT name, food_state, calories, protein
        FROM foods
        WHERE food_state IN ('raw', 'cooked')
        ORDER BY name, food_state
    """).fetchall()

    for row in rows:
        print(row["name"], "|", row["food_state"],
              "| Calories:", row["calories"],
              "| Protein:", row["protein"])

    print("\nTOTAL:", connection.execute(
        "SELECT COUNT(*) FROM foods"
    ).fetchone()[0])

finally:
    connection.close()
