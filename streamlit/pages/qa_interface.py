import base64
from datetime import datetime
import os
from fpdf import FPDF
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
 
# Load environment variables from .env file
load_dotenv()
 
# Set up the page configuration
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)
 
# Initialize settings
def initialize_settings():
    Settings.embed_model = NVIDIAEmbedding(model="nvidia/nv-embedqa-e5-v5", truncate="END")
    Settings.llm = NVIDIA(model="meta/llama-3.1-8b-instruct")
    Settings.text_splitter = SentenceSplitter(chunk_size=600)
 
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
        temp_file_path = 'streamlit/pages/temp_document.pdf'
        with open(temp_file_path, 'wb') as f:
            f.write(response.content)
        return temp_file_path
    else:
        st.error("Failed to download the PDF.")
        return None
 
def show_pdf(file_path):
    try:
        if not Path(file_path).exists():
            st.error(f"File not found: {file_path}")
            return False
        with open(file_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        pdf_viewer(pdf_content)
        return True
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")
        return False
 
# Function to create a download link for the PDF
def create_pdf_download(st_session_state_notes):
    pdf = FPDF()
    pdf.add_page()
   
    # Title and Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Research Notes", 0, 1, 'C')
   
    # Date
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, datetime.now().strftime("%B %d, %Y"), 0, 1, 'C')
   
    # Add a line separator
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
 
    # Content
    pdf.set_font("Arial", size=12)
   
    queries = st_session_state_notes.split('\n\n---\n\n')
    for query in queries:
        if query.strip():
            lines = query.strip().split('\n')
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, lines[0], 0, 1)  # Query number
            pdf.set_font("Arial", '', 12)
            for line in lines[1:]:
                pdf.multi_cell(0, 10, line)
            pdf.ln(10)
 
    # Generate PDF as bytes
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
   
    # Create base64 encoded download link
    b64 = base64.b64encode(pdf_bytes).decode('latin-1')
    download_link = f'<a href="data:application/pdf;base64,{b64}" download="research_notes_{datetime.now().strftime("%Y%m%d")}.pdf">Download PDF</a>'
   
    return download_link
 
# Custom PDF class with header
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, st.session_state['pdf_key'], 0, 1, 'C')
        self.ln(10)
 
