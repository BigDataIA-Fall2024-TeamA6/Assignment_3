import streamlit as st
from PIL import Image
import os

st.set_page_config(
    #page_title="Document Details",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Display welcome message
if "username" in st.session_state and st.session_state.user_type == "user":
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

def load_local_image(image_name):
    image_path = os.path.join("D:/DAMG7245/Assignment_3/streamlit/images", image_name)
    return Image.open(image_path)

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

def image_to_base64(image):
    import base64
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def handle_click(image_file, title, description):
    st.session_state.selected_image = image_file
    st.session_state.selected_title = title
    st.session_state.selected_description = description
    st.switch_page("pages/doc_detail.py")

def create_image_grid(image_folder, num_images_per_row=5):
    image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
    
    titles = [f"Image {i + 1}" for i in range(len(image_files))]
    descriptions = [
        f"Brief summary for image {i + 1}. Key features and highlights shown here."
        for i in range(len(image_files))
    ]

    for i in range(0, len(image_files), num_images_per_row):
        cols = st.columns(num_images_per_row)
        for j, image_file in enumerate(image_files[i:i + num_images_per_row]):
            with cols[j]:
                img = load_local_image(image_file)
                img_base64 = image_to_base64(img)
                
                # Create unique index for each image
                image_index = i + j
                
                # Display the image container
                st.markdown(
                    create_image_with_info(
                        img_base64,
                        titles[image_index],
                        descriptions[image_index].replace('\n', '<br>')
                    ),
                    unsafe_allow_html=True
                )
                
                # Add the view details button using Streamlit's native button
                if st.button("View Details", key=f"btn_{image_index}"):
                    handle_click(
                        image_file,
                        titles[image_index],
                        descriptions[image_index]
                    )

# Initialize session state variables if they don't exist
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'selected_title' not in st.session_state:
    st.session_state.selected_title = None
if 'selected_description' not in st.session_state:
    st.session_state.selected_description = None

# Call the function to create the grid
image_folder = "D:/DAMG7245/Assignment_3/streamlit/images"
create_image_grid(image_folder)