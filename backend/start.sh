#!/bin/sh
# Start script for Railway deployment
# This script properly expands the PORT environment variable

PORT=${PORT:-8000}
echo "Starting server on port $PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT