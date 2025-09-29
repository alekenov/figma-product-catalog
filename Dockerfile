# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (for PostgreSQL)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port (Render will override this with PORT env variable)
EXPOSE 8000

# Use shell form to expand environment variable
# Render provides PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}