import sys
import os
from pathlib import Path

# Ensure root workspace directory is in python path for Linux production environments
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app import app

if __name__ == "__main__":
    app.run()
