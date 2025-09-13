# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Copy requirements.txt from back-end folder
COPY back-end/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire back-end source code
COPY back-end/ ./back-end/

# Stage 2: Final image
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy back-end source code
COPY --from=builder /app/back-end /app/back-end

EXPOSE 8000

CMD ["uvicorn", "back-end.main:app", "--host", "0.0.0.0", "--port", "8000"]
