#!/usr/bin/env python3
"""
Test script to run queries from within Render service
Deploy this to your Render service to use query_render_postgres
"""

import os
import json

# This would work ONLY when running inside Render service
def test_render_internal_query():
    """
    When this code runs INSIDE Render:
    1. It can use internal hostname: dpg-d3d3i07diees738dl92g-a
    2. No SSL required for internal connections
    3. MCP query_render_postgres would work
    """

    # Internal connection (no SSL needed)
    internal_url = "postgresql://figma_catalog_db_user:PASSWORD@dpg-d3d3i07diees738dl92g-a:5432/figma_catalog_db"

    print("To make query_render_postgres work:")
    print("1. Deploy your service to Render")
    print("2. Use MCP from within the deployed service")
    print("3. It will use internal network without SSL")

    return internal_url

# For local development, always use external URL with SSL
def get_database_url():
    """Get correct database URL based on environment"""

    # Check if running on Render
    if os.getenv("RENDER"):
        # Use internal URL without domain suffix
        return "postgresql://figma_catalog_db_user:cj3U4fmMKXpMl2lRMa4A9CalUGBzWBzJ@dpg-d3d3i07diees738dl92g-a:5432/figma_catalog_db"
    else:
        # Use external URL with SSL for local development
        return "postgresql://figma_catalog_db_user:cj3U4fmMKXpMl2lRMa4A9CalUGBzWBzJ@dpg-d3d3i07diees738dl92g-a.oregon-postgres.render.com:5432/figma_catalog_db?sslmode=require"

if __name__ == "__main__":
    print("Current environment:", "Render" if os.getenv("RENDER") else "Local")
    print("Database URL to use:", get_database_url())