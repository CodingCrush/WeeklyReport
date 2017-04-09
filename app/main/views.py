from flask import render_template, redirect, url_for
from flask_admin.contrib.mongoengine import ModelView
from flask_login import login_required, current_user
from . import main
from .forms import ReportForm, ReportSubmitForm
from .. import admin
from ..models import Permission, User, Report, Project, Department
from datetime import datetime
from ..utils import get_week_count, default_content, permission_required
from config import Config


@main.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.my_report'))


@main.route('/write_report/', methods=['GET', 'POST'])
@login_required
def write_report():
    form = ReportForm()
    submit_form = ReportSubmitForm()
    report = Report.objects(
        author=current_user.username,
        week_count=get_week_count(),
        year=datetime.today().year
    ).first()
    if form.save.data and form.validate_on_submit():
        if report:
            report.content = form.body.data
            report.belong_project = form.project.data
            report.save()
        else:
            Report(content=form.body.data,
                   author=current_user.username,
                   created_at=datetime.now(),
                   week_count=get_week_count(),
                   belong_project=form.project.data,
                   year=datetime.today().year,
                   ).save()
    if report:
        form.body.data = report.content
        form.project.data = report.belong_project
    else:
        form.body.data = default_content

    if report and submit_form.submit.data and submit_form.validate_on_submit():
        report.confirmed = True
        report.save()

    return render_template('write_report.html',
                           form=form,
                           submit_form=submit_form,
                           week_count=get_week_count())


@main.route('/my_report/', methods=['GET'])
@main.route('/my_report/<int:page_count>', methods=['GET'])
@login_required
def my_report(page_count=1):
    pagination = Report.objects(author=current_user.username, confirmed=True).order_by(
        '-created_at').paginate(page=page_count, per_page=Config.PER_PAGE)
    return render_template('my_report.html', pagination=pagination)


# def is_allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in {'png', 'jpg', 'jpeg', 'gif'}
#
#
# @main.route("/upload/", methods=["POST"])
# def ck_upload():
#     form = ReportForm()
#     response = form.upload(endpoint=main)
#     return response


@main.route('/subordinate_report/', methods=['GET'])
@main.route('/subordinate_report/<int:page_count>', methods=['GET'])
@permission_required(Permission.READ_DEPARTMENT_REPORT)
def subordinate_report(page_count=1):

    qst = Report.objects.all()
    if not current_user.can(Permission.READ_ALL_REPORT):
        qst = qst(author__belong_department=current_user__belong_department)

    pagination = qst(confirmed=True).order_by('-created_at').paginate(
            page=page_count, per_page=Config.PER_PAGE)
    return render_template('subordinate_report.html', pagination=pagination)


class WeeklyReportModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))

admin.add_view(WeeklyReportModelView(User))
admin.add_view(WeeklyReportModelView(Report))
admin.add_view(WeeklyReportModelView(Project))
admin.add_view(WeeklyReportModelView(Department))
