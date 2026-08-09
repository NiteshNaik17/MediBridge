import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'medibridge-super-secret-key-2026')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/medibridge')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'backend', 'uploads', 'medical_documents')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}

    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
