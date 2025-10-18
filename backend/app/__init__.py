from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    # Configuração do CORS para aceitar apenas origens de extensões do Chrome
    CORS(app, resources={r"/api/*": {"origins": ["chrome-extension://*"]}})
    
    # Opcional: habilite debug para desenvolvimento (desative em produção)
    app.config['DEBUG'] = True
    
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

