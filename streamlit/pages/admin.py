import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from pages.db import DBConnection  # Assuming this is in a separate file, e.g., db_connection.py

# Header for the admin page
st.header("Admin")
st.write(f"You are logged in as Admin.")

# Fetch the data from the 'log_tb' table using the DBConnection singleton
def fetch_log_table_data():
    # Get the cursor from the DBConnection instance
    db_instance = DBConnection.get_instance()
    cursor = db_instance.get_cursor()
    
    # Execute query to get data from the 'log_tb' table
    query = "SELECT * FROM log_tb"
    cursor.execute(query)
    
    # Fetch the results and get the column names
    records = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(records, columns=column_names)
    
    return df

# Fetch and display the data from the 'log_tb' table
log_data = fetch_log_table_data()
st.write("Log Table Data:")
st.dataframe(log_data)  # This will display the table in a nice format