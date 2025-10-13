# Python 3.11 Dockerfile for AI Agent Service V2
FROM python:3.11-slim as builder

# Install build dependencies
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Set PATH to include local Python packages
ENV PATH=/root/.local/bin:$PATH

# Expose port (Railway will override with $PORT)
EXPOSE 8080

# Run the application
CMD ["./start.sh"]
