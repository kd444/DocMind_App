# Use an official Python runtime as a parent image
FROM python:3.11-slim as backend

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and main.py into the container
COPY pyproject.toml ./
COPY main.py ./

# Install Poetry and dependencies
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

# Ensure main.py is executable (if needed)
RUN chmod +x main.py

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Start Gunicorn as the application server
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
