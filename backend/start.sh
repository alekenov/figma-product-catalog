#!/bin/sh
# Start script for Railway deployment
# This script properly expands the PORT environment variable

PORT=${PORT:-8000}
echo "Starting server on port $PORT"

# Run Kaspi Pay database migration if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    python3 run_kaspi_migration.py || echo "Warning: Migration script failed but continuing..."
fi

exec uvicorn main:app --host 0.0.0.0 --port $PORT