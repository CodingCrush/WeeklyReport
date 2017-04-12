from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_mongoengine import *
from config import config

bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = MongoEngine()

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
    app.session_interface = MongoEngineSessionInterface(db)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # chartkick support
    app.jinja_env.add_extension("chartkick.ext.charts")

    return app
