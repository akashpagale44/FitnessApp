
import sqlite3
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st


# =========================
# DATABASE AND CURRENT USER
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "fitness.db"

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

user_id = st.session_state.user_id


def get_connection():
    """Connect to the fitness database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


st.title("📈 Progress")
st.write("Track your weight and monitor your progress over time.")


# =========================
# GET USER PROFILE
# =========================

connection = get_connection()

try:
    user_data = connection.execute(
        """
        SELECT weight, goal_weight
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()
finally:
    connection.close()

if user_data is None:
    st.error("Please create your profile first.")
    st.stop()

current_profile_weight = float(user_data["weight"] or 72.0)
goal_weight = float(user_data["goal_weight"] or 75.0)


# =========================
# LOG TODAY'S WEIGHT
# =========================

st.subheader("⚖️ Log Today's Weight")

with st.form("weight_form"):
    weight = st.number_input(
        "Weight (kg)",
        min_value=30.0,
        max_value=250.0,
        value=current_profile_weight,
        step=0.1,
        format="%.1f"
    )

    save_weight = st.form_submit_button("💾 Save Weight")

if save_weight:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO weight_logs (user_id, date, weight)
            VALUES (?, ?, ?)
            """,
            (user_id, date.today().isoformat(), weight)
        )

        cursor.execute(
            """
            UPDATE users
            SET weight = ?
            WHERE id = ?
            """,
            (weight, user_id)
        )

        connection.commit()
        st.success("Weight saved and profile updated successfully! 📈")

    except sqlite3.Error as error:
        connection.rollback()
        st.error(f"Could not save your weight: {error}")

    finally:
        connection.close()

    st.rerun()


# =========================
# GET WEIGHT HISTORY
# =========================

st.subheader("📊 Weight Progress")

connection = get_connection()

try:
    weight_data = pd.read_sql_query(
        """
        SELECT id, date, weight
        FROM weight_logs
        WHERE user_id = ?
        ORDER BY date ASC, id ASC
        """,
        connection,
        params=(user_id,)
    )
finally:
    connection.close()


# =========================
# PROGRESS SUMMARY
# =========================

if weight_data.empty:
    st.info(
        "No weight history available yet. "
        "Save your weight above to start tracking."
    )
    st.stop()

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
)

# Sort using real dates, not formatted date strings.
weight_data = weight_data.sort_values(
    ["date", "id"],
    ascending=[True, True]
).reset_index(drop=True)

if weight_data.empty:
    st.info("No valid weight records are available.")
    st.stop()

starting_weight = float(weight_data.iloc[0]["weight"])
latest_weight = float(weight_data.iloc[-1]["weight"])
weight_change = latest_weight - starting_weight

# Calculate progress toward the goal.
total_goal_distance = goal_weight - starting_weight

if abs(total_goal_distance) < 0.001:
    progress = (
        100.0
        if abs(latest_weight - goal_weight) < 0.001
        else 0.0
    )
else:
    progress = (
        (latest_weight - starting_weight)
        / total_goal_distance
    ) * 100

    progress = max(0.0, min(100.0, progress))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Starting Weight", f"{starting_weight:.1f} kg")

with col2:
    st.metric("Current Weight", f"{latest_weight:.1f} kg")

with col3:
    st.metric("Goal Weight", f"{goal_weight:.1f} kg")

with col4:
    st.metric("Weight Change", f"{weight_change:+.1f} kg")


# =========================
# GOAL PROGRESS
# =========================

st.subheader("🎯 Goal Progress")

st.progress(progress / 100)

st.write(
    f"You are approximately **{progress:.0f}%** "
    "toward your weight goal."
)


# =========================
# WEIGHT CHART
# =========================

st.subheader("📈 Weight Chart")

# Keep the latest entry for each calendar day.
# The data is sorted chronologically before plotting.
chart_data = (
    weight_data
    .assign(calendar_date=weight_data["date"].dt.date)
    .drop_duplicates(subset=["calendar_date"], keep="last")
    .sort_values("calendar_date")
    .set_index("date")[["weight"]]
)

st.line_chart(
    chart_data,
    y="weight",
    x_label="Date",
    y_label="Weight (kg)"
)


# =========================
# WEIGHT HISTORY
# =========================

st.subheader("📋 Weight History")

display_data = weight_data[
    ["date", "weight"]
].copy()

display_data["date"] = display_data["date"].dt.strftime(
    "%d %b %Y"
)

display_data["weight"] = display_data["weight"].round(1)

# Display newest entries first in the table.
display_data = display_data.iloc[::-1].reset_index(drop=True)

display_data.columns = ["Date", "Weight (kg)"]

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)
