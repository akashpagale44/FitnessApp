import streamlit as st
import sqlite3

from database import get_user


st.title("👤 Profile")

st.write("Manage your personal fitness information.")


# =========================
# CURRENT USER
# =========================

if "user_id" not in st.session_state:
    st.session_state.user_id = 1

user_id = st.session_state.user_id


# =========================
# GET CURRENT PROFILE
# =========================

user = get_user(user_id)

if not user:
    st.error("No profile found. Please create a profile first.")
    st.stop()


# =========================
# CURRENT PROFILE
# =========================

st.subheader("📋 Current Profile")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Name", user["name"])
    st.metric("Age", user["age"])

with col2:
    st.metric("Height", f"{user['height']:.0f} cm")
    st.metric("Weight", f"{user['weight']:.1f} kg")

with col3:
    st.metric("Goal Weight", f"{user['goal_weight']:.1f} kg")
    st.metric("Goal", user["fitness_goal"])

st.write(f"**Gender:** {user['gender']}")
st.write(f"**Activity Level:** {user['activity_level']}")

st.divider()


# =========================
# UPDATE PROFILE
# =========================

st.subheader("✏️ Update Profile")

name = st.text_input(
    "Name",
    value=user["name"]
)

age = st.number_input(
    "Age",
    min_value=10,
    max_value=100,
    value=int(user["age"])
)

gender_options = ["Male", "Female", "Other"]

gender_index = (
    gender_options.index(user["gender"])
    if user["gender"] in gender_options
    else 0
)

gender = st.selectbox(
    "Gender",
    gender_options,
    index=gender_index
)

height = st.number_input(
    "Height (cm)",
    min_value=100.0,
    max_value=250.0,
    value=float(user["height"]),
    step=0.1
)

weight = st.number_input(
    "Current Weight (kg)",
    min_value=30.0,
    max_value=250.0,
    value=float(user["weight"]),
    step=0.1
)

goal_weight = st.number_input(
    "Goal Weight (kg)",
    min_value=30.0,
    max_value=250.0,
    value=float(user["goal_weight"]),
    step=0.1
)

fitness_goals = [
    "Lose Fat",
    "Build Muscle",
    "Maintain Weight"
]

goal_index = (
    fitness_goals.index(user["fitness_goal"])
    if user["fitness_goal"] in fitness_goals
    else 0
)

fitness_goal = st.selectbox(
    "Fitness Goal",
    fitness_goals,
    index=goal_index
)

activity_levels = [
    "Sedentary",
    "Lightly Active",
    "Moderately Active",
    "Very Active"
]

activity_index = (
    activity_levels.index(user["activity_level"])
    if user["activity_level"] in activity_levels
    else 0
)

activity_level = st.selectbox(
    "Activity Level",
    activity_levels,
    index=activity_index
)


# =========================
# SAVE CHANGES
# =========================

if st.button("💾 Save Changes", type="primary"):

    if name.strip() == "":
        st.error("Please enter your name.")

    else:

        connection = sqlite3.connect("data/fitness.db")
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE users
            SET name = ?,
                age = ?,
                gender = ?,
                height = ?,
                weight = ?,
                goal_weight = ?,
                fitness_goal = ?,
                activity_level = ?
            WHERE id = ?
        """, (
            name,
            age,
            gender,
            height,
            weight,
            goal_weight,
            fitness_goal,
            activity_level,
            user_id
        ))

        connection.commit()
        connection.close()

        st.success("Profile updated successfully! 🎉")

        st.rerun()