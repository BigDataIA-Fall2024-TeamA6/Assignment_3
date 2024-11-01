# Use an official Python image
FROM python:3.12-slim

# Set the working directory for Streamlit
WORKDIR /app

# Copy only the necessary files from the root to avoid excessive rebuilds
COPY /pyproject.toml /poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Install dependencies from Poetry
RUN poetry install --no-root

# Copy the Streamlit source code
COPY . /app

# Expose the port for Streamlit
EXPOSE 8501

# Command to run the Streamlit app
#CMD ["streamlit", "run", "pages/app.py", "--server.port=8501"]
ENTRYPOINT ["poetry", "run", "streamlit", "run", "streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

