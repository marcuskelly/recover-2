import os

# third-party imports
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_sslify import SSLify

# local imports
from config import app_config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


def create_app(config_name):
    if os.getenv('FLASK_CONFIG') == "production":
        app = Flask(__name__)
        sslify = SSLify(app)
        #  app.config.from_object(__name__)
        app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
        app.config.update(dict(
            MAIL_SERVER = 'smtp.gmail.com',
            MAIL_PORT = 587,
            MAIL_USE_SSL = False,
            MAIL_USE_TLS = True,
            MAIL_USERNAME = os.environ.get('MAIL_USERNAME'),
            MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD'),
            MAIL_DEFAULT_SENDER = '"Recover" <noreply@gmail.com>'
        ))
        app.config.update(
            SECRET_KEY=os.getenv('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI')
        )
        mail.init_app(app)
        #  mail = Mail(app)
    else:
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_object(app_config[config_name])
        app.config.from_pyfile('config.py')

    Bootstrap(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"
    migrate = Migrate(app, db)


    from app import models

    from .doctor import doctor as doctor_blueprint
    app.register_blueprint(doctor_blueprint, url_prefix='/doctor')

    from .patient import patient as patient_blueprint
    app.register_blueprint(patient_blueprint)


    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', title='Forbidden'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', title='Server Error'), 500

    return app
