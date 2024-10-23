import streamlit as st
import mysql.connector
import bcrypt  # Import bcrypt for password hashing

# Connect to the AWS RDS MySQL instance
def create_connection():
    connection = mysql.connector.connect(
        host='database-1.cdwumcckkqqt.us-east-1.rds.amazonaws.com',
        user='admin',
        password='amazonrds7245',
        database='gaia_benchmark_dataset_validation'
    )
    return connection

# Function to create a new user
def create_new_user(first_name, last_name, username, password):
    connection = create_connection()
    cursor = connection.cursor()

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # User type is always set to "user"
    user_type = "user"

    # Insert new user into the 'login' table
    query = """
    INSERT INTO login (fname, lname, username, password, user_type)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (first_name, last_name, username, hashed_password.decode('utf-8'), user_type))
    
    # Commit the transaction and close the connection
    connection.commit()
    cursor.close()
    connection.close()

    return True

# Function for the create new user page
def create_account_page():
    st.title("Create New User Account")

    # Input fields for account creation
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    username = st.text_input("Username", placeholder="example@mail.com")
    password = st.text_input("Password", type="password")


    col1,col2 = st.columns(2)
    # Handle account creation

    with col1:
    # Submit button
        submit_button = st.button("Create Account")
        
        if submit_button:
            if first_name and last_name and username and password:
                try:
                    create_new_user(first_name, last_name, username, password)
                    st.success(f"Account created for {first_name} {last_name} ({username}) as a User!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("All fields are required!")
    
    with col2:
        if st.button("Back to Login"):
            st.switch_page("pages/login.py")
 
if __name__ == "__main__":
    create_account_page()