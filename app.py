"""
Proxy file for Render deployment
This file imports the FastAPI app from backend directory
"""
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Now import main module directly (without 'backend.' prefix since we added it to path)
from main import app

# Export app for uvicorn
__all__ = ['app']