import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import Flask, send_from_directory, jsonify
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId
from flask_cors import CORS
from backend.config import Config
from backend.routes.auth_routes import auth_bp
from backend.routes.hospital_routes import hospital_bp
from backend.routes.patient_routes import patient_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.ai_routes import ai_bp

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(BASE_DIR, 'frontend'),
        static_url_path=''
    )
    app.json_provider_class = CustomJSONProvider
    app.json = CustomJSONProvider(app)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, supports_credentials=True)

    # Register API Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(hospital_bp, url_prefix='/api/hospitals')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

    # Uploads route
    @app.route('/uploads/medical_documents/<path:filename>')
    def serve_uploaded_file(filename):
        upload_folder = app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename)

    # Serve static frontend files
    @app.route('/')
    def index():
        return send_from_directory(os.path.join(BASE_DIR, 'frontend'), 'index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        frontend_dir = os.path.join(BASE_DIR, 'frontend')
        requested_path = os.path.join(frontend_dir, filename)
        if os.path.exists(requested_path) and os.path.isfile(requested_path):
            return send_from_directory(frontend_dir, filename)
        # If accessing portal subfolder without .html (e.g. /hospital/dashboard)
        if os.path.exists(requested_path + '.html'):
            return send_from_directory(frontend_dir, filename + '.html')
        return send_from_directory(frontend_dir, 'index.html')

    @app.errorhandler(404)
    def not_found(e):
        return send_from_directory(os.path.join(BASE_DIR, 'frontend'), 'index.html')

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"MediBridge AI Platform is starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, use_reloader=False)

from flask import Flask, send_from_directory, jsonify
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId
from flask_cors import CORS
from backend.config import Config
from backend.routes.auth_routes import auth_bp
from backend.routes.hospital_routes import hospital_bp
from backend.routes.patient_routes import patient_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.ai_routes import ai_bp

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(BASE_DIR, 'frontend'),
        static_url_path=''
    )
    app.json_provider_class = CustomJSONProvider
    app.json = CustomJSONProvider(app)
    app.config.from_object(Config)


    # Enable CORS
    CORS(app, supports_credentials=True)

    # Register API Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(hospital_bp, url_prefix='/api/hospitals')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

    # Uploads route
    @app.route('/uploads/medical_documents/<path:filename>')
    def serve_uploaded_file(filename):
        upload_folder = app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename)

    # Serve static frontend files
    @app.route('/')
    def index():
        return send_from_directory(os.path.join(BASE_DIR, 'frontend'), 'index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        frontend_dir = os.path.join(BASE_DIR, 'frontend')
        requested_path = os.path.join(frontend_dir, filename)
        if os.path.exists(requested_path) and os.path.isfile(requested_path):
            return send_from_directory(frontend_dir, filename)
        # If accessing portal subfolder without .html (e.g. /hospital/dashboard)
        if os.path.exists(requested_path + '.html'):
            return send_from_directory(frontend_dir, filename + '.html')
        return send_from_directory(frontend_dir, 'index.html')

    @app.errorhandler(404)
    def not_found(e):
        return send_from_directory(os.path.join(BASE_DIR, 'frontend'), 'index.html')

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"MediBridge AI Platform is starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
