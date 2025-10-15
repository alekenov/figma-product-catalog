#!/bin/sh
# Start script for Railway deployment
# This script properly expands the PORT environment variable

PORT=${PORT:-8000}
echo "Starting server on port $PORT"

# Run Kaspi Pay database migration if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "Running Kaspi Pay database migration..."
    psql "$DATABASE_URL" -c "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS kaspi_payment_id VARCHAR(50);" || echo "Warning: Could not add kaspi_payment_id"
    psql "$DATABASE_URL" -c "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS kaspi_payment_status VARCHAR(20);" || echo "Warning: Could not add kaspi_payment_status"
    psql "$DATABASE_URL" -c "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS kaspi_payment_created_at TIMESTAMP;" || echo "Warning: Could not add kaspi_payment_created_at"
    psql "$DATABASE_URL" -c "ALTER TABLE \"order\" ADD COLUMN IF NOT EXISTS kaspi_payment_completed_at TIMESTAMP;" || echo "Warning: Could not add kaspi_payment_completed_at"
    echo "Kaspi Pay migration completed"
fi

exec uvicorn main:app --host 0.0.0.0 --port $PORT