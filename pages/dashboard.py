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


# =========================
# PAGE SETTINGS
# =========================

st.set_page_config(
    page_title="Fitness App - Dashboard",
    page_icon="🏋️",
    layout="wide"
)


# =========================
# CURRENT USER
# =========================

# Temporary current-user system
# Later we will replace this with proper login/profile selection.

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

user_id = st.session_state.user_id


# =========================
# TITLE
# =========================

st.title("🏠 Dashboard")
st.write("Your personal fitness overview")


# =========================
# GET USER
# =========================

user = get_user(user_id)

if user is None:
    st.error("Please create your profile first.")
    st.stop()


# =========================
# CALCULATE TARGETS
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

workout_count = get_today_workout_count(user_id)


# =========================
# TODAY'S NUTRITION
# =========================

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        COALESCE(SUM(calories), 0),
        COALESCE(SUM(protein), 0)
    FROM nutrition_logs
    WHERE user_id = ?
    AND date = DATE('now')
    """,
    (user_id,)
)

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


# =========================
# WEIGHT PROGRESS
# =========================

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
    params=(user_id,)
)

connection.close()


if weight_data.empty:

    weight_progress = 0
    latest_weight = user["weight"]

else:

    starting_weight = float(
        weight_data.iloc[0]["weight"]
    )

    latest_weight = float(
        weight_data.iloc[-1]["weight"]
    )

    goal_weight = float(
        user["goal_weight"]
    )

    if starting_weight != goal_weight:

        weight_progress = (
            (starting_weight - latest_weight)
            / (starting_weight - goal_weight)
        ) * 100

        weight_progress = max(
            0,
            min(100, weight_progress)
        )

    else:

        weight_progress = 100


# =========================
# WELCOME
# =========================

st.subheader(
    f"👋 Welcome, {user['name']}!"
)

st.write(
    f"Your current goal is **{user['fitness_goal']}**."
)


# =========================
# TODAY'S OVERVIEW
# =========================

st.subheader("📊 Today's Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🔥 Calories",
        f"{calories_consumed:.0f} kcal"
    )

with col2:
    st.metric(
        "🥩 Protein",
        f"{protein_consumed:.1f} g"
    )

with col3:
    st.metric(
        "⚖️ Current Weight",
        f"{latest_weight:.1f} kg"
    )

with col4:
    st.metric(
        "🏋️ Workouts",
        workout_count
    )


# =========================
# DAILY TARGETS
# =========================

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


# =========================
# DAILY PROGRESS
# =========================

st.subheader("📈 Today's Progress")

calorie_progress = (
    min(calories_consumed / calorie_target, 1.0)
    if calorie_target > 0
    else 0
)

protein_progress = (
    min(protein_consumed / protein_target, 1.0)
    if protein_target > 0
    else 0
)

st.write(
    f"🔥 Calories: **{calories_consumed:.0f} / "
    f"{calorie_target} kcal**"
)

st.progress(calorie_progress)

st.write(
    f"🥩 Protein: **{protein_consumed:.1f} / "
    f"{protein_target} g**"
)

st.progress(protein_progress)


# =========================
# WEIGHT GOAL
# =========================

st.subheader("🎯 Weight Goal Progress")

st.progress(weight_progress / 100)

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


# =========================
# FITNESS INFORMATION
# =========================

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
        "Activity Level",
        user["activity_level"]
    )


# =========================
# WEIGHT CHART
# =========================

if not weight_data.empty:

    st.subheader("📈 Weight History")

    weight_data["date"] = pd.to_datetime(
        weight_data["date"]
    )

    st.line_chart(
        weight_data.set_index("date")["weight"]
    )

else:

    st.info(
        "No weight history available yet. "
        "Start logging your weight to see your progress chart."
    )


# =========================
# TODAY'S FOCUS
# =========================

st.subheader("💡 Today's Focus")

focus_col1, focus_col2 = st.columns(2)

with focus_col1:

    st.write(
        f"🥩 Aim for **{protein_target:.0f} g** "
        "of protein today."
    )

    st.write(
        f"🔥 You have approximately "
        f"**{calories_remaining:.0f} kcal** remaining."
    )

with focus_col2:

    st.write(
        "💪 Stay consistent with your training."
    )

    st.write(
        "💧 Remember to stay hydrated."
    )

    st.write(
        "😴 Give your body enough time to recover."
    )