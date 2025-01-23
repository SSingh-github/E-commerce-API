from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuration from .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        # Import routes
        from .routes import auth_blueprint
        app.register_blueprint(auth_blueprint)

        # Create tables if they do not exist
        db.create_all()

    return app
