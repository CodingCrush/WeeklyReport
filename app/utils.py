import datetime
from functools import wraps
from flask import abort
from flask_login import current_user
from config import Config
from .models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or \
                    not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def email_check(email_address):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.email == email_address:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return email_check(Config.FLASK_ADMIN_EMAIL)(f) or \
           permission_required(Permission.ADMINISTER)(f)


def get_week_count(at=datetime.datetime.now()):
    return at.isocalendar()[1]


def get_this_monday():
    today = datetime.date.today()
    weekday = today.weekday()
    return today-datetime.timedelta(weekday)


def is_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in {'png', 'jpg', 'jpeg', 'gif'}


default_content = "<p><strong>本周工作内容:</strong></p><ol><li></li></ol>" \
                  "<p>&nbsp;<strong>下周计划:</strong></p><ol><li></li></ol>"
