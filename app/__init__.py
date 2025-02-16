from config import Config
from flask import Flask, request, current_app
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


# Подготовка экземпляров для приложения
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'


def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)
    # Регистрация blueprint
    from app.main import bp
    app.register_blueprint(bp)
    from app.auth import bp
    app.register_blueprint(bp)

    # Связка экземпляров с приложением
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    return app


from app.models import models
