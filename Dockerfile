# --- STAGE 1: Builder Stage ---
# Use a Python base image with a full build environment.
FROM python:3.11-slim-bookworm AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project directory into the container.
# This is the key change. It ensures all files are available for the next steps,
# regardless of where the build command is executed.
COPY . .

# Change into the backend directory to install requirements
WORKDIR /app/backend

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# --- STAGE 2: Final Production Image ---
# Use a lightweight Python base image for the final application
FROM python:3.11-slim-bookworm

# Set the working directory
WORKDIR /app

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code from the builder stage
COPY --from=builder /app/backend /app/backend

# Expose the port the FastAPI application runs on
EXPOSE 8000

# Define the start command to run your FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
