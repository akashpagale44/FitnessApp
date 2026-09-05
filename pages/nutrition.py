import streamlit as st
import sqlite3
from pathlib import Path

from database import get_user, get_food, save_nutrition_log
from calculations import (
    calculate_bmr,
    calculate_tdee,
    calculate_calorie_target,
    calculate_protein_target
)


st.title("🍎 Nutrition")

st.write("Track your daily food intake and nutrition.")


# -------------------------
# Get User
# -------------------------

user = get_user(1)

if user is None:
    st.error("Please create your profile first.")
    st.stop()


# -------------------------
# Calculate Daily Targets
# -------------------------

bmr = calculate_bmr(
    user["weight"],
    user["height"],
    user["age"],
    user["gender"]
)

tdee = calculate_tdee(
    bmr,
    user["activity_level"]
)

calorie_target = calculate_calorie_target(
    tdee,
    user["fitness_goal"]
)

protein_target = calculate_protein_target(
    user["weight"]
)


# -------------------------
# Add Food
# -------------------------

st.subheader("🍽️ Add Food")

meal = st.selectbox(
    "Meal",
    [
        "Breakfast",
        "Lunch",
        "Dinner",
        "Snack"
    ]
)

food_name = st.selectbox(
    "Food Name",
    [
        "egg",
        "rice",
        "chicken breast",
        "milk",
        "oats",
        "banana"
    ]
)

quantity = st.number_input(
    "Quantity (g)",
    min_value=1.0,
    value=100.0
)


if st.button("Add Food"):

    food = get_food(food_name)

    if food is None:

        st.error(
            "Food not found in our database."
        )

    else:

        calories = food["calories"] * quantity / 100
        protein = food["protein"] * quantity / 100
        carbs = food["carbs"] * quantity / 100
        fats = food["fats"] * quantity / 100

        save_nutrition_log(
            1,
            f"{meal} - {food_name}",
            quantity,
            calories,
            protein,
            carbs,
            fats
        )

        st.success(
            f"{food_name.title()} added to {meal}! 🍽️"
        )


# -------------------------
# Today's Nutrition
# -------------------------

st.subheader("📊 Today's Nutrition")

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

cursor = connection.cursor()

cursor.execute("""
    SELECT
        COALESCE(SUM(calories), 0),
        COALESCE(SUM(protein), 0),
        COALESCE(SUM(carbs), 0),
        COALESCE(SUM(fats), 0)
    FROM nutrition_logs
    WHERE user_id = ?
    AND date = DATE('now')
""", (1,))

totals = cursor.fetchone()

connection.close()

total_calories = totals[0]
total_protein = totals[1]
total_carbs = totals[2]
total_fats = totals[3]


# -------------------------
# Nutrition Metrics
# -------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Calories",
        f"{total_calories:.0f} kcal"
    )

with col2:
    st.metric(
        "Protein",
        f"{total_protein:.1f} g"
    )

with col3:
    st.metric(
        "Carbs",
        f"{total_carbs:.1f} g"
    )

with col4:
    st.metric(
        "Fats",
        f"{total_fats:.1f} g"
    )


# -------------------------
# Daily Targets
# -------------------------

st.subheader("🎯 Daily Targets")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Calorie Target",
        f"{calorie_target} kcal"
    )

with col2:
    st.metric(
        "Protein Target",
        f"{protein_target} g"
    )


# -------------------------
# Remaining Targets
# -------------------------

remaining_calories = (
    calorie_target - total_calories
)

remaining_protein = (
    protein_target - total_protein
)

st.subheader("📌 Remaining Today")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Calories Remaining",
        f"{max(0, remaining_calories):.0f} kcal"
    )

with col2:
    st.metric(
        "Protein Remaining",
        f"{max(0, remaining_protein):.1f} g"
    )


# -------------------------
# Today's Food Log
# -------------------------

st.subheader("📋 Today's Food Log")

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

food_log = cursor = connection.cursor()

cursor.execute("""
    SELECT
        food_name AS Food,
        quantity AS Quantity,
        calories AS Calories,
        protein AS Protein,
        carbs AS Carbs,
        fats AS Fats
    FROM nutrition_logs
    WHERE user_id = ?
    AND date = DATE('now')
    ORDER BY id DESC
""", (1,))

rows = cursor.fetchall()

connection.close()


if not rows:

    st.info(
        "No food logged today."
    )

else:

    import pandas as pd

    food_data = pd.DataFrame(
        rows,
        columns=[
            "Food",
            "Quantity",
            "Calories",
            "Protein",
            "Carbs",
            "Fats"
        ]
    )

    st.dataframe(
        food_data,
        use_container_width=True,
        hide_index=True
    )