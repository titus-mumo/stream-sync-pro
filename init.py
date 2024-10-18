from flask import Flask
import secrets
from datetime import timedelta
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from models import db, User
from views.routes import main
from views.user import master
from views.following import follow
from views.messaging import messaging, websocket_handler
from config import Config
from flask_login import LoginManager
from quart import Quart

from aiohttp import web
from aiohttp_wsgi import WSGIHandler

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

# Function to create aiohttp app
def create_aiohttp_app(flask_app):
    # Initialize aiohttp app
    aiohttp_app = web.Application()

    # WSGI handler to integrate Flask with aiohttp
    wsgi_handler = WSGIHandler(flask_app)

    # Routes for handling Flask and aiohttp
    aiohttp_app.router.add_route('*', '/{path_info:.*}', wsgi_handler)  # Handles all Flask routes
    aiohttp_app.router.add_route('GET', '/listen', websocket_handler)   # WebSocket route

    return aiohttp_app

if __name__ == "__main__":
    print("Starting the app...")

    # Create Flask app
    flask_app = create_app()
    print("Flask app created.")

    # Create aiohttp app and run it
    aiohttp_app = create_aiohttp_app(flask_app)
    print("Running aiohttp on port 5555...")
    web.run_app(aiohttp_app, port=5555)
    print("Server is running on port 5555")
