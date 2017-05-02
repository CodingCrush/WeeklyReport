from flask import request, Response, redirect, url_for, current_app
from flask_admin.contrib.sqla import ModelView
from flask_babelex import lazy_gettext as _
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
from . import main
from .. import admin, db
from ..models import Permission, User, Role, Report, Department
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
        res = Response(_("Failed Uploading"))
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


class UserAdminView(WeeklyReportModelView):
    column_labels = dict(email='邮箱', username='姓名',
                         is_ignored='不参与统计',
                         role='角色', department='部门')
    form_columns = column_list = [
        'email', 'username', 'is_ignored', 'role', 'department']
    can_delete = True
    can_create = False
    form_widget_args = {
        'email': {
            'readonly': True
        },
    }


class RoleAdminView(WeeklyReportModelView):
    column_labels = dict(name='名称', users='成员')
    form_columns = ['name', 'users']
    column_list = ['name']
    can_create = False
    can_edit = True
    can_delete = False
    form_widget_args = {
        'name': {
            'readonly': True
        },
    }


class DepartmentAdminView(WeeklyReportModelView):
    column_labels = dict(name='名称', users='成员')
    form_columns = ['name', 'users']
    can_edit = True
    can_delete = False
    form_widget_args = {
        'name': {
            'readonly': True
        },
    }


class ReportAdminView(WeeklyReportModelView):
    column_labels = dict(year='年份', week_count='周次',
                         created_at='创建时间', content='内容',
                         author='员工邮箱', department='部门')
    column_list = ('author', 'department', 'year', 'week_count',
                   'content', 'created_at')
    form_columns = ['created_at', 'week_count', 'year', 'content']
    can_edit = True
    can_export = True
    form_widget_args = {
        'year': {
            'readonly': True
        },
        'created_at': {
            'readonly': True
        },
    }


admin.add_view(UserAdminView(User, db.session, name='用户'))
admin.add_view(RoleAdminView(Role, db.session, name='角色'))
admin.add_view(ReportAdminView(Report, db.session, name='周报', endpoint="reports"))
admin.add_view(DepartmentAdminView(Department, db.session, name='部门'))
