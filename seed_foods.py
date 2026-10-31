import ast
from database import add_food, get_connection

# Read the existing food dictionary directly from database.py
with open("database.py", "r", encoding="utf-8") as file:
    tree = ast.parse(file.read())

food_data = None

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_food":
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "foods":
                        food_data = ast.literal_eval(item.value)
                        break

if food_data is None:
    raise RuntimeError("Could not find the existing food dictionary.")

category_map = {
    "egg": "Eggs",
    "boiled egg": "Eggs",
    "chicken breast": "Meat and Fish",
    "milk": "Dairy",
    "paneer": "Dairy",
    "curd": "Dairy",
    "rice": "Grains and Cereals",
    "oats": "Grains and Cereals",
    "chapati": "Grains and Cereals",
    "poha": "Grains and Cereals",
    "idli": "Grains and Cereals",
    "dosa": "Grains and Cereals",
    "upma": "Grains and Cereals",
    "bajra flour": "Grains and Cereals",
    "whole wheat flour": "Grains and Cereals",
    "dal": "Pulses and Legumes",
    "cooked moong dal": "Pulses and Legumes",
    "moong dal": "Pulses and Legumes",
    "soya chunks": "Pulses and Legumes",
    "roasted chana": "Pulses and Legumes",
    "besan": "Pulses and Legumes",
    "chickpeas": "Pulses and Legumes",
    "cooked chickpeas": "Pulses and Legumes",
    "rajma": "Pulses and Legumes",
    "banana": "Fruits",
    "apple": "Fruits",
    "orange": "Fruits",
    "dates": "Fruits",
    "potato": "Vegetables",
    "sweet potato": "Vegetables",
    "tomato": "Vegetables",
    "cucumber": "Vegetables",
    "carrot": "Vegetables",
    "peanuts": "Nuts and Seeds",
    "almonds": "Nuts and Seeds",
    "sweet corn": "Vegetables",
    "sugar": "Other"
}

connection = get_connection()

try:
    existing = {
        (row["name"].lower(), row["food_state"])
        for row in connection.execute(
            "SELECT name, food_state FROM foods"
        ).fetchall()
    }
finally:
    connection.close()

added = 0
skipped = 0

for name, values in food_data.items():

    if "calories" in values:
        variants = [("standard", values)]
    else:
        variants = [
            (state, nutrition)
            for state, nutrition in values.items()
            if state != "standard"
        ]

    for state, nutrition in variants:

        key = (name.lower(), state)

        if key in existing:
            skipped += 1
            continue

        add_food(
            name=name,
            category=category_map.get(name, "Other"),
            calories=nutrition["calories"],
            protein=nutrition["protein"],
            carbs=nutrition["carbs"],
            fats=nutrition["fats"],
            measurement_unit="ml" if name == "milk" else "g",
            food_state=state,
            data_source="Existing Fitness App food database",
            is_approximate=1
        )

        existing.add(key)
        added += 1

print("FOOD LIBRARY IMPORT COMPLETED")
print("Food records added:", added)
print("Existing records skipped:", skipped)

connection = get_connection()
try:
    total = connection.execute(
        "SELECT COUNT(*) FROM foods"
    ).fetchone()[0]
    print("Total food records now in database:", total)
finally:
    connection.close()
