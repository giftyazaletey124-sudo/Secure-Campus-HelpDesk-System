
from flask import Flask
from config import Config
from app.database import create_tables

def create_app():
    app = Flask(__name__)

    # Load application settings
    app.config.from_object(Config)

    # Register website routes
    from app.routes import main
    app.register_blueprint(main)

    # Create database tables
    with app.app_context():
        create_tables()

    return app
