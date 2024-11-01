
---

## **Assignment 3 - Automated Web Scraping and Multi-Modal RAG Implementation using NVIDIA**

### **Contributors**:
- Sahiti Nallamolu
- Vishodhan Krishnan
- Vismay Devjee



### **Project Resources**:
---
a. **Diagrams**: [Architecture Diagram](https://github.com/BigDataIA-Fall2024-TeamA6/Assignment_3/architecture_diagram/)  
b. **Fully Documented Code Labs**: [Codelabs Preview](https://codelabs-preview.appspot.com/?file_id=1mjvrVPW4HhfXsRnsTeXvmz30b2qKbRQ2dVz1ydNykV4/)  
c. **Video of the Submission**: [Zoom Recording]()  
d. **Link to Working Application**: [Streamlit App](https://team6app1.streamlit.app/)  
e. **GitHub Project**: [GitHub Repository](https://github.com/BigDataIA-Fall2024-TeamA6/Assignment_3)



## Synopsis

This project develops a client-facing application that enables efficient exploration, summarization, and querying of documents from the CFA Institute Research Foundation. Using FastAPI and Streamlit, users can select documents, generate summaries on-demand with **NVIDIA’s API**, and query content via a **multi-modal RAG** system powered by **Zilliz Cloud** and **LlamaIndex.** Research notes are incrementally indexed for continuous learning and easy access, and the application is fully containerized with Docker for secure and scalable deployment. This solution provides a seamless interface for real-time document interaction and research insights.


### Technologies Used
- **Streamlit**: for the frontend interface.
- **FastAPI**: for backend API management.
- **Selenium**: for web scraping from CFA Institute Research Foundation Publications.
- **NVIDIA API**: for summary generation.
- **Zilliz Cloud**: as the vector database for document indexing and search.
- **LlamaIndex**: for language model interaction.
- **Amazon S3**: for storing unstructured data.
- **Snowflake**: for structured database management.


## Problem Statement

- **Objective**: To create an automated and efficient system for scraping, exploring, and analyzing documents from the CFA Institute Research Foundation Publications.
- **Current Challenge**: Accessing key insights from large volumes of publications is time-consuming.
- **Data Complexity**: Managing various data formats, such as PDFs and images, adds to the challenge.
- **Goal**: Build a system that integrates:
  - **Data Storage**: Efficiently handle and store unstructured and structured data.
  - **Processing**: Usage of NVIDIA API and LLAMA to navigate through Research Notes and PDF content for continuous learning.
  - **User Experience**: Providing user with Q&A interface for user to explore the document, and providing user with most efficient and accurate answers through RAG model.



## Desired Outcome

The desired outcome is a user-friendly application that allows users to:

- **Select and view documents**: Access documents with an intuitive grid view option.
- **Generate on-demand summaries**: Use NVIDIA’s summarization API to create concise document summaries.
- **Interactively query documents**: Utilize a multi-modal Retrieval-Augmented Generation (RAG) system powered by Zilliz Cloud and LlamaIndex, providing concise responses based on user inputs.
- **Search and index research notes**: Incrementally index and search verified research notes for easy future reference.
```

## File Structure:

Assignment_3/
  ├── airflow/
  │   ├── dags/
  │   │   └── dag_extract_upload.py     #DAG definition for triggering PDF extractions using  
  │   └── docker-compose.yaml   #Airflow deployment configuration
  │   └── requirements.txt  
  ├── architecture_diagram/
  │   ├── arch_diagram.py
  ├── db_setup_scripts/
  │   ├── json_to_s3.py               
  │   ├── web_scraper.py
  ├── streamlit/
  │   ├── app.py                #Main Streamlit application
  │   ├── pages/
  │   │   └── qa_interface.py       #Admin page for viewing logs
  │   │   └── doc_detail.py         #User creation form
  │   │   └── db.py                 #Define db Connections
  │   │   └── user_landing.py       #Main landing page for users
  │   └── document_processors.py    
  │   └── utils.py
  │   └── app.py
  ├── FastAPI/
  │   └── api.py               #FastAPI application for PDF extraction and GPT-4 integration
  │   └── models.py             #FastAPI application for PDF extraction and GPT-4 
  ├── poetry.lock               #Poetry dependencies lock file
  └── README.md 
```


## How It Works
1. **Scraping Data**: The data is scraped from the CFA Institute Research Foundation Publications website using Selenium. The unstructered data like PDFs and Images are stored in AWS S3 bucket while structered data is stored in Snowflake.
2. **Research Paper Selection**: User is provided with list of all research papers available on the site in a grid format. The user can see hover over any image (cover) to see the title and brief summary about the paper.
3. **Detailed Summary**: The user can see all the details of a paper and detailed summary provided by NVIDIA API.
4. **Q&A Interface**: Users can ask questions related to the pdf selected in a chat prompt. If the question has already been asked previously, answer from the  Research Notes is provided, else the LLM refers to vector database to provide most accurate answer.
5. **Content Preview**: While the users are able to ask questions through chat prompt, they can view the content i.e. pdf preview or research notes on the left side for reference.

## Architecture Diagram

![Architecture Diagram](https://github.com/BigDataIA-Fall2024-TeamA6/Assignment_3/blob/main/architecture_diagram/web_scraping_and_rag_model_pipeline.png)

---

### **Desired Outcome**

The application will allow users to:
- Register and securely log in using JWT-based authentication.
- Query extracted text from PDF documents, selecting between open-source or API-based extraction methods.
- View extracted information and interact with the system in a user-friendly manner.

---

### **Steps to Run this Application**

1. **Clone this repository** to your local machine:

   ```bash
   git clone https://github.com/your-repo.git
   ```

2. **Install all required dependencies**:

   ```bash
   poetry install
   ```

3. **Add your credentials** to a `.env` file under the `/streamlit` and `/airflow` folders:

   - AWS Access Key
   - AWS Secret Access Key
   - NVIDIA API Key (if applicable)
   - Snowflake Access Details

4. **Run the applications**:

   - **Airflow** (for pipeline automation):

     ```bash
     docker-compose -f airflow/docker-compose.yaml up
     ```

   - **Streamlit** (for the user interface):

     ```bash
     streamlit run streamlit/app.py
     ```

5. **Using the Application**:
   - **Query PDF Documents**: Choose any Research Paper to ask questions.
   - **Interact**: Use the chatbox to ask questions related to pdf.
   - **Reference**: Refer the document on the left side.


---

### **References**

1. [Airflow Documentation](https://airflow.apache.org/)
2. [FastAPI Documentation](https://fastapi.tiangolo.com/)
3. [Streamlit Documentation](https://docs.streamlit.io/)
4. [NVIDIA API](https://build.nvidia.com/meta/llama-3_1-405b-instruct)
5. [RAG Model](https://github.com/NVIDIA/GenerativeAIExamples/tree/main/community/llm_video_series/video_2_multimodal-rag)
6. [RAG](https://github.com/run-llama/rags)
7. [LLM](https://github.com/run-llama/llama_parse/tree/main/examples/multimodal)
8. [Chatbot](https://github.com/streamlit/llamaindex-chat-with-streamlit-docs) 

---
