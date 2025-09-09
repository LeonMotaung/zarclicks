from flask import Flask
from flask_pymongo import PyMongo
from config import Config

mongo = PyMongo()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize MongoDB
    mongo.init_app(app)
    
    # Register blueprints/routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app