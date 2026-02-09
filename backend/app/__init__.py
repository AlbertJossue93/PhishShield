from flask import Flask
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler

def configure_logging(app: Flask) -> None:
    """
    Configura logging estruturado em arquivo quando a aplicação não está em modo debug.
    """
    if app.debug:
        return

    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_handler = RotatingFileHandler(
        "logs/phishshield.log",
        maxBytes=10_240_000,
        backupCount=10,
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("PhishShield startup")


def create_app():
    app = Flask(__name__)

    # DEBUG controlado por variável de ambienete
    debug_env = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.config["DEBUG"] = debug_env


    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*",  
                "methods": ["POST", "OPTIONS"],
                "allow_headers": ["Content-Type"],
            }
        },
    )

    configure_logging(app)

    from app.routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    return app  
