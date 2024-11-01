from diagrams import Diagram, Cluster, Edge
from diagrams.aws.storage import S3
from diagrams.custom import Custom
from diagrams.onprem.workflow import Airflow

# Diagram setup
with Diagram("Web Scraping and RAG Model Pipeline", show=False):
    
    # Leftmost component: Airflow for scraping and loading data into S3 and Snowflake
    with Cluster("Apache Airflow Orchestrator"):
        # Define components within Airflow cluster
        website = Custom("Website", "architecture_diagram/webpage.png")  # Replace with path to website icon
        selenium = Custom("Selenium\nPython", "architecture_diagram/selenium.png")  # Replace with path to Selenium icon
        s3 = S3("AWS S3")
        snowflake = Custom("Snowflake", "architecture_diagram/snowflake.png")  # Replace with path to Snowflake icon

        # Workflow connections within Airflow
        website >> Edge(color='black') >> selenium
        selenium >> Edge(color='black') >> s3
        selenium >> Edge(color='black') >> snowflake

    # FastAPI component positioned after Airflow
    fastapi = Custom("FastAPI", "architecture_diagram/fastapi.png")  # Replace with path to FastAPI icon

    # Streamlit and Q&A Interface after FastAPI
    with Cluster("Client-Facing Application"):
        streamlit = Custom("Streamlit", "architecture_diagram/streamlit.png")  # Replace with path to Streamlit icon
        q_a_interface = Custom("Q&A Interface", "architecture_diagram/q&a.png")  # Replace with path to Q&A Interface icon

    # NVIDIA and Zilliz Cloud components to the right of Streamlit
    with Cluster("Summary & Query Retrieval", direction="BT"):
        nvidia_api = Custom("NVIDIA API", "architecture_diagram/nvidia.png")  # Replace with path to NVIDIA icon
        vector_db = Custom("Vector Database (Zilliz Cloud)", "architecture_diagram/vectordb.png")  # Replace with path to Vector DB icon

    # Llama and Research Notes (PDF) components to the right of Streamlit, below NVIDIA & Zilliz
    #with Cluster("Q&A Processing", direction="BT"):
    llama = Custom("Llamaindex", "architecture_diagram/llama.png")  # Replace with path to Llama icon
    research_notes_pdf = Custom("Research Notes (PDF)", "architecture_diagram/researchnotespdf.png")  # Replace with path to PDF icon

    # Additional S3 storage for processed research notes
    #with Cluster("Storage", direction="BT"):    
    s3_2 = S3("AWS S3")

    # Connections across clusters as per the left-to-right layout
    # FastAPI connections to S3 and Snowflake from Airflow
    s3 >> Edge(color='black') >> fastapi
    snowflake >> Edge(color='black') >> fastapi

    # Client-facing flow from FastAPI to Streamlit and Q&A Interface
    fastapi >> Edge(color='black') >> streamlit
    fastapi >> Edge(color='slateblue') >> q_a_interface

    # Streamlit interactions with NVIDIA & Zilliz Cloud Processing
    streamlit >> Edge(color='black') >> nvidia_api
    nvidia_api >> Edge(color='black') >> vector_db
    nvidia_api >> Edge(color='slateblue') >> streamlit

    # Q&A interactions with Llama and Research Notes (PDF)
    q_a_interface >> Edge(color='black') >> llama
    llama >> Edge(color='black') >> research_notes_pdf

    # Research notes (PDF) interaction with Streamlit and storage in S3
    research_notes_pdf >> Edge(color='slateblue', label="Back to Streamlit") >> streamlit
    research_notes_pdf >> Edge(color='black', label="Stored in S3") >> s3_2
