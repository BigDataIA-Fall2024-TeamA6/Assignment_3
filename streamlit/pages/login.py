import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Document Details",
    initial_sidebar_state="collapsed"
)

# Main Streamlit app
def main():
    st.header("Login Page")

    username = st.text_input("Username", key='uname')
    password = st.text_input("Password", type="password", key='pword')

    if st.button("Login", key='login'):
        # Send request to FastAPI for authentication
        response = requests.post("http://localhost:8000/login", json={"username": username, "password": password})

        if response.status_code == 200:
            user_data = response.json()
            st.success(f"Welcome, {user_data['username']}!")
            st.session_state.username = username
            st.switch_page("pages/user_landing.py")
        else:
            st.error("Invalid username or password!")

    if st.button("Create User", key='create_user'):
        st.switch_page("pages/create_user.py")  # Redirect to the create user page

if __name__ == "__main__":
    main()
