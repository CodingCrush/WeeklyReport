from flask import render_template, current_app, request
from flask_login import current_user
from . import main


@main.app_errorhandler(403)
def forbidden(e):

    current_app.logger.error(
        '403 forbidden at {} by {} '.format(request.url, current_user.email))

    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):

    current_app.logger.error(
        '404 not found at {} by {} '.format(request.url, current_user.email))

    return render_template('404.html'), 404
