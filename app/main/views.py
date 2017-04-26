from flask import request, Response, redirect, url_for, current_app
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
from . import main
from .. import admin, db
from ..models import Permission, User, Department
from ..utils import permission_required, is_allowed_file


@main.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('report.read'))


@main.route("/upload/", methods=["POST"])
@permission_required(Permission.WRITE_REPORT)
def upload():
    img = request.files.get('image')
    if img and is_allowed_file(img.filename):
        filename = secure_filename(img.filename)
        img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        img_url = request.url_root + current_app.config['IMAGE_UPLOAD_DIR'] + filename
        res = Response(img_url)

        current_app.logger.info(
            '{} uploaded image'.format(current_user.email))
    else:
        res = Response("上传失败")
    res.headers["ContentType"] = "text/html"
    res.headers["Charset"] = "utf-8"

    current_app.logger.error(
        '{} failed uploading image'.format(current_user.email))
    return res


class WeeklyReportModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Department, db.session))
