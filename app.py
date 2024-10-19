from flask import Flask
import secrets
from datetime import timedelta
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from models import db, User
from views.routes import main
from views.user import master
from views.following import follow
from views.messaging import messaging
# from views.messaging import websocket_handler
from config import Config
from flask_login import LoginManager
import os

# Initialize Flask-Login
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to create Flask app
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Login to continue"
    
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=30)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Set up Flask secret key
    foo = secrets.token_urlsafe(16)
    app.secret_key = foo

    # Register Flask blueprints
    bootstrap = Bootstrap5(app)
    csrf = CSRFProtect()
    app.register_blueprint(main)
    app.register_blueprint(master)
    app.register_blueprint(follow)
    app.register_blueprint(messaging)

    return app