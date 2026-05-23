"""
Fire NOC System - Main Flask Application
Run: python app.py
"""
import os
from flask import Flask, send_from_directory, jsonify
from config import Config
from extensions import db, jwt, bcrypt
from flask_cors import CORS

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app,
         origins=app.config.get('CORS_ORIGINS', '*'),
         supports_credentials=True,
         allow_headers=app.config.get('CORS_HEADERS', ['Content-Type', 'Authorization']))

    # Ensure upload folders exist
    for folder in ['documents', 'inspections', 'noc']:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder), exist_ok=True)

    # Register blueprints
    from routes.auth_routes        import auth_bp
    from routes.application_routes import app_bp
    from routes.other_routes       import (inspection_bp, followup_bp, noc_bp,
                                           document_bp, notification_bp, dashboard_bp)

    app.register_blueprint(auth_bp,         url_prefix='/api')
    app.register_blueprint(app_bp,          url_prefix='/api')
    app.register_blueprint(inspection_bp,   url_prefix='/api')
    app.register_blueprint(followup_bp,     url_prefix='/api')
    app.register_blueprint(noc_bp,          url_prefix='/api')
    app.register_blueprint(document_bp,     url_prefix='/api')
    app.register_blueprint(notification_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp,    url_prefix='/api')

    # Serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'Fire NOC System API Running'}), 200

    # Serve frontend pages
    @app.route('/')
    def index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/<path:path>')
    def serve_frontend(path):
        full = os.path.join('..', 'frontend', path)
        if os.path.exists(full):
            return send_from_directory('../frontend', path)
        return send_from_directory('../frontend', 'index.html')

    # JWT error handlers
    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({'error': 'Missing token', 'reason': reason}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({'error': 'Invalid token', 'reason': reason}), 422

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()          # creates tables if they don't exist
        print("✅  Database tables verified / created.")
    print("🔥  Fire NOC System running at http://localhost:5000")
    app.run(debug=True, port=5000)
