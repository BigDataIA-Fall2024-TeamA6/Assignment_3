# Use an official Python 3.12 image
FROM python:3.12-slim

# Set the working directory for FastAPI
WORKDIR /app

# Copy pyproject.toml and poetry.lock from the root folder
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Install dependencies from Poetry
RUN poetry install --no-root

# Copy the FastAPI source code
COPY ./fast_api/ /app/fast_api

# Ensure Uvicorn is installed and available
RUN poetry run uvicorn --version

# Expose the port for FastAPI
EXPOSE 8000

# Command to run FastAPI using Uvicorn
CMD ["poetry", "run", "uvicorn", "fast_api.api:app", "--host", "0.0.0.0", "--port", "8000"]
