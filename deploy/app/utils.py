#coding:utf-8
import datetime
from functools import wraps
from flask import abort
from flask_login import current_user
import re


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


def get_week_count(at=None):
    if at:
        return at.isocalendar()[1]
    else:
        return datetime.datetime.now().isocalendar()[1]


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

def clean_html(html):
    """
    Remove HTML markup from the given string.
    :param html: the HTML string to be cleaned
    :type html: str
    :rtype: str
    """

    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()
	
def get_week_days(year, week, index):
    d = datetime.date(year, 1, 1)
    if (d.weekday() > 3):
        d = d + datetime.timedelta(7-d.weekday())
    else:
	    d = d - datetime.timedelta(d.weekday())
    dlt = datetime.timedelta(days = (week - 1) * 7)
    return (d + dlt, d + dlt + datetime.timedelta(days=6))[index]