#!/bin/bash
# ==============================================================================
# SQLite Local Database Initialization Script
# ==============================================================================
# This script initializes a fresh SQLite database for local development
#
# Usage:
#   ./init_local_db.sh          # Initialize fresh database
#   ./init_local_db.sh --keep   # Keep existing database, only run migrations
# ==============================================================================

set -e  # Exit on error

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DB_FILE="figma_catalog.db"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}SQLite Database Initialization${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if --keep flag is passed
KEEP_DB=false
if [ "$1" == "--keep" ]; then
    KEEP_DB=true
    echo -e "${YELLOW}⚠️  --keep flag detected: Preserving existing database${NC}"
fi

# Step 1: Remove old database (unless --keep)
if [ "$KEEP_DB" == false ]; then
    if [ -f "$DB_FILE" ]; then
        echo -e "${YELLOW}🗑️  Removing old database: $DB_FILE${NC}"
        rm -f "$DB_FILE"
        echo -e "${GREEN}✅ Old database removed${NC}"
    else
        echo -e "${BLUE}ℹ️  No existing database found${NC}"
    fi
    echo ""
fi

# Step 2: Verify DATABASE_URL is not set
if [ ! -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ ERROR: DATABASE_URL is set!${NC}"
    echo -e "${RED}   This script is for SQLite local development only.${NC}"
    echo -e "${RED}   Please unset DATABASE_URL or remove it from .env${NC}"
    echo ""
    echo "Current DATABASE_URL: $DATABASE_URL"
    exit 1
fi

echo -e "${GREEN}✅ DATABASE_URL not set - will use SQLite${NC}"
echo ""

# Step 3: Create database tables
echo -e "${BLUE}📊 Creating database tables...${NC}"
python3 -c "
import asyncio
from database import create_db_and_tables

async def main():
    await create_db_and_tables()
    print('✅ Tables created successfully')

asyncio.run(main())
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database tables created${NC}"
else
    echo -e "${RED}❌ Failed to create tables${NC}"
    exit 1
fi
echo ""

# Step 4: Run migrations
echo -e "${BLUE}🔄 Running migrations...${NC}"
python3 -c "
import asyncio
from database import run_migrations

async def main():
    await run_migrations()
    print('✅ Migrations completed')

asyncio.run(main())
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations completed${NC}"
else
    echo -e "${RED}❌ Migrations failed${NC}"
    exit 1
fi
echo ""

# Step 5: Load seed data (only if not keeping DB)
if [ "$KEEP_DB" == false ]; then
    echo -e "${BLUE}🌱 Loading seed data...${NC}"

    if [ -f "seed_data.py" ]; then
        python3 seed_data.py

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Seed data loaded${NC}"
        else
            echo -e "${RED}❌ Failed to load seed data${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  seed_data.py not found - skipping seed data${NC}"
    fi
    echo ""
fi

# Step 6: Verify database
echo -e "${BLUE}🔍 Verifying database...${NC}"
if [ -f "$DB_FILE" ]; then
    DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
    echo -e "${GREEN}✅ Database created: $DB_FILE ($DB_SIZE)${NC}"

    # Show table count
    TABLE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null)
    if [ ! -z "$TABLE_COUNT" ]; then
        echo -e "${GREEN}   Tables: $TABLE_COUNT${NC}"
    fi
else
    echo -e "${RED}❌ Database file not found!${NC}"
    exit 1
fi
echo ""

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✅ Database initialization complete!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Start backend: python3 main.py"
echo "  2. Test API: curl http://localhost:8014/health"
echo ""
