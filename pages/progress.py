import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import date


st.title("📈 Progress")

st.write("Track your weight and monitor your progress over time.")


# -------------------------
# Get User
# -------------------------

connection = sqlite3.connect(
    Path("data") / "fitness.db"
)

user_data = pd.read_sql_query(
    """
    SELECT weight, goal_weight
    FROM users
    WHERE id = ?
    """,
    connection,
    params=(1,)
)

connection.close()

current_profile_weight = user_data.iloc[0]["weight"]
goal_weight = user_data.iloc[0]["goal_weight"]


# -------------------------
# Add Weight
# -------------------------

st.subheader("⚖️ Log Today's Weight")

weight = st.number_input(
    "Weight (kg)",
    min_value=30.0,
    max_value=250.0,
    value=float(current_profile_weight)
)

if st.button("Save Weight"):

    connection = sqlite3.connect(
        Path("data") / "fitness.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO weight_logs (
            user_id,
            date,
            weight
        )
        VALUES (?, ?, ?)
    """, (
        1,
        date.today().isoformat(),
        weight
    ))

    connection.commit()
    connection.close()

    st.success("Weight saved successfully! 📈")


# -------------------------
# Weight History
# -------------------------

st.subheader("📊 Weight Progress")

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

    st.info("No weight data available yet.")

else:

    starting_weight = weight_data.iloc[0]["weight"]
    latest_weight = weight_data.iloc[-1]["weight"]

    weight_change = latest_weight - starting_weight

    if goal_weight != starting_weight:
        progress = (
            (starting_weight - latest_weight)
            / (starting_weight - goal_weight)
        ) * 100

        progress = max(0, min(100, progress))
    else:
        progress = 100

    # -------------------------
    # Progress Summary
    # -------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Starting Weight",
            f"{starting_weight:.1f} kg"
        )

    with col2:
        st.metric(
            "Current Weight",
            f"{latest_weight:.1f} kg"
        )

    with col3:
        st.metric(
            "Goal Weight",
            f"{goal_weight:.1f} kg"
        )

    with col4:
        st.metric(
            "Weight Change",
            f"{weight_change:+.1f} kg"
        )

    # -------------------------
    # Goal Progress
    # -------------------------

    st.subheader("🎯 Goal Progress")

    st.progress(
        progress / 100
    )

    st.write(
        f"You are approximately **{progress:.0f}%** "
        "toward your weight goal."
    )

    # -------------------------
    # Weight Chart
    # -------------------------

    st.subheader("📈 Weight Chart")

    weight_data["date"] = pd.to_datetime(
        weight_data["date"]
    )

    st.line_chart(
        weight_data.set_index("date")["weight"]
    )

    # -------------------------
    # Weight History
    # -------------------------

    st.subheader("📋 Weight History")

    st.dataframe(
        weight_data,
        use_container_width=True,
        hide_index=True
    )