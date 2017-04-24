from flask import Flask
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = "basic"
login_manager.login_view = 'auth.login'

app = Flask(__name__)

admin = Admin(app, name='WeeklyReport', template_mode='bootstrap3')


def create_app(config_name):

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    if not app.config['DEBUG']:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler('logs/weeklyreport.log', maxBytes=1024 * 1024 * 100, backupCount=20)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s-%(levelname)s %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # chartkick support
    app.jinja_env.add_extension("chartkick.ext.charts")

    return app
