from auth import restore_login_session
import streamlit as st
import pandas as pd

from database import get_connection
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
    page_icon="💪",
    layout="wide"
)



# =========================
# CURRENT USER
# =========================

restore_login_session()

if not st.session_state.get("authenticated", False) or "user_id" not in st.session_state:
    st.warning("Please log in to access this page.")
    st.stop()

user_id = st.session_state.user_id


# =========================
# TITLE
# =========================

st.title("💪 Fitness Dashboard")
st.write("Your personal fitness overview")


# =========================
# LOAD DASHBOARD DATA
# =========================

connection = get_connection()

try:
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )
    user = cursor.fetchone()

    if user is not None:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM workout_logs
            WHERE user_id = ?
            AND date = DATE('now')
            """,
            (user_id,)
        )
        workout_count = cursor.fetchone()[0]

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

        cursor.execute(
            """
            SELECT date, weight
            FROM weight_logs
            WHERE user_id = ?
            ORDER BY date
            """,
            (user_id,)
        )
        weight_rows = cursor.fetchall()

        weight_data = pd.DataFrame(
            weight_rows,
            columns=["date", "weight"]
        )

finally:
    connection.close()

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

calories_consumed = float(nutrition[0] or 0)
protein_consumed = float(nutrition[1] or 0)

calories_remaining = max(
    0,
    calorie_target - calories_consumed
)

protein_remaining = max(
    0,
    protein_target - protein_consumed
)


# =========================
# WEIGHT HISTORY
# =========================

goal_weight = float(user["goal_weight"])

if weight_data.empty:
    latest_weight = float(user["weight"])
    weight_progress = 0.0

else:
    weight_data["date"] = pd.to_datetime(
        weight_data["date"],
        errors="coerce"
    )

    weight_data["weight"] = pd.to_numeric(
        weight_data["weight"],
        errors="coerce"
    )

    weight_data = weight_data.dropna(
        subset=["date", "weight"]
    ).sort_values("date")

    if weight_data.empty:
        latest_weight = float(user["weight"])
        weight_progress = 0.0

    else:
        starting_weight = float(
            weight_data.iloc[0]["weight"]
        )

        latest_weight = float(
            weight_data.iloc[-1]["weight"]
        )

        total_change_needed = goal_weight - starting_weight
        actual_change = latest_weight - starting_weight

        if abs(latest_weight - goal_weight) < 0.1:
            weight_progress = 100.0

        elif abs(total_change_needed) < 0.1:
            weight_progress = 0.0

        else:
            weight_progress = (
                actual_change / total_change_needed
            ) * 100

            weight_progress = max(
                0.0,
                min(100.0, weight_progress)
            )


# =========================
# WELCOME
# =========================

st.subheader(f"Welcome, {user['name']}!")

st.write(
    f"Your current fitness goal is **{user['fitness_goal']}**."
)


# =========================
# TODAY'S OVERVIEW
# =========================

st.subheader("Today's Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Calories Consumed",
        f"{calories_consumed:.0f} kcal"
    )

with col2:
    st.metric(
        "Protein Consumed",
        f"{protein_consumed:.1f} g"
    )

with col3:
    st.metric(
        "Current Weight",
        f"{latest_weight:.1f} kg"
    )

with col4:
    st.metric(
        "Workouts Today",
        workout_count
    )


# =========================
# DAILY TARGETS
# =========================

st.subheader("Daily Targets")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Calorie Target",
        f"{calorie_target:.0f} kcal"
    )

with col2:
    st.metric(
        "Protein Target",
        f"{protein_target:.0f} g"
    )

with col3:
    st.metric(
        "Calories Remaining",
        f"{calories_remaining:.0f} kcal"
    )

with col4:
    st.metric(
        "Protein Remaining",
        f"{protein_remaining:.1f} g"
    )


# =========================
# DAILY GOAL TRACKER
# =========================

st.subheader("Today's Goal Tracker")

calorie_progress = (
    min(max(calories_consumed / calorie_target, 0.0), 1.0)
    if calorie_target > 0
    else 0.0
)

protein_progress = (
    min(max(protein_consumed / protein_target, 0.0), 1.0)
    if protein_target > 0
    else 0.0
)

calorie_percentage = (
    calories_consumed / calorie_target * 100
    if calorie_target > 0
    else 0.0
)

protein_percentage = (
    protein_consumed / protein_target * 100
    if protein_target > 0
    else 0.0
)


# =========================
# CALORIE PROGRESS
# =========================

st.markdown("### 🔥 Daily Calories")

st.write(
    f"**{calories_consumed:.0f} / {calorie_target:.0f} kcal**"
)

st.progress(calorie_progress)

st.caption(
    f"{calorie_percentage:.0f}% of your calorie target"
)

if calorie_target <= 0:
    st.warning("Your calorie target is unavailable.")

elif calories_consumed >= calorie_target:
    st.success("Your calorie target has been reached.")

else:
    st.info(
        f"Approximately {calories_remaining:.0f} kcal "
        "remaining to reach your target."
    )

st.divider()


# =========================
# PROTEIN PROGRESS
# =========================

st.markdown("### 🥚 Daily Protein")

st.write(
    f"**{protein_consumed:.1f} / {protein_target:.0f} g**"
)

st.progress(protein_progress)

st.caption(
    f"{protein_percentage:.0f}% of your protein target"
)

if protein_target <= 0:
    st.warning("Your protein target is unavailable.")

elif protein_consumed >= protein_target:
    st.success(
        "Great! You have reached your protein target."
    )

else:
    st.info(
        f"Approximately {protein_remaining:.1f} g protein "
        "remaining to reach your target."
    )


# =========================
# WEIGHT GOAL
# =========================

st.subheader("Weight Goal Progress")

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
        f"{goal_weight:.1f} kg"
    )

with col3:
    remaining_weight = abs(
        latest_weight - goal_weight
    )

    st.metric(
        "Weight to Goal",
        f"{remaining_weight:.1f} kg"
    )

if abs(latest_weight - goal_weight) < 0.1:
    st.success(
        "Congratulations! You have reached your weight goal."
    )


# =========================
# FITNESS INFORMATION
# =========================

st.subheader("Fitness Information")

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
    st.subheader("Weight History")

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

st.subheader("Today's Focus")

focus_col1, focus_col2 = st.columns(2)

with focus_col1:
    st.write(
        f"Aim for **{protein_target:.0f} g** of protein today."
    )

    st.write(
        f"You have approximately **{calories_remaining:.0f} kcal** "
        "remaining to reach your calorie target."
    )

with focus_col2:
    st.write("💪 Stay consistent with your training.")
    st.write("💧 Remember to stay hydrated.")
    st.write("😴 Give your body enough time to recover.")