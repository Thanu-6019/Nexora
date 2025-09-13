# --- STAGE 1: Builder Stage ---
# Use a Python base image with a full build environment.
FROM python:3.11-slim-bookworm AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the builder stage
# We're only copying the requirements here to keep the first stage lightweight
COPY backend/requirements.txt .

# Install dependencies from the requirements file
# The `--no-cache-dir` flag ensures a smaller image by not storing temporary files
RUN pip install --no-cache-dir -r requirements.txt

# --- STAGE 2: Final Production Image ---
# Use a lightweight Python base image for the final application
FROM python:3.11-slim-bookworm

# Set the working directory
WORKDIR /app

# Copy the installed packages from the builder stage
# This is the key step of a multi-stage build: we copy only the essentials
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy your application code into the final image
# The dot `.` copies everything from the current directory
COPY . .

# Expose the port the FastAPI application runs on
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

