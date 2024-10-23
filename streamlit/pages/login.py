import streamlit as st
import mysql.connector
from passlib.context import CryptContext

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

st.set_page_config(
    page_title="Document Details",
    # layout="wide",
    initial_sidebar_state="collapsed"
)

# Database connection
def create_connection():
    """Create a database connection."""
    try:
        connection = mysql.connector.connect(
            host='database-1.cdwumcckkqqt.us-east-1.rds.amazonaws.com',
            user='admin',
            password='amazonrds7245',
            database='gaia_benchmark_dataset_validation'
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error connecting to database: {err}")
        return None

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Authenticate user
def authenticate_user(username, password, user_type):
    connection = create_connection()
    if connection is not None:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT username, password, user_type FROM login WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and verify_password(password, user['password']) and user_type == user['user_type']:
            return user
    return None

# Main Streamlit app
def main():
    st.header("Login Page")

    username = st.text_input("Username", key='uname')
    password = st.text_input("Password", type="password", key='pword')
    user_type = st.selectbox("Choose User type", options=['user', 'admin'], key='select_user_type')

    if st.button("Login", key='login'):
        user = authenticate_user(username, password, user_type)
        
        if user:
            st.success(f"Welcome, {user['username']}!")
            st.session_state.username = username
            st.session_state.user_type = user_type
            if user_type == 'user':
                st.switch_page("pages/user_landing.py")
            elif user_type == 'admin':
                st.switch_page("pages/admin.py")
        else:
            st.error("Invalid username, password, or user type!")

    if st.button("Create User", key='create_user'):
        st.switch_page("pages/create_user.py")  # Redirect to the create user page

if __name__ == "__main__":
    main()
