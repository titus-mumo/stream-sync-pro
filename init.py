from flask import Flask
import secrets
from datetime import timedelta
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from models import db, User
from routes import main
from config import Config
from flask_login import LoginManager

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Login to continue"

    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=30) 

    with app.app_context():
        db.create_all()

    foo = secrets.token_urlsafe(16)
    app.secret_key = foo

    bootstrap = Bootstrap5(app)
    csrf = CSRFProtect()
    app.register_blueprint(main)
    return app





