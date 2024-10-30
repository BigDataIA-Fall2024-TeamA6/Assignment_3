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

API_BASE_URL = "http://localhost:8000"

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

# Updated function to get image details from FastAPI
def get_image_details_from_fastapi(image_key):
    try:
        response = requests.get(f"{API_BASE_URL}/image-details/{image_key}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching image details: {str(e)}")
        return {
            "title": "Untitled",
            "pdf_summary": "No summary available.",
            "nvidia_summary": "",
            "image_link": "",
            "pdf_link": ""
        }

def main():
    # Create three columns with specific ratios to push logout to the right
    left_col, middle_col, right_col = st.columns([3, 8, 3])
    
    # Back button in left column
    with left_col:
        if st.button("← Back to Gallery"):
            st.session_state.selected_image = None
            st.session_state.selected_details = None
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
        
        # 
    
    # Fetch image details from FastAPI
    details = get_image_details_from_fastapi(st.session_state.selected_image)
    
    # Create two columns for image and details
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Fetch and display the selected image from FastAPI
        img = load_image_from_fastapi(st.session_state.selected_image)
        if img:
            st.image(img, use_column_width=True)

    with col2:
        # Display the title and details
        st.title(details.get('title', 'Untitled'))
        
        # Display PDF link if available
        if details.get('pdf_link'):
            st.markdown(f"[View PDF Document]({details['pdf_link']})")
        
        # Add "Ask me a Question" button with custom styling
        st.markdown("""
            <style>
            .stButton > button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
                font-weight: bold;
                margin-top: 20px;
            }
            .stButton > button:hover {
                background-color: #45a049;
            }
            </style>
        """, unsafe_allow_html=True)
        
        if st.button("Ask me a Question"):
            st.session_state.current_document = st.session_state.selected_image
            image_name = st.session_state.selected_image
            # # Define the base URL and the PDF key
            # base_url = "https://bdia-assignment-3.s3.us-east-1.amazonaws.com/bdia-assignment-3/"
            # pdf_key = "beyond-active-and-passive"

            # # Concatenate the strings to form the complete PDF link
            # pdf_link = base_url + pdf_key + ".pdf"
            # st.write(pdf_link)
            st.switch_page("pages/qa_interface.py")

    # Add summaries section below
    st.header("PDF Summary")
    st.write(st.session_state.get('nvidia_summary'))
    
    # if details.get('nvidia_summary'):
    #     st.header("NVIDIA Summary")
    #     st.write(st.session_state.get('nvidia_summary'))

if __name__ == "__main__":
    main()