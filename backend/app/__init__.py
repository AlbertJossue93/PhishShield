from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # 🔥 Libera somente API e aceita qualquer extensão Chrome
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config['DEBUG'] = True

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
