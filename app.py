"""
Proxy file for Render deployment
This file imports the FastAPI app from backend directory
"""
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the FastAPI app from backend
from backend.main import app

# Export app for uvicorn
__all__ = ['app']