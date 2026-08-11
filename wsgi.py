import os
import sys
from pathlib import Path

# Add root project directory and backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

BACKEND_DIR = BASE_DIR / 'backend'
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from backend.app import app
except ModuleNotFoundError:
    from app import app

if __name__ == "__main__":
    app.run()
