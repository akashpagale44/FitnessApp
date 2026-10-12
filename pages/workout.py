import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

from database import save_workout_log


# =========================
# CURRENT USER
# =========================

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

user_id = st.session_state.user_id


st.title("🏋️ Workout")

st.write("Follow a workout plan and track your training.")


# =========================
# GET USER GOAL
# =========================

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

cursor = connection.cursor()

cursor.execute("""
    SELECT fitness_goal
    FROM users
    WHERE id = ?
""", (user_id,))

user_goal = cursor.fetchone()

connection.close()


if user_goal:
    fitness_goal = user_goal[0]
else:
    fitness_goal = "Build Muscle"


# =========================
# RECOMMENDED WORKOUT PLAN
# =========================

st.subheader("📋 Recommended Workout Plan")


if fitness_goal == "Build Muscle":

    workout_plan = {
        "Monday": "Chest + Triceps",
        "Tuesday": "Back + Biceps",
        "Wednesday": "Legs",
        "Thursday": "Shoulders + Abs",
        "Friday": "Chest + Back",
        "Saturday": "Legs + Arms",
        "Sunday": "Rest"
    }

elif fitness_goal == "Lose Fat":

    workout_plan = {
        "Monday": "Full Body + Cardio",
        "Tuesday": "Upper Body",
        "Wednesday": "Cardio + Abs",
        "Thursday": "Lower Body",
        "Friday": "Full Body",
        "Saturday": "Cardio + Abs",
        "Sunday": "Rest"
    }

else:

    workout_plan = {
        "Monday": "Full Body",
        "Tuesday": "Cardio",
        "Wednesday": "Upper Body",
        "Thursday": "Rest",
        "Friday": "Lower Body",
        "Saturday": "Full Body + Cardio",
        "Sunday": "Rest"
    }


plan_data = pd.DataFrame(
    list(workout_plan.items()),
    columns=["Day", "Workout"]
)

st.dataframe(
    plan_data,
    use_container_width=True,
    hide_index=True
)


# =========================
# LOG WORKOUT
# =========================

st.subheader("📝 Log Workout")

exercise_name = st.selectbox(
    "Exercise",
    [
        "Bench Press",
        "Squat",
        "Deadlift",
        "Lat Pulldown",
        "Barbell Row",
        "Shoulder Press",
        "Bicep Curl",
        "Tricep Pushdown",
        "Leg Press",
        "Lateral Raise"
    ]
)


sets = st.number_input(
    "Sets",
    min_value=1,
    max_value=10,
    value=3,
    step=1
)


reps = st.number_input(
    "Reps",
    min_value=1,
    max_value=50,
    value=10,
    step=1
)


weight = st.number_input(
    "Weight (kg)",
    min_value=0.0,
    max_value=500.0,
    value=0.0,
    step=0.5
)


notes = st.text_area(
    "Notes",
    placeholder="Optional notes about this exercise..."
)


# =========================
# SAVE WORKOUT
# =========================

if st.button("💾 Save Workout"):

    save_workout_log(
        user_id,
        exercise_name,
        sets,
        reps,
        weight,
        notes
    )

    st.success(
        f"{exercise_name} saved successfully! 💪"
    )


# =========================
# TODAY'S WORKOUTS
# =========================

st.subheader("📋 Today's Workouts")

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

query = """
    SELECT
        exercise_name AS Exercise,
        sets AS Sets,
        reps AS Reps,
        weight AS Weight,
        notes AS Notes
    FROM workout_logs
    WHERE user_id = ?
    AND date = DATE('now')
    ORDER BY id DESC
"""

workouts = pd.read_sql_query(
    query,
    connection,
    params=(user_id,)
)

connection.close()


# =========================
# DISPLAY WORKOUTS
# =========================

if workouts.empty:

    st.info(
        "No workouts logged today."
    )

else:

    st.dataframe(
        workouts,
        use_container_width=True,
        hide_index=True
    )


    # =========================
    # WORKOUT SUMMARY
    # =========================

    total_sets = workouts["Sets"].sum()
    total_reps = workouts["Reps"].sum()

    total_volume = (
        workouts["Sets"]
        * workouts["Reps"]
        * workouts["Weight"]
    ).sum()


    st.subheader("📊 Today's Workout Summary")

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Total Sets",
            int(total_sets)
        )


    with col2:

        st.metric(
            "Total Reps",
            int(total_reps)
        )


    with col3:

        st.metric(
            "Training Volume",
            f"{total_volume:.0f} kg"
        )