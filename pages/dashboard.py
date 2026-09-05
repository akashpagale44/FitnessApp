import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

from database import get_user, get_today_workout_count
from calculations import (
    calculate_bmr,
    calculate_tdee,
    calculate_calorie_target,
    calculate_protein_target
)


st.title("🏠 Dashboard")

st.write("Your personal fitness overview")


# -------------------------
# Get User
# -------------------------

user = get_user(1)

if user is None:
    st.error("Please create your profile first.")
    st.stop()


# -------------------------
# Calculate Targets
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

workout_count = get_today_workout_count(1)


# -------------------------
# Today's Nutrition
# -------------------------

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

cursor = connection.cursor()

cursor.execute("""
    SELECT
        COALESCE(SUM(calories), 0),
        COALESCE(SUM(protein), 0)
    FROM nutrition_logs
    WHERE user_id = ?
    AND date = DATE('now')
""", (1,))

nutrition = cursor.fetchone()

connection.close()

calories_consumed = nutrition[0]
protein_consumed = nutrition[1]

calories_remaining = max(
    0,
    calorie_target - calories_consumed
)

protein_remaining = max(
    0,
    protein_target - protein_consumed
)


# -------------------------
# Weight Progress
# -------------------------

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

weight_data = pd.read_sql_query(
    """
    SELECT date, weight
    FROM weight_logs
    WHERE user_id = ?
    ORDER BY date
    """,
    connection,
    params=(1,)
)

connection.close()

if weight_data.empty:

    weight_progress = 0
    latest_weight = user["weight"]

else:

    starting_weight = weight_data.iloc[0]["weight"]
    latest_weight = weight_data.iloc[-1]["weight"]

    if user["goal_weight"] != starting_weight:

        weight_progress = (
            (starting_weight - latest_weight)
            / (starting_weight - user["goal_weight"])
        ) * 100

        weight_progress = max(
            0,
            min(100, weight_progress)
        )

    else:
        weight_progress = 100


# -------------------------
# Welcome
# -------------------------

st.subheader(f"👋 Welcome, {user['name']}!")

st.write(
    f"Your current goal is **{user['fitness_goal']}**."
)


# -------------------------
# Today's Overview
# -------------------------

st.subheader("📊 Today's Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Calories",
        f"{calories_consumed:.0f} kcal"
    )

with col2:
    st.metric(
        "Protein",
        f"{protein_consumed:.1f} g"
    )

with col3:
    st.metric(
        "Current Weight",
        f"{latest_weight:.1f} kg"
    )

with col4:
    st.metric(
        "Workouts",
        workout_count
    )


# -------------------------
# Daily Targets
# -------------------------

st.subheader("🎯 Daily Targets")

col1, col2, col3, col4 = st.columns(4)

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

with col3:
    st.metric(
        "Calories Left",
        f"{calories_remaining:.0f} kcal"
    )

with col4:
    st.metric(
        "Protein Left",
        f"{protein_remaining:.1f} g"
    )


# -------------------------
# Goal Progress
# -------------------------

st.subheader("🎯 Weight Goal Progress")

st.progress(
    weight_progress / 100
)

st.write(
    f"**{weight_progress:.0f}%** of your weight goal completed"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Current Weight",
        f"{latest_weight:.1f} kg"
    )

with col2:
    st.metric(
        "Goal Weight",
        f"{user['goal_weight']:.1f} kg"
    )

with col3:
    remaining_weight = abs(
        latest_weight - user["goal_weight"]
    )

    st.metric(
        "Weight to Goal",
        f"{remaining_weight:.1f} kg"
    )


# -------------------------
# Body Information
# -------------------------

st.subheader("📋 Fitness Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "BMR",
        f"{bmr} kcal"
    )

with col2:
    st.metric(
        "TDEE",
        f"{tdee} kcal"
    )

with col3:
    st.metric(
        "Activity",
        user["activity_level"]
    )


# -------------------------
# Weight Chart
# -------------------------

if not weight_data.empty:

    st.subheader("📈 Weight History")

    weight_data["date"] = pd.to_datetime(
        weight_data["date"]
    )

    st.line_chart(
        weight_data.set_index("date")["weight"]
    )


# -------------------------
# Quick Tips
# -------------------------

st.subheader("💡 Today's Focus")

st.write(
    f"🥩 Aim for **{protein_target} g** of protein today."
)

st.write(
    f"🔥 You have approximately **{calories_remaining:.0f} kcal** remaining."
)

st.write(
    "💪 Stay consistent with your training and recovery."
)

st.write(
    "💧 Remember to stay hydrated throughout the day."
)