import sqlite3

connection = sqlite3.connect("data/fitness.db")

checks = {
    "Exercises": "SELECT COUNT(*) FROM exercises",
    "Muscle relationships": "SELECT COUNT(*) FROM exercise_muscles",
    "Primary mappings": "SELECT COUNT(*) FROM exercise_muscles WHERE role = 'primary'",
    "Secondary mappings": "SELECT COUNT(*) FROM exercise_muscles WHERE role = 'secondary'"
}

print("\nEXERCISE DATABASE VERIFICATION\n")

for label, query in checks.items():
    result = connection.execute(query).fetchone()[0]
    print(f"{label}: {result}")

connection.close()