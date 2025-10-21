#!/bin/sh
# Start script for Embedding Service on Railway
# Properly expands PORT environment variable

PORT=${PORT:-8001}
echo "Starting Embedding Service on port $PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT
