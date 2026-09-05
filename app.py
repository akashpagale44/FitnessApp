import streamlit as st
from database import create_database

create_database()

st.set_page_config(
    page_title="Fitness App",
    page_icon="🏋️"
)

st.title("🏋️ Fitness App")
st.write("Your all-in-one fitness companion")
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Nutrition",
        "Workout",
        "Progress",
        "Learn",
        "Profile"
    ]
)