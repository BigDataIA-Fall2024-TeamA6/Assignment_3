import streamlit as st
from PIL import Image
import os

st.set_page_config(
    page_title="Document Details",
    initial_sidebar_state="collapsed"
)
# # Redirect to login if not logged in
# if not st.session_state.get('logged_in', False):
#     st.switch_page("login.py")

# Redirect to landing if no image is selected
if not st.session_state.get('selected_image'):
    st.switch_page("pages/user_landing.py")

def load_local_image(image_name):
    image_path = os.path.join("D:/DAMG7245/Assignment_3/streamlit/images", image_name)
    return Image.open(image_path)

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
        # Custom CSS to right-align the button
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
    
    # Create two columns for image and details
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Display the selected image
        img = load_local_image(st.session_state.selected_image)
        st.image(img, use_column_width=True)

    with col2:
        # Display the title and basic info
        st.title(st.session_state.selected_title)
        st.write("Category: Sample Category")
        st.write("Date Added: January 1, 2024")
        st.write("Resolution: 1920x1080")

    # Add summary section below
    st.header("Summary")
    st.write(st.session_state.selected_description)

    # Additional details section
    st.header("Additional Information")
    st.write("""
    • Feature 1: Description of feature 1
    • Feature 2: Description of feature 2
    • Feature 3: Description of feature 3
    """)

if __name__ == "__main__":
    main()