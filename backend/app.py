# backend entry point
from flask import Flask, jsonify
from flask_cors import CORS
from config import current_config

# import routes
from routes.auth import auth_bp
from routes.tasks import tasks_bp
from routes.analytics import analytics_bp
from routes.sessions import sessions_bp


# create app
def create_app():
    app = Flask(__name__)
    
    # load config
    app.config['SECRET_KEY'] = current_config.SECRET_KEY
    app.config['DEBUG'] = current_config.DEBUG
    
    # enable cors
    CORS(app, resources={r"/api/*": {"origins": current_config.CORS_ORIGINS}})
    
    # register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
    
    # root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'app': 'Procrastify API',
            'version': '1.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'tasks': '/api/tasks',
                'analytics': '/api/analytics',
                'sessions': '/api/sessions'
            }
        })
    
    # health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app



app = create_app()

if __name__ == '__main__':
    print("Procrastify backend starting on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
