#!/bin/sh
# Start script for Railway deployment
# This script properly expands the PORT environment variable

PORT=${PORT:-8000}
echo "Starting server on port $PORT"

# Run database migrations if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "🔄 Running migrations..."
    python3 run_kaspi_migration.py || echo "Warning: Kaspi migration failed but continuing..."
    python3 migrations/add_ai_agent_flags.py || echo "Warning: AI Agent flags migration failed but continuing..."
fi

exec uvicorn main:app --host 0.0.0.0 --port $PORT