import os
import requests
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from pathlib import Path
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA

from document_processors import load_multimodal_data
from utils import set_environment_variables

from dotenv import load_dotenv
from pymilvus import connections

# # Load environment variables from .env file
load_dotenv()

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

# # Connect to Zilliz Cloud
# connections.connect(
#     uri=os.getenv("ZILLIZ_CLOUD_URI"),
#     user=os.getenv("ZILLIZ_CLOUD_USER"),
#     password=os.getenv("ZILLIZ_CLOUD_PASSWORD")
# )

# Set up the page configuration
st.set_page_config(layout="wide")

# Initialize settings
def initialize_settings():
    Settings.embed_model = NVIDIAEmbedding(model="nvidia/nv-embedqa-e5-v5", truncate="END")
    Settings.llm = NVIDIA(model="meta/llama-3.1-405b-instruct")
    Settings.text_splitter = SentenceSplitter(chunk_size=1000)

# Create index from documents
def create_index(documents):
    vector_store = MilvusVectorStore(
        uri=os.getenv("ZILLIZ_CLOUD_URI"),
        user=os.getenv("ZILLIZ_CLOUD_USER"),
        password=os.getenv("ZILLIZ_CLOUD_PASSWORD"),
        collection_name="Assignment3", 
        dim=1024
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_documents(documents, storage_context=storage_context)

def download_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        # Create a temporary file and return its path
        temp_file_path = 'pages/temp_document.pdf'  # You can use tempfile to create a unique temp file
        with open(temp_file_path, 'wb') as f:
            f.write(response.content)
        return temp_file_path
    else:
        st.error("Failed to download the PDF.")
        return None

def show_pdf(file_path):
    try:
        # Check if file exists
        if not Path(file_path).exists():
            st.error(f"File not found: {file_path}")
            return False
        
        # Read the PDF file
        with open(file_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        
        # Display the PDF
        pdf_viewer(pdf_content)
        return True
        
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")
        return False

# Main function to run the Streamlit app
def main():
    set_environment_variables()
    initialize_settings()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.title("Multimodal RAG")
        
        st.session_state.current_document = st.session_state.selected_image
        pdf_key = st.session_state.selected_image.split('.')[0].split('/')[1]
        st.write(pdf_key)
        
        if pdf_key and st.button("Fetch Document"):
            # Define the base URL and the PDF key
            base_url = "https://bdia-assignment-3.s3.us-east-1.amazonaws.com/Research-Foundation/"
            pdf_link = base_url + pdf_key + ".pdf"
            try:
                # Download the PDF file
                pdf_path = download_pdf(pdf_link)
                if pdf_path:
                    # Load document data directly from the downloaded file
                    documents = load_multimodal_data(pdf_path)  # Update this function if necessary
                    st.session_state['index'] = create_index(documents)
                    st.session_state['history'] = []
                    st.success("Document fetched and index created!")

                    # Display the PDF preview
                    st.subheader("PDF Preview:")
                    
                    show_pdf(pdf_path)
                    
            except Exception as e:
                st.error(f"Error fetching document: {e}")

    
    with col2:
        if 'index' in st.session_state:
            st.title("Chat")
            if 'history' not in st.session_state:
                st.session_state['history'] = []
            
            query_engine = st.session_state['index'].as_query_engine(similarity_top_k=20, streaming=True)

            user_input = st.chat_input("Enter your query:")

            # Display chat messages
            chat_container = st.container()
            with chat_container:
                for message in st.session_state['history']:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            if user_input:
                with st.chat_message("user"):
                    st.markdown(user_input)
                st.session_state['history'].append({"role": "user", "content": user_input})
                
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    response = query_engine.query(user_input)
                    for token in response.response_gen:
                        full_response += token
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                st.session_state['history'].append({"role": "assistant", "content": full_response})

            # Add a clear button
            if st.button("Clear Chat"):
                st.session_state['history'] = []
                st.rerun()

if __name__ == "__main__":
    main()