import os
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_BASE_URL = "http://localhost:8000"  # Your FastAPI base URL


# Display welcome message
if "username" in st.session_state:
    st.header(f"Welcome {st.session_state.username}!")

# Custom CSS for slide-out info card with button
st.markdown("""
<style>
.image-container {
    position: relative;
    display: inline-block;
    width: 100%;
    overflow: hidden;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.image-container:hover {
    transform: translateY(-5px);
}

.image-main {
    width: 100%;
    display: block;
    border-radius: 8px;
}

.info-card {
    position: absolute;
    bottom: -100%;
    left: 0;
    right: 0;
    background: linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.98));
    padding: 12px;
    transition: bottom 0.3s ease;
    border-top: 1px solid rgba(0,0,0,0.1);
}

.image-container:hover .info-card {
    bottom: 0;
}

.info-title {
    font-size: 1em;
    font-weight: bold;
    margin-bottom: 8px;
    color: #333;
}

.info-description {
    font-size: 0.9em;
    color: #666;
    line-height: 1.4;
    margin-bottom: 12px;
}

.view-details-container {
    width: 100%;
    text-align: center;
}

.stButton {
    width: 100%;
    margin-top: 8px;
}

.stButton > button {
    width: 100%;
    background-color: #0066cc !important;
    color: white !important;
    border-radius: 4px !important;
    padding: 6px 12px !important;
    font-size: 0.85em !important;
    border: none !important;
    cursor: pointer !important;
    opacity: 1 !important;
    position: relative !important;
}

.stButton > button:hover {
    background-color: #0052a3 !important;
    border: none !important;
}

.stMarkdown {
    transition: opacity 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# Function to get image from FastAPI
def load_image_from_fastapi(image_key):
    try:
        print(f"Requesting image with key: {image_key}")  # Debugging log
        response = requests.get(f"{API_BASE_URL}/fetch-image/{image_key}")
        print(f"Response status: {response.status_code}")  # Log the response status
        print(f"Response content: {response.text}")
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
        print(f"Requesting details for image key: {image_key}")
        response = requests.get(f"{API_BASE_URL}/image-details/{image_key}")
        response.raise_for_status()
        details = response.json()
        return details.get("title"), details.get("brief")
    except requests.RequestException as e:
        st.error(f"Error fetching image details: {str(e)}")
        return "Untitled", "No description available."

# Function to create the image with information
def create_image_with_info(image_base64, title, description):
    return f"""
    <div class="image-container">
        <img src="data:image/png;base64,{image_base64}" class="image-main">
        <div class="info-card">
            <div class="info-title">{title}</div>
            <div class="info-description">{description}</div>
            <div class="view-details-container"></div>
        </div>
    </div>
    """

# Function to query NVIDIA API for summary
def get_nvidia_summary(title, description):
    NVIDIA_API_URL = "https://ai.api.nvidia.com/v1/vlm/nvidia/neva-22b"  # Replace with your actual endpoint
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")  # Replace with your actual API key

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "role": "user",
                "content": f'Write a 5 line summary for the following title and summary: Title: {title}. Summary: {description}'
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.20,
        "top_p": 0.70,
        "seed": 0,
        "stream": False
    }

    try:
        response = requests.post(NVIDIA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        
        # Extract the summary from the response
        summary_content = json_response['choices'][0]['message']['content']
        return summary_content 
        
    except requests.RequestException as e:
        st.error(f"Error fetching summary from NVIDIA API: {str(e)}")
        return "Error retrieving summary."

# Updated handle button click function
def handle_click(image_file, title, description):
    st.session_state.selected_image = image_file
    st.session_state.selected_title = title
    st.session_state.selected_description = description
    
    # Fetch NVIDIA summary
    nvidia_summary = get_nvidia_summary(title, description)

    # Store NVIDIA summary in session state or display it directly
    st.session_state.nvidia_summary = nvidia_summary
    # st.session_state.selected_nvidia_summary = nvidia_summary

    # Optionally, switch to another page or display the details directly
    st.write("NVIDIA Summary:", nvidia_summary)  # Display the summary on the current page
    st.switch_page("pages/doc_detail.py")

# Function to create the image grid from FastAPI
def create_image_grid(num_images_per_row=5):
    try:
        response = requests.get(f"{API_BASE_URL}/list-images")
        response.raise_for_status()
        image_files = response.json()

        for i in range(0, len(image_files), num_images_per_row):
            cols = st.columns(num_images_per_row)
            for j, image_file in enumerate(image_files[i:i + num_images_per_row]):
                with cols[j]:
                    # Fetch image from FastAPI
                    img = load_image_from_fastapi(image_file)
                    if img:
                        img_base64 = image_to_base64(img)
                        # Fetch title and description from FastAPI
                        title, description = get_image_details_from_fastapi(image_file)
                        st.markdown(
                            create_image_with_info(
                                img_base64,
                                title,
                                description.replace('\n', '<br>')
                            ),
                            unsafe_allow_html=True
                        )
                        if st.button("View Details", key=f"btn_{image_file}"):
                            handle_click(image_file, title, description)
    except requests.RequestException as e:
        st.error(f"Error fetching image list: {str(e)}")
        
# Function to convert an image to base64
def image_to_base64(image):
    try:
        buffered = BytesIO()
        image.save(buffered, format="PNG")  # Save the image to the buffer in PNG format
        return base64.b64encode(buffered.getvalue()).decode("utf-8")  # Encode the image to base64
    except Exception as e:
        st.error(f"Error converting image to base64: {str(e)}")
        return None


# Initialize session state variables if they don't exist
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'selected_title' not in st.session_state:
    st.session_state.selected_title = None
if 'selected_description' not in st.session_state:
    st.session_state.selected_description = None


# Call the function to create the grid from FastAPI
create_image_grid()
