from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from routes import api
from priority import SECRET_KEY

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({
        'app': 'Procrastify API',
        'version': '1.0',
        'status': 'running'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Procrastify backend starting on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
