from authentification import *
from dashboard import dashboard_page
import streamlit as st

# Main app
def main():

    # Initialize database
    init_db()

    # Session state management
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.page = 'login'

    # Navigation
    if st.session_state.logged_in:
        col1, col2 = st.columns([8, 1])  # 8:1 ratio, so button sticks right
        with col2:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.page = "login"
                st.rerun()

    # Pages
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.page == 'dashboard':
            dashboard_page()
        elif st.session_state.page == 'user_management' and st.session_state.user[2] == 'admin':
            user_management_page()


if __name__ == "__main__":
    main()