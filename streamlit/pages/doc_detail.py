import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# Set Streamlit configuration
st.set_page_config(
    page_title="Document Details",
    initial_sidebar_state="collapsed"
)

API_BASE_URL = "http://localhost:8000"  # Replace with your FastAPI URL if deployed

# Redirect to landing if no image is selected
if not st.session_state.get('selected_image'):
    st.switch_page("pages/user_landing.py")

# Function to get image from FastAPI
def load_image_from_fastapi(image_key):
    try:
        response = requests.get(f"{API_BASE_URL}/fetch-image/{image_key}")
        response.raise_for_status()
        image_base64 = response.json().get("image_base64")
        img = Image.open(BytesIO(base64.b64decode(image_base64)))
        return img
    except requests.RequestException as e:
        st.error(f"Error fetching image: {str(e)}")
        return None

# Function to get image details from FastAPI
def get_image_details_from_fastapi(image_key):
    try:
        response = requests.get(f"{API_BASE_URL}/image-details/{image_key}")
        response.raise_for_status()
        details = response.json()
        return details.get("title"), details.get("brief")
    except requests.RequestException as e:
        st.error(f"Error fetching image details: {str(e)}")
        return "Untitled", "No description available."

def main():
    # Create three columns with specific ratios to push logout to the right
    left_col, middle_col, right_col = st.columns([3, 8, 3])
    
    # Back button in left column
    with left_col:
        if st.button("← Back to Gallery"):
            st.session_state.selected_image = None
            st.session_state.selected_title = None
            st.session_state.selected_description = None
            st.switch_page("pages/user_landing.py")
    
    # Empty middle column to create space
    with middle_col:
        st.empty()
    
    # Logout button in right column
    with right_col:
        st.markdown("""
        <style>
        div[data-testid="column"]:nth-child(3) .stButton {
            display: flex;
            justify-content: flex-end;
        }
        div[data-testid="column"]:nth-child(3) .stButton > button {
            background-color: #dc3545;
            color: white;
            border: none;
            padding: 0.2rem 1rem;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        div[data-testid="column"]:nth-child(3) .stButton > button:hover {
            background-color: #c82333;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.username = None
            st.switch_page("pages/login.py")
    
    # Fetch image details from FastAPI
    title, description = get_image_details_from_fastapi(st.session_state.selected_image)
    
    # Create two columns for image and details
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Fetch and display the selected image from FastAPI
        img = load_image_from_fastapi(st.session_state.selected_image)
        if img:
            st.image(img, use_column_width=True)

    with col2:
        # Display the title and basic info fetched from FastAPI
        st.title(title)
        st.write("Category: Sample Category")  # Modify if the category is stored in Snowflake
        st.write("Date Added: January 1, 2024")  # Modify if the date is available
        st.write("Resolution: 1920x1080")  # Modify based on the actual data
    
    # Add summary section below
    st.header("Summary")
    st.write(description)

if __name__ == "__main__":
    main()
