import streamlit as st
import requests  # To send API requests

# Function to send API request to create a new user
def create_new_user(first_name, last_name, username, password):
    api_url = "http://localhost:8000/create_user/"  # FastAPI endpoint

    # Payload with user data
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "password": password
    }

    # Send POST request to FastAPI
    response = requests.post(api_url, json=payload)

    # Check the response from FastAPI
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(response.json().get("detail", "Unknown error"))

# Function for the create new user page
def create_account_page():
    st.title("Create New User Account")

    # Input fields for account creation
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    username = st.text_input("Username", placeholder="example@mail.com")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    # Handle account creation
    with col1:
        submit_button = st.button("Create Account")
        if submit_button:
            if first_name and last_name and username and password:
                try:
                    response = create_new_user(first_name, last_name, username, password)
                    st.success(f"Account created for {first_name} {last_name} ({username})!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("All fields are required!")
    
    with col2:
        if st.button("Back to Login"):
            st.switch_page("pages/login.py")  # Placeholder for page navigation

if __name__ == "__main__":
    create_account_page()
