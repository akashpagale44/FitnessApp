import streamlit as st
from database import save_user, get_user


st.title("👤 Profile")

st.write("Manage your personal fitness information.")


# -------------------------
# Current Profile
# -------------------------

user = get_user(1)

if user:

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

    st.write(
        f"**Gender:** {user['gender']}"
    )

    st.write(
        f"**Activity Level:** {user['activity_level']}"
    )

    st.divider()


# -------------------------
# Create New Profile
# -------------------------

st.subheader("📝 Create Profile")

st.info(
    "For the current project demo, creating a new profile "
    "will add a new user to the database."
)

name = st.text_input(
    "Name"
)

age = st.number_input(
    "Age",
    min_value=10,
    max_value=100,
    value=19
)

gender = st.selectbox(
    "Gender",
    [
        "Male",
        "Female",
        "Other"
    ]
)

height = st.number_input(
    "Height (cm)",
    min_value=100.0,
    max_value=250.0,
    value=183.0
)

weight = st.number_input(
    "Current Weight (kg)",
    min_value=30.0,
    max_value=250.0,
    value=70.0
)

goal_weight = st.number_input(
    "Goal Weight (kg)",
    min_value=30.0,
    max_value=250.0,
    value=75.0
)

fitness_goal = st.selectbox(
    "Fitness Goal",
    [
        "Lose Fat",
        "Build Muscle",
        "Maintain Weight"
    ]
)

activity_level = st.selectbox(
    "Activity Level",
    [
        "Sedentary",
        "Lightly Active",
        "Moderately Active",
        "Very Active"
    ]
)


# -------------------------
# Save Profile
# -------------------------

if st.button("Create Profile", type="primary"):

    if name.strip() == "":
        st.error("Please enter your name.")

    else:

        user_id = save_user(
            name,
            age,
            gender,
            height,
            weight,
            goal_weight,
            fitness_goal,
            activity_level
        )

        st.success(
            "Profile created successfully! 🎉"
        )

        st.write(
            f"Your User ID: **{user_id}**"
        )