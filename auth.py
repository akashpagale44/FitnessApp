import streamlit as st
import extra_streamlit_components as stx

from database import get_user_by_session_token

AUTH_COOKIE_NAME = "fitness_app_session"


def restore_login_session():
    """Restore a valid login from the browser cookie."""
    if st.session_state.get("authenticated", False):
        return True

    cookie_manager = stx.CookieManager(
        key="fitness_auth_cookie_read"
    )

    browser_cookies = cookie_manager.cookies or {}
    saved_token = browser_cookies.get(AUTH_COOKIE_NAME)

    if not saved_token:
        return False

    saved_user = get_user_by_session_token(saved_token)

    if saved_user is None:
        return False

    st.session_state.user_id = saved_user["id"]
    st.session_state.authenticated = True
    st.session_state.user_name = saved_user["name"]
    st.session_state.user_email = saved_user["email"]
    st.session_state["_fitness_session_token"] = saved_token

    return True
