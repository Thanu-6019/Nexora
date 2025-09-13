# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's cache
COPY back-end/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 80

# Define the start command to run your FastAPI application
CMD ["uvicorn", "back-end.main:app", "--host", "0.0.0.0", "--port", "80"]
