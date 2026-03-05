"""
Procrastify v2.0 - Flask Backend API
Main Application Entry Point
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import current_config

# Import route blueprints
from routes.auth import auth_bp
from routes.tasks import tasks_bp
from routes.analytics import analytics_bp
from routes.sessions import sessions_bp


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = current_config.SECRET_KEY
    app.config['DEBUG'] = current_config.DEBUG
    
    # Enable CORS for mobile app
    CORS(app, resources={r"/api/*": {"origins": current_config.CORS_ORIGINS}})
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'app': 'Procrastify API',
            'version': '2.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'tasks': '/api/tasks',
                'analytics': '/api/analytics',
                'sessions': '/api/sessions'
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


# Create app instance
app = create_app()

if __name__ == '__main__':
    print("""
    ===========================================================
    |                                                           |
    |   PROCRASTIFY v2.0 API SERVER                             |
    |                                                           |
    |   Server running at: http://localhost:5000                |
    |                                                           |
    |   Endpoints:                                              |
    |   - POST /api/auth/register     - Register new user       |
    |   - POST /api/auth/login        - Login user              |
    |   - GET  /api/tasks             - Get all tasks           |
    |   - POST /api/tasks             - Create task             |
    |   - GET  /api/analytics/daily   - Get daily stats         |
    |   - POST /api/sessions/start    - Start focus session     |
    |                                                           |
    ===========================================================
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
