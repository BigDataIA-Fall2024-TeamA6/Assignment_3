import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None

           
def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

st.switch_page("pages/login.py")
