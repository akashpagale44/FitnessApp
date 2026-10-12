import streamlit as st
import sqlite3
import pandas as pd
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


# =========================
# CURRENT USER
# =========================

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

user_id = st.session_state.user_id


# =========================
# GET USER
# =========================

user = get_user(user_id)

if user is None:
    st.error("Please create your profile first.")
    st.stop()


# =========================
# CALCULATE DAILY TARGETS
# =========================

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


# =========================
# ADD FOOD
# =========================

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


# =========================
# RAW / COOKED SELECTION
# =========================

foods_with_cooking_difference = [
    "chicken breast",
    "rice"
]

if food_name in foods_with_cooking_difference:

    measurement_choice = st.radio(
        "How did you measure it?",
        [
            "Raw weight",
            "Cooked weight"
        ],
        horizontal=True
    )

    if measurement_choice == "Raw weight":
        measurement_type = "raw"
    else:
        measurement_type = "cooked"

else:

    measurement_type = "standard"


# =========================
# QUANTITY
# =========================

quantity = st.number_input(
    "Quantity (g)",
    min_value=1.0,
    value=100.0,
    step=1.0
)


# =========================
# INFORMATION
# =========================

if food_name == "chicken breast":

    st.info(
        "💡 Chicken loses water during cooking. "
        "Select Raw if you weighed it before cooking "
        "or Cooked if you weighed it after cooking."
    )

elif food_name == "rice":

    st.info(
        "💡 Rice absorbs water during cooking. "
        "Select Raw if you weighed dry rice "
        "or Cooked if you weighed cooked rice."
    )


# =========================
# ADD FOOD BUTTON
# =========================

if st.button("➕ Add Food"):

    food = get_food(
        food_name,
        measurement_type
    )

    if food is None:

        st.error(
            "Food not found in our database."
        )

    else:

        calories = food["calories"] * quantity / 100
        protein = food["protein"] * quantity / 100
        carbs = food["carbs"] * quantity / 100
        fats = food["fats"] * quantity / 100

        food_display_name = food_name

        if measurement_type == "raw":
            food_display_name = (
                f"{food_name} (Raw)"
            )

        elif measurement_type == "cooked":
            food_display_name = (
                f"{food_name} (Cooked)"
            )

        save_nutrition_log(
            user_id,
            f"{meal} - {food_display_name}",
            quantity,
            calories,
            protein,
            carbs,
            fats
        )

        st.success(
            f"{food_name.title()} added to {meal}! 🍽️"
        )

        st.write(
            f"**Calories:** {calories:.1f} kcal"
        )

        st.write(
            f"**Protein:** {protein:.1f} g"
        )


# =========================
# TODAY'S NUTRITION
# =========================

st.subheader("📊 Today's Nutrition")

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        COALESCE(SUM(calories), 0),
        COALESCE(SUM(protein), 0),
        COALESCE(SUM(carbs), 0),
        COALESCE(SUM(fats), 0)
    FROM nutrition_logs
    WHERE user_id = ?
    AND date = DATE('now')
    """,
    (user_id,)
)

totals = cursor.fetchone()

connection.close()

total_calories = totals[0]
total_protein = totals[1]
total_carbs = totals[2]
total_fats = totals[3]


# =========================
# NUTRITION METRICS
# =========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🔥 Calories",
        f"{total_calories:.0f} kcal"
    )

with col2:
    st.metric(
        "🥩 Protein",
        f"{total_protein:.1f} g"
    )

with col3:
    st.metric(
        "🍚 Carbs",
        f"{total_carbs:.1f} g"
    )

with col4:
    st.metric(
        "🥑 Fats",
        f"{total_fats:.1f} g"
    )


# =========================
# DAILY TARGETS
# =========================

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


# =========================
# REMAINING TARGETS
# =========================

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


# =========================
# TODAY'S FOOD LOG
# =========================

st.subheader("📋 Today's Food Log")

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

cursor = connection.cursor()

cursor.execute(
    """
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
    """,
    (user_id,)
)

rows = cursor.fetchall()

connection.close()


if not rows:

    st.info(
        "No food logged today."
    )

else:

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