import sqlite3
from datetime import datetime, timedelta

import streamlit as st
import extra_streamlit_components as stx

from database import (
    create_database,
    authenticate_user,
    register_user,
    get_user,
    get_user_by_email,
    set_user_credentials,
    create_auth_session,
    get_user_by_session_token,
    revoke_auth_session,
)

st.set_page_config(
    page_title="Fitness App",
    page_icon="??",
    layout="wide"
)

create_database()

# -------------------------
# PERSISTENT LOGIN COOKIES
# -------------------------

AUTH_COOKIE_NAME = "fitness_app_session"
SESSION_DURATION_DAYS = 7

cookie_manager = stx.CookieManager(
    key="fitness_auth_cookie_read"
)
browser_cookies = cookie_manager.cookies

# Restore a valid login after a browser refresh or new Streamlit session.
if not st.session_state.get("authenticated", False):
    saved_token = browser_cookies.get(AUTH_COOKIE_NAME)

    if saved_token:
        saved_user = get_user_by_session_token(saved_token)

        if saved_user:
            st.session_state.user_id = saved_user["id"]
            st.session_state.authenticated = True
            st.session_state.user_name = saved_user["name"]
            st.session_state.user_email = saved_user["email"]
            st.session_state["_fitness_session_token"] = saved_token
        else:
            cookie_manager.delete(
                AUTH_COOKIE_NAME,
                key="fitness_auth_cookie_clear"
            )

def start_authenticated_session(user):
    """Start a seven-day persistent login for an authenticated user."""
    token = create_auth_session(
        user["id"],
        duration_days=SESSION_DURATION_DAYS
    )

    cookie_manager.set(
        AUTH_COOKIE_NAME,
        token,
        key="fitness_auth_cookie_set",
        path="/",
        expires_at=datetime.now() + timedelta(days=SESSION_DURATION_DAYS),
        secure=False,
        same_site="strict",
    )

    st.session_state.user_id = user["id"]
    st.session_state.authenticated = True
    st.session_state.user_name = user["name"]
    st.session_state.user_email = user["email"]
    st.session_state["_fitness_session_token"] = token


st.title("?? Fitness App")
st.caption("Your personal fitness, nutrition and workout companion")

# -------------------------
# LOGGED-IN HOME
# -------------------------

if st.session_state.get("authenticated", False):

    st.sidebar.success(
        f"Logged in as {st.session_state.get('user_name', 'User')}"
    )

    if st.sidebar.button("Log out"):
        session_token = (
            st.session_state.get("_fitness_session_token")
            or browser_cookies.get(AUTH_COOKIE_NAME)
        )

        if session_token:
            revoke_auth_session(session_token)

        if cookie_manager.get(AUTH_COOKIE_NAME):
            cookie_manager.delete(
                AUTH_COOKIE_NAME,
                key="fitness_auth_cookie_logout"
            )

        for key in [
            "user_id",
            "authenticated",
            "user_name",
            "user_email",
            "_fitness_session_token",
        ]:
            st.session_state.pop(key, None)

        st.rerun()

    st.subheader(
        f"Welcome, {st.session_state.get('user_name', 'User')}!"
    )

    st.success("You are logged in successfully.")

    st.info(
        "Use the pages listed in the sidebar to access your "
        "Dashboard, Nutrition, Workout, Progress, Learn and Profile."
    )

    st.write("Your fitness journey starts here!")

# -------------------------
# LOGIN AND REGISTRATION
# -------------------------

else:

    st.write("Please log in or create an account to continue.")

    existing_profile = get_user(1)
    can_link_existing = (
        existing_profile is not None
        and not existing_profile["email"]
        and not existing_profile["password_hash"]
    )

    tab_names = ["Login", "Create Account"]

    if can_link_existing:
        tab_names.append("Connect Existing Profile")

    tabs = st.tabs(tab_names)

    # -------------------------
    # LOGIN
    # -------------------------

    with tabs[0]:

        st.subheader("Login")

        with st.form("login_form"):

            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")

            login_clicked = st.form_submit_button(
                "Login",
                type="primary"
            )

        if login_clicked:

            user = authenticate_user(email, password)

            if user:

                start_authenticated_session(user)

                st.success("Login successful!")

            else:
                st.error("Invalid email or password.")

    # -------------------------
    # CREATE ACCOUNT
    # -------------------------

    with tabs[1]:

        st.subheader("Create a New Account")

        with st.form("register_form"):

            name = st.text_input("Full name")
            new_email = st.text_input("Email address")
            new_password = st.text_input(
                "Create password",
                type="password"
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            st.markdown("**Fitness Profile**")

            age = st.number_input(
                "Age", min_value=13, max_value=100, value=18
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other", "Prefer not to say"]
            )

            height = st.number_input(
                "Height (cm)", min_value=100.0,
                max_value=250.0, value=170.0
            )

            weight = st.number_input(
                "Current weight (kg)", min_value=25.0,
                max_value=300.0, value=70.0
            )

            goal_weight = st.number_input(
                "Goal weight (kg)", min_value=25.0,
                max_value=300.0, value=70.0
            )

            fitness_goal = st.selectbox(
                "Fitness goal",
                [
                    "Build Muscle",
                    "Lose Fat",
                    "Maintain Fitness",
                    "Improve Strength",
                    "General Fitness"
                ]
            )

            activity_level = st.selectbox(
                "Activity level",
                [
                    "Sedentary",
                    "Lightly Active",
                    "Moderately Active",
                    "Very Active",
                    "Extremely Active"
                ]
            )

            register_clicked = st.form_submit_button(
                "Create Account",
                type="primary"
            )

        if register_clicked:

            if new_password != confirm_password:
                st.error("Passwords do not match.")

            else:

                try:

                    new_user_id = register_user(
                        name=name,
                        email=new_email,
                        password=new_password,
                        age=int(age),
                        gender=gender,
                        height=height,
                        weight=weight,
                        goal_weight=goal_weight,
                        fitness_goal=fitness_goal,
                        activity_level=activity_level
                    )

                    new_user = get_user(new_user_id)
                    start_authenticated_session(new_user)

                    st.success("Account created successfully!")

                except sqlite3.IntegrityError:
                    st.error("This email is already registered.")

                except ValueError as error:
                    st.error(str(error))

                except Exception:
                    st.error(
                        "Account creation failed. Please try again."
                    )

    # -------------------------
    # CONNECT EXISTING PROFILE
    # -------------------------

    if can_link_existing:

        with tabs[2]:

            st.subheader("Connect Your Existing Profile")

            st.info(
                f"Existing profile found: {existing_profile['name']}. "
                "Connecting it will preserve its existing fitness history."
            )

            st.warning(
                "Complete this setup yourself before making the app public."
            )

            with st.form("link_profile_form"):

                owner_email = st.text_input("Your email address")
                owner_password = st.text_input(
                    "Create password",
                    type="password"
                )
                owner_confirm = st.text_input(
                    "Confirm password",
                    type="password"
                )

                link_clicked = st.form_submit_button(
                    "Connect Existing Profile",
                    type="primary"
                )

            if link_clicked:

                if owner_password != owner_confirm:
                    st.error("Passwords do not match.")

                else:

                    try:

                        set_user_credentials(
                            1,
                            owner_email,
                            owner_password
                        )

                        user = get_user(1)

                        start_authenticated_session(user)

                        st.success("Existing profile connected!")

                    except ValueError as error:
                        st.error(str(error))

                    except sqlite3.IntegrityError:
                        st.error("This email is already registered.")

                    except Exception:
                        st.error(
                            "Could not connect the profile. Please try again."
                        )
