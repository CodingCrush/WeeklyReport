from datetime import datetime
from flask import Flask
from flask_admin import Admin
from flask_babelex import Babel
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import config
from .json_encoder import JSONEncoder


bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = "basic"
login_manager.login_view = 'auth.login'

app = Flask(__name__)

babel = Babel()

admin = Admin(app, name='WeeklyReport', template_mode='bootstrap3')


@babel.localeselector
def get_locale():
    return 'zh_Hans_CN'


def create_app(config_name):

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    mail.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .report import report as report_blueprint
    app.register_blueprint(report_blueprint, url_prefix='/report')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # chartkick support
    app.jinja_env.add_extension('chartkick.ext.charts')

    # i18n support
    app.jinja_env.add_extension('jinja2.ext.i18n')

    # jinja env to help check statistics page under this week
    app.jinja_env.globals.update(
        get_this_week_count=lambda: datetime.now().isocalendar()[1])

    # lazy_gettext Json Error Fix
    app.json_encoder = JSONEncoder
    return app
