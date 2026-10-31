import json
import sqlite3
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "data" / "fitness.db"
API_URL = "https://search.openfoodfacts.org/search"


def search_online_foods(query, limit=10):
    query = query.strip()

    if len(query) < 2:
        return []

    params = urlencode({
        "q": query,
        "page_size": limit,
        "langs": "en",
    })

    request = Request(
        f"{API_URL}?{params}",
        headers={
            "User-Agent": "FitnessApp/1.0 (Student Project)",
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))

    hits = data.get("hits", [])

    if isinstance(hits, dict):
        hits = hits.get("hits", [])

    if not hits:
        hits = data.get("products", [])

    results = []
    seen = set()

    for hit in hits:
        product = hit.get("_source", hit)

        name = (
            product.get("product_name")
            or product.get("product_name_en")
            or product.get("generic_name")
            or ""
        ).strip()

        if not name:
            continue

        nutrients = product.get("nutriments") or {}

        def nutrient(*keys):
            for key in keys:
                value = nutrients.get(key, product.get(key))
                if value is not None:
                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        pass
            return 0.0

        calories = nutrient("energy-kcal_100g", "energy-kcal_value")

        if calories <= 0:
            energy_kj = nutrient("energy_100g")
            calories = energy_kj / 4.184 if energy_kj > 0 else 0

        protein = nutrient("proteins_100g")
        carbs = nutrient("carbohydrates_100g")
        fats = nutrient("fat_100g")

        if calories <= 0 or not any([protein, carbs, fats]):
            continue

        barcode = str(product.get("code") or product.get("id") or "")
        brand = str(product.get("brands") or "").split(",")[0].strip()

        unique_key = barcode or (name.lower(), brand.lower())

        if unique_key in seen:
            continue

        seen.add(unique_key)

        results.append({
            "name": name,
            "brand": brand,
            "barcode": barcode,
            "quantity": product.get("quantity", ""),
            "calories": round(calories, 2),
            "protein": round(protein, 2),
            "carbs": round(carbs, 2),
            "fats": round(fats, 2),
            "data_source": "Open Food Facts",
        })

    return results


def save_online_food_to_library(food):
    with sqlite3.connect(DB_PATH) as connection:
        category = connection.execute(
            "SELECT id FROM food_categories WHERE name = ?",
            ("Other",),
        ).fetchone()

        if category:
            category_id = category[0]
        else:
            cursor = connection.execute(
                "INSERT INTO food_categories (name) VALUES (?)",
                ("Other",),
            )
            category_id = cursor.lastrowid

        existing = connection.execute(
            """
            SELECT id FROM foods
            WHERE lower(name) = lower(?)
              AND lower(COALESCE(brand, '')) = lower(?)
              AND data_source = 'Open Food Facts'
              AND food_state = 'standard'
            """,
            (food["name"], food["brand"]),
        ).fetchone()

        if existing:
            return False

        connection.execute(
            """
            INSERT INTO foods (
                name,
                category_id,
                brand,
                variant,
                measurement_unit,
                calories,
                protein,
                carbs,
                fats,
                food_state,
                data_source,
                is_approximate,
                is_active
            )
            VALUES (?, ?, ?, ?, 'g', ?, ?, ?, ?, 'standard',
                    'Open Food Facts', 1, 1)
            """,
            (
                food["name"],
                category_id,
                food["brand"] or None,
                food["barcode"] or None,
                food["calories"],
                food["protein"],
                food["carbs"],
                food["fats"],
            ),
        )

        return True
