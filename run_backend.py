#!/usr/bin/env python3
import os
import sys

# Add backend to path
sys.path.insert(0, 'backend')

# Change to backend directory
os.chdir('backend')

# Import and run the app
import uvicorn
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)