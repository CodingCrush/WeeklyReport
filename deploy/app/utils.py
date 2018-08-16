#coding:utf-8
import datetime
from functools import wraps
from flask import abort
from flask_login import current_user


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


def get_week_count(at=datetime.datetime.now()):
    return at.isocalendar()[1]


def get_this_monday():
    today = datetime.date.today()
    weekday = today.weekday()
    return today-datetime.timedelta(weekday)


def is_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in {'png', 'jpg', 'jpeg', 'gif'}


def get_last_week():
    return datetime.datetime.now() - datetime.timedelta(days=7)


def get_last_week_start_at():
    return get_this_monday() - datetime.timedelta(days=7)


def get_last_week_end_at():
    return get_this_monday()
    
def get_last_week_content(last_week_content):
    content_index = last_week_content.find("next_week")
    if content_index != -1:
    	return last_week_content[content_index+31:]
    return ""
