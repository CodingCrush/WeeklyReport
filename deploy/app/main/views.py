#coding:utf-8
from datetime import date
from flask import request, Response, redirect, url_for, current_app
from flask_admin.model import typefmt
from flask_admin.contrib.sqla import ModelView
from flask_babelex import lazy_gettext as _
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
from . import main
from .. import admin, db
from ..models import Permission, User, Role, Report, Department
from ..utils import permission_required, is_allowed_file, clean_html
from sqlalchemy.exc import OperationalError

@main.route('/', methods=['GET', 'POST'])
def index():
    # check if the database is initialized.
    try:
        User.query.all()
    except OperationalError:
        db.create_all()
        Role.insert_roles()
        Department.insert_departments()

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
    base_template = '/base.html'

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

    def on_model_delete(self, model):

        current_app.logger.info(
            '{} deleted user:{}'.format(current_user.email, model))

        for report in Report.query.filter_by(author_id=model.id):
            db.session.delete(report)
        db.session.commit()


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


class ReportAdminView(WeeklyReportModelView):
    column_labels = dict(year=u'年份', week_count=u'周次',
                         created_at=u'创建时间', last_content=u'上周计划', content=u'内容',
                         author=u'员工', department=u'部门')
    column_list = ('author', 'department', 'year', 'week_count', 'last_content',
                   'content', 'created_at')
    column_default_sort = ('created_at', True)
    column_searchable_list = ('week_count',)
    form_columns = ['created_at', 'week_count', 'year', 'content']
    list_template = '/admin/model/report_list_template.html'
    can_edit = True
    can_export = True
    export_types=['xls']
    form_widget_args = {
        'year': {
            'readonly': True
        },
        'last_content': {
            'readonly': True
        },
        'created_at': {
            'readonly': True
        },
    }

    def date_format(view, value):
        return value.strftime('%Y-%m-%d')
        
    def author_format(v, c, m, p):
        return str(m.author)
        
    def department_format(v, c, m, p):
        return str(m.department)
    
    def format_last_content(v, c, m, p):
    	  if m.last_content:
           return clean_html(m.last_content)

    	  return ''

    def format_content(v, c, m, p):
    	  if m.content:
           return clean_html(m.content)

    	  return ''
    	  
    def format_created_at(v, c, m, p):
    	  return m.created_at.strftime('%Y-%m-%d')   	  

    REPORT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
    REPORT_FORMATTERS.update({
            date: date_format,
        })
    column_type_formatters = REPORT_FORMATTERS
    
    EXPORT_REPORT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
    EXPORT_REPORT_FORMATTERS.update({
            "author": author_format,
            "department": department_format,
            "last_content": format_last_content,
            "content": format_content,
            "created_at":format_created_at,
        })
    column_formatters_export = EXPORT_REPORT_FORMATTERS


admin.add_view(UserAdminView(User, db.session, name='用户'))
admin.add_view(RoleAdminView(Role, db.session, name='角色'))
admin.add_view(ReportAdminView(Report, db.session, name='周报', endpoint="reports"))
admin.add_view(DepartmentAdminView(Department, db.session, name='部门'))
