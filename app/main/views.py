from flask import render_template, request, Response, redirect, url_for
from flask_admin.contrib.mongoengine import ModelView
from flask_login import current_user
from config import Config
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from . import main
from .forms import ReportForm, ReportSubmitForm, ReportFilterForm
from .. import admin
from ..models import Permission, User, Report, Project, Department
from ..utils import get_week_count, default_content, \
    permission_required, is_allowed_file, get_this_monday


@main.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.my_report'))


@main.route('/write_report/', methods=['GET', 'POST'])
@permission_required(Permission.WRITE_REPORT)
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
            report.project = Project.objects(name=form.project.data).first()
            report.save()
        else:
            Report(content=form.body.data,
                   author=current_user.username,
                   project=Project.objects(name=form.project.data).first(),
                   created_at=datetime.now(),
                   week_count=get_week_count(),
                   year=datetime.today().year,
                   ).save()
        return redirect(url_for('main.write_report'))

    if report and submit_form.submit.data and \
            submit_form.validate_on_submit():
        report.confirmed = True
        report.save()

    if report:
        form.body.data = report.content
        form.project.data = report.project.name
    else:
        form.body.data = default_content
    return render_template('write_report.html',
                           form=form,
                           submit_form=submit_form,
                           week_count=get_week_count())


@main.route("/upload/", methods=["POST"])
@permission_required(Permission.WRITE_REPORT)
def upload():
    img = request.files.get('image')
    if img and is_allowed_file(img.filename):
        filename = secure_filename(img.filename)
        img.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        img_url = request.url_root + Config.IMAGE_UPLOAD_DIR + filename
        res = Response(img_url)

    else:
        res = Response("上传失败")
    res.headers["ContentType"] = "text/html"
    res.headers["Charset"] = "utf-8"
    return res


@main.route('/my_report/', methods=['GET'])
@main.route('/my_report/<int:page_count>', methods=['GET'])
@permission_required(Permission.WRITE_REPORT)
def my_report(page_count=1):
    pagination = Report.objects(author=current_user.username, confirmed=True).\
        order_by('-created_at').paginate(page=page_count, per_page=Config.PER_PAGE)
    return render_template('my_report.html', pagination=pagination)


@main.route('/subordinate_report/', methods=['GET', 'POST'])
@main.route('/subordinate_report/<int:page_count>', methods=['GET', 'POST'])
@permission_required(Permission.READ_DEPARTMENT_REPORT)
def subordinate_report(page_count=1):
    form = ReportFilterForm()

    qst = Report.objects.all()

    if form.validate_on_submit():
        if not form.user.data == '*':
            qst = qst(author=form.user.data)
        if not form.project.data == '*':
            qst = qst(project=Project.objects(name=form.project.data).first())
        if not form.department.data == '*':
            users = User.objects(department=Department.objects(name=form.department.data).first())
            qst = qst(author__in=[user.username for user in users])
        pagination = qst(created_at__lte=form.end_at.data,
                         created_at__gte=form.start_at.data,
                         confirmed=True).\
            order_by('-created_at').paginate(
            page=page_count, per_page=Config.PER_PAGE)

        return render_template('subordinate_report.html',
                               form=form,
                               pagination=pagination)

    if not current_user.can(Permission.READ_ALL_REPORT):
        qst = qst(author__department=current_user__department)

    form.start_at.data = get_this_monday()
    form.end_at.data = datetime.now()+timedelta(hours=24)

    pagination = qst(confirmed=True).order_by('-created_at').paginate(
            page=page_count, per_page=Config.PER_PAGE)
    return render_template('subordinate_report.html',
                           form=form,
                           pagination=pagination)


class WeeklyReportModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))

admin.add_view(WeeklyReportModelView(User))
admin.add_view(WeeklyReportModelView(Report))
admin.add_view(WeeklyReportModelView(Project))
admin.add_view(WeeklyReportModelView(Department))
