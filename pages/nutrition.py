import streamlit as st
import sqlite3
import json
import pandas as pd
from pathlib import Path

from database import get_user, save_nutrition_log, get_connection
from auth import restore_login_session
from calculations import (
    calculate_bmr,
    calculate_tdee,
    calculate_calorie_target,
    calculate_protein_target,
)

st.set_page_config(page_title="Nutrition", page_icon="N", layout="wide")

st.title("Nutrition")
st.write("Track your food, calories, protein, carbs, and fats.")

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "fitness.db"


# =========================
# LOAD FOOD LIBRARY FROM SQLITE
# =========================

@st.cache_data(ttl=3600, show_spinner=False)
def load_food_library():
    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            SELECT
                f.id,
                f.name,
                f.category_id,
                c.name AS category,
                f.brand,
                f.variant,
                f.measurement_unit,
                f.calories,
                f.protein,
                f.carbs,
                f.fats,
                f.fibre,
                f.food_state,
                f.data_source,
                f.is_approximate,
                d.serving_unit,
                d.serving_nutrition_json
            FROM foods f
            LEFT JOIN food_categories c
                ON f.category_id = c.id
            LEFT JOIN food_nutrition_details d
                ON f.id = d.food_id
            WHERE f.is_active = 1
            ORDER BY f.name COLLATE NOCASE, f.food_state
            """
        )
        columns = [column[0] for column in cursor.description]
        foods = cursor.fetchall()
        return [dict(zip(columns, tuple(food))) for food in foods]
    finally:
        connection.close()


# =========================
# CURRENT USER
# =========================

restore_login_session()

if not st.session_state.get("authenticated", False) or "user_id" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

user_id = st.session_state.user_id
user = get_user(user_id)

if user is None:
    st.error("Please create your profile first.")
    st.stop()


# =========================
# DAILY TARGETS
# =========================

bmr = calculate_bmr(
    user["weight"],
    user["height"],
    user["age"],
    user["gender"],
)

tdee = calculate_tdee(bmr, user["activity_level"])
calorie_target = calculate_calorie_target(tdee, user["fitness_goal"])
protein_target = calculate_protein_target(user["weight"])


# =========================
# FOOD LIBRARY
# =========================

try:
    food_library = load_food_library()
except sqlite3.Error as error:
    st.error(f"Could not load food library: {error}")
    st.stop()

if not food_library:
    st.warning("Your food library is empty. Add foods to the foods table first.")
    st.stop()


# =========================
# SERVING SIZE PRESETS
# =========================

def get_serving_options(food_name, food_state, unit):
    if unit == "ml":
        return {
            "1 glass (250 ml)": 250,
            "2 glasses (500 ml)": 500,
            "100 ml": 100,
            "Custom quantity": None,
        }

    if food_name == "egg":
        return {
            "1 egg (about 50 g)": 50,
            "2 eggs (about 100 g)": 100,
            "3 eggs (about 150 g)": 150,
            "Custom quantity": None,
        }

    if food_name == "milk":
        return {
            "1 glass (250 ml)": 250,
            "2 glasses (500 ml)": 500,
            "100 ml": 100,
            "Custom quantity": None,
        }

    if food_name == "chapati":
        return {
            "1 medium chapati (about 40 g)": 40,
            "2 medium chapatis (about 80 g)": 80,
            "3 medium chapatis (about 120 g)": 120,
            "Custom quantity": None,
        }

    if food_name == "rice" and food_state == "cooked":
        return {
            "Small serving (100 g)": 100,
            "1 bowl (about 150 g)": 150,
            "Large serving (200 g)": 200,
            "Custom quantity": None,
        }

    if food_name == "rice" and food_state == "raw":
        return {
            "Small portion (50 g dry)": 50,
            "Medium portion (75 g dry)": 75,
            "Large portion (100 g dry)": 100,
            "Custom quantity": None,
        }

    if food_name == "chicken breast":
        return {
            "100 g": 100,
            "150 g": 150,
            "200 g": 200,
            "250 g": 250,
            "Custom quantity": None,
        }

    return {
        "50 g": 50,
        "100 g": 100,
        "150 g": 150,
        "200 g": 200,
        "Custom quantity": None,
    }


def food_label(food):
    label = food["name"].title()

    if food.get("brand"):
        label += f" - {food['brand']}"

    if food.get("variant"):
        label += f" ({food['variant']})"

    if food["food_state"] != "standard":
        label += f" - {food['food_state'].title()}"

    if food.get("category"):
        label += f" | {food['category']}"

    return label


# =========================
# ADD FOOD
# =========================

st.subheader("Add Food")

meal = st.selectbox(
    "Meal",
    ["Breakfast", "Lunch", "Dinner", "Snack"],
)

search_text = st.text_input(
    "Search food library",
    placeholder="Search eggs, chicken, oats, rice...",
)

categories = sorted({
    food["category"]
    for food in food_library
    if food["category"]
})

selected_category = st.selectbox(
    "Filter by category",
    ["All Categories"] + categories,
)

filtered_foods = food_library

if search_text.strip():
    filtered_foods = [
        food for food in filtered_foods
        if search_text.lower() in food["name"].lower()
        or search_text.lower() in (food.get("brand") or "").lower()
        or search_text.lower() in (food.get("variant") or "").lower()
    ]

if selected_category != "All Categories":
    filtered_foods = [
        food for food in filtered_foods
        if food["category"] == selected_category
    ]

if not filtered_foods:
    st.warning("No matching foods found. Try another search or category.")

food_by_id = {food["id"]: food for food in filtered_foods}

selected_food_id = st.selectbox(
    "Select food to add",
    [None] + list(food_by_id.keys()),
    format_func=lambda food_id: (
        "Select food to add"
        if food_id is None
        else food_label(food_by_id[food_id])
    ),
    index=0,
)

if selected_food_id is None:
    st.info("Search for a food and select it to view its nutrition.")

if selected_food_id is not None:
    food = food_by_id[selected_food_id]

    food_name = food["name"].lower()
    measurement_type = food["food_state"]
    unit = food["measurement_unit"]

    if measurement_type in ["raw", "cooked"]:
        if food_name == "rice":
            st.info(
                "Raw rice means dry weight before boiling."
                if measurement_type == "raw"
                else "Cooked rice means weight after cooking."
            )
        elif food_name == "chicken breast":
            st.info(
                "Raw chicken means weight before cooking."
                if measurement_type == "raw"
                else "Cooked chicken means weight after cooking."
            )

    serving_data = {}
    if food.get("serving_nutrition_json"):
        try:
            serving_data = json.loads(food["serving_nutrition_json"])
        except (TypeError, json.JSONDecodeError):
            serving_data = {}

    serving_keys = [
        "unit_serving_energy_kcal",
        "unit_serving_protein_g",
        "unit_serving_carb_g",
        "unit_serving_fat_g",
    ]

    has_serving_data = (
        food.get("serving_unit")
        and all(serving_data.get(key) is not None for key in serving_keys)
    )

    quantity_mode = "Weight (g)"
    serving_quantity = 1.0
    quantity_display = ""

    if has_serving_data:
        quantity_mode = st.radio(
            "Quantity method",
            ["Weight (g)", "Serving"],
            horizontal=True,
        )

    if has_serving_data and quantity_mode == "Serving":
        serving_unit = food["serving_unit"]
        serving_quantity = st.number_input(
            f"Number of servings ({serving_unit})",
            min_value=0.25,
            max_value=50.0,
            value=1.0,
            step=0.25,
        )
        quantity = serving_quantity
        quantity_display = f"{serving_quantity:g} x {serving_unit}"
        st.caption(
            "Nutrition is calculated from the INDB per-serving values. "
            "No gram conversion is assumed."
        )
    else:
        serving_options = get_serving_options(
            food_name,
            measurement_type,
            unit,
        )

        serving_label = st.selectbox(
            "Choose serving size",
            list(serving_options.keys()),
        )

        preset_quantity = serving_options[serving_label]

        if preset_quantity is None:
            quantity = st.number_input(
                f"Enter quantity ({unit})",
                min_value=1.0,
                max_value=5000.0,
                value=100.0,
                step=10.0,
            )
        else:
            quantity = float(preset_quantity)

        quantity_display = f"{quantity:g} {unit}"
        st.caption(f"Quantity used for calculation: {quantity_display}")


    # =========================
    # NUTRITION PREVIEW
    # =========================

    if has_serving_data and quantity_mode == "Serving":
        calories = float(serving_data["unit_serving_energy_kcal"]) * quantity
        protein = float(serving_data["unit_serving_protein_g"]) * quantity
        carbs = float(serving_data["unit_serving_carb_g"]) * quantity
        fats = float(serving_data["unit_serving_fat_g"]) * quantity
        serving_fibre = serving_data.get("unit_serving_fibre_g")
        fibre = float(serving_fibre) * quantity if serving_fibre is not None else None
    else:
        calories = float(food["calories"]) * quantity / 100
        protein = float(food["protein"]) * quantity / 100
        carbs = float(food["carbs"]) * quantity / 100
        fats = float(food["fats"]) * quantity / 100
        fibre = (
            float(food["fibre"]) * quantity / 100
            if food.get("fibre") is not None else None
        )

    st.subheader("Nutrition Preview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Calories", f"{calories:.1f} kcal")
    col1.metric("Protein", f"{protein:.1f} g")
    col2.metric("Carbs", f"{carbs:.1f} g")
    col2.metric("Fats", f"{fats:.1f} g")
    col3.metric("Fibre", f"{fibre:.1f} g" if fibre is not None else "Unavailable")

    if food["is_approximate"]:
        st.caption(
            "These are approximate nutrition values. Actual values can vary "
            "by brand, recipe, cooking method, and added oil."
        )
    else:
        st.caption(f"Nutrition data source: {food['data_source'] or 'Not specified'}")


    # =========================
    # SAVE FOOD
    # =========================

    if st.button("Add Food to Daily Log", use_container_width=True):
        food_display_name = f"{meal} - {food['name'].title()}"

        if food.get("brand"):
            food_display_name += f" ({food['brand']})"

        if measurement_type in ["raw", "cooked"]:
            food_display_name += f" ({measurement_type.title()})"

        if has_serving_data and quantity_mode == "Serving":
            food_display_name += f" ({quantity_display})"

        try:
            save_nutrition_log(
                user_id,
                food_display_name,
                quantity,
                calories,
                protein,
                carbs,
                fats,
                fibre=fibre,
            )
            st.success(f"{food['name'].title()} added to {meal}!")
            st.rerun()
        except Exception as error:
            st.error(f"Could not save food: {error}")


    # =========================
# LOAD TODAY'S LOG
# =========================

st.divider()
st.subheader("Today's Nutrition")

connection = get_connection()
try:
    totals = connection.execute(
        """
        SELECT
            COALESCE(SUM(calories), 0),
            COALESCE(SUM(protein), 0),
            COALESCE(SUM(carbs), 0),
            COALESCE(SUM(fats), 0),
            SUM(fibre)
        FROM nutrition_logs
        WHERE user_id = ?
          AND date = DATE('now', 'localtime')
        """,
        (user_id,),
    ).fetchone()

    rows = connection.execute(
        """
        SELECT id, food_name, quantity, calories, protein, carbs, fats, fibre
        FROM nutrition_logs
        WHERE user_id = ?
          AND date = DATE('now', 'localtime')
        ORDER BY id DESC
        """,
        (user_id,),
    ).fetchall()
except sqlite3.Error as error:
    st.error(f"Could not load nutrition history: {error}")
    st.stop()
finally:
    connection.close()

total_calories, total_protein, total_carbs, total_fats, total_fibre = totals

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Calories", f"{total_calories:.0f} kcal")
col2.metric("Protein", f"{total_protein:.1f} g")
col3.metric("Carbs", f"{total_carbs:.1f} g")
col4.metric("Fats", f"{total_fats:.1f} g")
col5.metric("Fibre (known)", f"{total_fibre:.1f} g" if total_fibre is not None else "?")


# =========================
# MEAL-WISE SUMMARY
# =========================

st.divider()
st.subheader("Meal-wise Summary")

meal_names = ["Breakfast", "Lunch", "Dinner", "Snack"]

meal_totals = {
    name: {"calories": 0.0, "protein": 0.0, "fibre": 0.0, "has_fibre": False}
    for name in meal_names
}

for row in rows:
    logged_food = row[1]
    food_calories = row[3] or 0
    food_protein = row[4] or 0
    food_fibre = row[7]

    for meal_name in meal_names:
        if logged_food.startswith(meal_name + " -"):
            meal_totals[meal_name]["calories"] += food_calories
            meal_totals[meal_name]["protein"] += food_protein
            if food_fibre is not None:
                meal_totals[meal_name]["fibre"] += food_fibre
                meal_totals[meal_name]["has_fibre"] = True
            break

cols = st.columns(4)

for col, meal_name in zip(cols, meal_names):
    with col:
        st.markdown(f"**{meal_name}**")
        st.metric(
            "Calories",
            f"{meal_totals[meal_name]['calories']:.0f} kcal",
        )
        st.metric(
            "Protein",
            f"{meal_totals[meal_name]['protein']:.1f} g",
        )
        st.metric(
            "Fibre (known)",
            f"{meal_totals[meal_name]['fibre']:.1f} g"
            if meal_totals[meal_name]["has_fibre"] else "?",
        )


# =========================
# DAILY TARGETS
# =========================

st.divider()
st.subheader("Daily Targets")

col1, col2 = st.columns(2)
col1.metric("Calorie Target", f"{calorie_target:.0f} kcal")
col2.metric("Protein Target", f"{protein_target:.1f} g")

remaining_calories = calorie_target - total_calories
remaining_protein = protein_target - total_protein

col1, col2 = st.columns(2)
col1.metric(
    "Calories Remaining",
    f"{max(0, remaining_calories):.0f} kcal",
)
col2.metric(
    "Protein Remaining",
    f"{max(0, remaining_protein):.1f} g",
)

if calorie_target > 0:
    st.caption("Calorie target progress")
    st.progress(min(total_calories / calorie_target, 1.0))

if protein_target > 0:
    st.caption("Protein target progress")
    st.progress(min(total_protein / protein_target, 1.0))


# =========================
# TODAY'S FOOD LOG
# =========================

st.divider()
st.subheader("Today's Food Log")

if not rows:
    st.info("No food logged today.")
else:
    food_data = pd.DataFrame(
        [
            {
                "Food": row[1],
                "Quantity": row[2],
                "Calories": round(row[3], 1),
                "Protein (g)": round(row[4], 1),
                "Carbs (g)": round(row[5], 1),
                "Fats (g)": round(row[6], 1),
            }
            for row in rows
        ]
    )

    st.dataframe(
        food_data,
        use_container_width=True,
        hide_index=True,
    )

    # =========================
    # DELETE A FOOD ENTRY
    # =========================

    st.subheader("Delete a Food Entry")
    st.caption(
        "Choose an entry logged today. Deletion cannot be undone."
    )

    row_options = {
        f"ID {row[0]} | {row[1]} | {row[2]:g} | {row[3]:.0f} kcal": row[0]
        for row in rows
    }

    selected_entry = st.selectbox(
        "Select the entry to delete",
        list(row_options.keys()),
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this entry."
    )

    if st.button("Delete Selected Entry", use_container_width=True):
        if not confirm_delete:
            st.warning("Please confirm deletion first.")
        else:
            selected_id = row_options[selected_entry]

            connection = get_connection()
            try:
                cursor = connection.execute(
                    """
                    DELETE FROM nutrition_logs
                    WHERE id = ?
                      AND user_id = ?
                      AND date = DATE('now', 'localtime')
                    """,
                    (selected_id, user_id),
                )

                if cursor.rowcount > 0:
                    st.success("Food entry deleted.")
                    st.rerun()
                else:
                    st.warning("Entry not found. Refresh and try again.")

            except sqlite3.Error as error:
                st.error(f"Could not delete entry: {error}")
            finally:
                connection.close()