# Main function to run the Streamlit app
def main():
    set_environment_variables()
    initialize_settings()
 
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
        if st.button("Home Page"):
            st.session_state.selected_image = None
            st.session_state.selected_details = None
            st.switch_page("pages/user_landing.py")
 
    col1, col2 = st.columns([1, 2])
 
    with col1:
        st.title("Multimodal RAG")
        st.session_state.current_document = st.session_state.selected_image
        pdf_key = st.session_state.selected_image.split('.')[0].split('/')[1]
        st.write(pdf_key)
 
        if pdf_key and st.button("Fetch Document"):
            base_url = "https://bdia-assignment-3.s3.us-east-1.amazonaws.com/Research-Foundation/"
            pdf_link = base_url + pdf_key + ".pdf"
            try:
                pdf_path = download_pdf(pdf_link)
                if pdf_path:
                    documents = load_multimodal_data(pdf_path)
                    st.session_state['index'] = create_index(documents)
                    st.session_state['history'] = []
                    st.session_state['pdf_key'] = pdf_key  # Set the pdf_key in session state
                    st.success("Document fetched and index created!")
                    st.subheader("PDF Preview:")
                    show_pdf(pdf_path)
            except Exception as e:
                st.error(f"Error fetching document: {e}")
 
    with col2:
        if 'index' in st.session_state:
            st.title("Chat")
            if 'history' not in st.session_state:
                st.session_state['history'] = []
            if 'terminal_output' not in st.session_state:
                st.session_state['terminal_output'] = ""
            if 'notes' not in st.session_state:
                st.session_state['notes'] = ""
           
            query_engine = st.session_state['index'].as_query_engine(similarity_top_k=10, streaming=True)
 
            user_input = st.chat_input("Enter your query:")
 
            chat_container = st.container()
            with chat_container:
                for message in st.session_state['history']:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
 
                    # Add each message to the terminal output
                    st.session_state['terminal_output'] += f"{message['role'].capitalize()}: {message['content']}\n"

            if user_input:
                with st.chat_message("user"):
                    st.markdown(user_input)
                st.session_state['history'].append({"role": "user", "content": user_input})
                st.session_state['terminal_output'] += f"User: {user_input}\n"
 
                # Add user input to the terminal output
                st.session_state['terminal_output'] += f"User: {user_input}\n"

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    response = query_engine.query(user_input)
                    for token in response.response_gen:
                        full_response += token
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                st.session_state['history'].append({"role": "assistant", "content": full_response})
                st.session_state['terminal_output'] += f"Assistant: {full_response}\n"
 
           
            if st.button("Clear Chat"):
                st.session_state['history'] = []
                st.session_state['terminal_output'] = "Chat history cleared\n"
                st.session_state['terminal_output'] = ""
                st.rerun()
 
    co1, co2 = st.columns([1, 2])
   
    with co2:
        st.text_area("Terminal Output", value=st.session_state['terminal_output'], height=200, key="terminal_display")
 
        if st.button("Add to Notes"):
            queries = st.session_state['notes'].split('\n\n---\n\n')
            query_number = len(queries) + 1 if st.session_state['notes'] else 1
            new_note = f"Query {query_number}:\n\n{st.session_state['terminal_output'].strip()}\n\n---\n\n"
            st.session_state['notes'] += new_note
            st.session_state['terminal_output'] = ""
            st.success("Added to notes!")
            st.rerun()
 
    st.markdown("""
        <style>
        .clear-notes-button {
            background-color: #FF6347 !important;  /* Tomato red */
            color: white !important;
            border: none !important;
        }
        .clear-notes-button:hover {
            background-color: #FF4500 !important;  /* Darker shade on hover */
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
 
    with co1:
        st.text_area("Notes", value=st.session_state['notes'], height=300, key="notes_display", disabled=True)
 
        col1, col2 = st.columns(2)  # Create two columns for buttons
 
        with col1:
            if st.button("Save Notes to PDF"):
                if st.session_state['notes']:
                    download_html = create_pdf_download(st.session_state['notes'])
                    st.markdown(download_html, unsafe_allow_html=True)
                    st.success("PDF is ready for download!")
                else:
                    st.warning("No notes to save.")
 
        with col2:
            # Add Clear Notes button with custom CSS class
            if st.button("Clear Notes", key="clear_notes_button", help="Clear all saved notes",
                        use_container_width=True,
                        type="secondary",
                        disabled=(st.session_state['notes'] == "")):
                st.session_state['notes'] = ""
                st.rerun()

            # Display terminal output in a text area
            st.text_area("Terminal Output", value=st.session_state['terminal_output'], height=200, key="terminal_display")

            # Add to Notes button
            if st.button("Add to Notes"):
                st.session_state['notes'] += st.session_state['terminal_output']
                st.session_state['terminal_output'] = ""  # Clear the terminal output
                st.success("Added to notes!")
                st.rerun() 

            # Display Notes
            st.text_area("Notes", value=st.session_state['notes'], height=200, key="notes_display", disabled=True)

            # Function to create a download link for the PDF
            def create_download_link(val, filename):
                b64 = base64.b64encode(val)  # val looks like b'...'
                return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

            # Add a button to save notes to PDF
            if st.button("Save Notes to PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                
                # Split the notes into lines and add them to the PDF
                for line in st.session_state['notes'].split('\n'):
                    pdf.cell(0, 10, txt=line, ln=True)
                
                # Generate the PDF
                pdf_output = pdf.output(dest="S").encode("latin-1")
                
                # Create a download link
                html = create_download_link(pdf_output, "my_notes")
                
                # Display the download link
                st.markdown(html, unsafe_allow_html=True)


 
if __name__ == "__main__":
    main()