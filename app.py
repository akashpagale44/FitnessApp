import streamlit as st

from database import create_database


# -------------------------
# Page Configuration
# -------------------------

st.set_page_config(
    page_title="Fitness App",
    page_icon="🏋️",
    layout="wide"
)


# -------------------------
# Initialize Database
# -------------------------

create_database()


# -------------------------
# Sidebar Navigation
# -------------------------

st.sidebar.title("🏋️ Fitness App")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Dashboard",
        "Nutrition",
        "Workout",
        "Progress",
        "Learn",
        "Profile"
    ]
)


# -------------------------
# Home Page
# -------------------------

if page == "Home":

    st.title("🏋️ Fitness App")

    st.write("Your all-in-one fitness companion")

    st.info(
        "Select a page from the sidebar to manage your "
        "fitness, nutrition, workouts, progress, and learning."
    )


# -------------------------
# Other Pages
# -------------------------

elif page == "Dashboard":
    st.title("📊 Dashboard")
    st.write("Dashboard page")

elif page == "Nutrition":
    st.title("🥗 Nutrition")
    st.write("Nutrition page")

elif page == "Workout":
    st.title("🏋️ Workout")
    st.write("Workout page")

elif page == "Progress":
    st.title("📈 Progress")
    st.write("Progress page")

elif page == "Learn":
    st.title("📚 Learn")
    st.write("Learning page")

elif page == "Profile":
    st.title("👤 Profile")
    st.write("Profile page")