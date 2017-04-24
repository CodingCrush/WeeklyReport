from flask import render_template, request, Response, redirect, \
    url_for, current_app, flash
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from . import main
from .forms import ReportForm, ReportFilterForm
from .. import admin, db
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
    form.project.choices = [
        (str(project.id), project.name) for project in Project.query.filter_by(is_closed=False)]

    report = Report.query.filter_by(
        author_id=current_user.id,
        week_count=get_week_count(),
        year=datetime.today().year
    ).first()
    if form.save.data and form.validate_on_submit():
        if report:
            report.content = form.body.data.replace('<br>', '')
            report.project_id = Project.query.get(form.project.data).id
            db.session.add(report)
        else:
            report = Report(
                content=form.body.data.replace('<br>', ''),
                author_id=current_user.id,
                project_id=Project.query.get(form.project.data).id,
                week_count=get_week_count(),
                year=datetime.today().year)
            db.session.add(report)
        db.session.commit()
        flash('周报提交成功')

        current_app.logger.info(
            '{} submitted report'.format(current_user.email))

        return redirect(url_for('main.write_report'))

    if report:
        form.body.data = report.content
        form.project.data = report.project_id
    else:
        form.body.data = default_content

    return render_template('write_report.html',
                           form=form,
                           week_count=get_week_count(),
                           start_at=get_this_monday(),
                           end_at=get_this_monday()+timedelta(days=6))


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


@main.route('/edit_last_week_report/', methods=['GET', 'POST'])
@permission_required(Permission.WRITE_REPORT)
def edit_last_week_report():
    form = ReportForm()
    form.project.choices = [
        (str(project.id), project.name) for project in Project.query.filter_by(is_closed=False)]

    last_week = datetime.now() - timedelta(days=7)
    last_week_start_at = get_this_monday() - timedelta(days=7)
    last_week_end_at = get_this_monday()

    report = Report.query.filter_by(
        author_id=current_user.id,
        week_count=get_week_count(last_week),
        year=last_week.year).first()

    if form.save.data and form.validate_on_submit():
        if report:
            report.content = form.body.data.replace('<br>', '')
            report.project_id = form.project.data
            report.project = Project.query.get(form.project.data)
        else:
            report = Report(
                content=form.body.data.replace('<br>', ''),
                author_id=current_user.id,
                project_id=form.project.data,
                week_count=get_week_count(last_week),
                year=last_week.year)
        db.session.add(report)
        db.session.commit()
        flash('周报提交成功')

        current_app.logger.info(
            "{} edited last week's report".format(current_user.email))

        return redirect(url_for('main.edit_last_week_report'))

    if report:
        form.body.data = report.content
        form.project.data = report.project_id
    else:
        form.body.data = default_content
    return render_template('write_report.html',
                           form=form,
                           week_count=get_week_count(last_week),
                           start_at=last_week_start_at,
                           end_at=last_week_end_at-timedelta(days=1))


@main.route('/my_report/', methods=['GET'])
@main.route('/my_report/<int:page_count>', methods=['GET'])
@permission_required(Permission.WRITE_REPORT)
def my_report(page_count=1):
    pagination = Report.query.filter_by(author_id=current_user.id).order_by(
        Report.created_at.desc()).paginate(
        page=page_count, per_page=current_app.config['PER_PAGE'])
    if not Report.query.filter_by(
            author_id=current_user.id,
            week_count=get_week_count(),
            year=datetime.today().year):
        flash('您的本周周报还未提交')
    return render_template('my_report.html', pagination=pagination)


@main.route('/subordinate_report/', methods=['GET', 'POST'])
@main.route('/subordinate_report/<int:page_count>', methods=['GET', 'POST'])
@permission_required(Permission.READ_DEPARTMENT_REPORT)
def subordinate_report(page_count=1):
    form = ReportFilterForm()

    user_choices = [('*', '*')]
    department_choices = user_choices[:]
    projects_choices = user_choices[:]

    user_choices.extend([(str(user.id), user.username) for user in User.query.all()])
    department_choices.extend([(str(dept.id), dept.name) for dept in Department.query.all()])
    projects_choices.extend([(str(proj.id), proj.name) for proj in Project.query.all()])

    form.user.choices = user_choices
    form.department.choices = department_choices
    form.project.choices = projects_choices

    qst = Report.query.filter_by()

    if form.validate_on_submit():
        qst = qst.filter(Report.created_at.between(
            form.start_at.data, form.end_at.data))

        if not form.department.data == '*':
            ids = [user.id for user in User.query.filter_by(
                department_id=form.department.data)]
            qst = qst.filter(Report.author_id.in_(ids))

        if not form.user.data == '*':
            qst = qst.filter_by(author_id=form.user.data)
        if not form.project.data == '*':
            qst = qst.filter_by(project_id=form.project.data)

        pagination = qst.paginate(
            page=page_count, per_page=current_app.config['PER_PAGE'])
        return render_template('subordinate_report.html',
                               form=form,
                               pagination=pagination)

    if not current_user.can(Permission.READ_ALL_REPORT):
        ids = [user.id for user in User.query.filter_by(
            department_id=current_user.department_id)]
        qst = qst.filter(Report.author_id.in_(ids))

    form.start_at.data = get_this_monday()
    form.end_at.data = datetime.now()+timedelta(hours=24)

    pagination = qst.filter_by().order_by(Report.created_at.desc()).paginate(
            page=page_count, per_page=current_app.config['PER_PAGE'])
    return render_template('subordinate_report.html',
                           form=form,
                           pagination=pagination)


@main.route('/statistics_report/', methods=['GET'])
@permission_required(Permission.READ_DEPARTMENT_REPORT)
def statistics_report():
    if not current_user.can(Permission.READ_ALL_REPORT):
        qst = Report.query.filter_by()
        dept_users = [user for user in User.query.filter_by(
            department_id=current_user.department_id) if user.is_authenticated]
        ids = [user.id for user in dept_users]
        if ids:
            qst = qst.filter(Report.author_id.in_(ids))

        submitted_users = [
            report.get_author_name() for report in qst.filter_by(
                week_count=get_week_count(),
                year=datetime.today().year)]

        data = {'已交': len(submitted_users),
                '未交': len(dept_users)-len(submitted_users)}
        names = {'has_submitted': submitted_users,
                 'not_yet': set([user.username for user in dept_users]
                                )-set(submitted_users)}

        return render_template('statistics_department.html',
                               data=data,
                               names=names,
                               week_count=get_week_count())

    stash = []
    contrast = {}
    for dept in Department.query.filter_by():
        qst = Report.query.filter_by()
        dept_users = [user for user in User.query.filter_by(
            department_id=dept.id) if user.is_authenticated]
        ids = [user.id for user in dept_users]
        if ids:
            qst = qst.filter(Report.author_id.in_(ids))
        else:
            qst = qst.filter(False)
        submitted_users = [
            report.get_author_name() for report in qst.filter_by(
                week_count=get_week_count(),
                year=datetime.today().year)]

        names = {'has_submitted': submitted_users,
                 'not_yet': set([user.username for user in dept_users]
                                )-set(submitted_users)}

        stash.append({'names': names,
                      'dept_name': dept.name
                      })
        contrast[dept.name] = len(dept_users) - len(submitted_users)

    return render_template('statistics_all.html',
                           contrast=contrast,
                           stash=stash,
                           week_count=get_week_count())


class WeeklyReportModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Report, db.session))
admin.add_view(ModelView(Project, db.session))
admin.add_view(ModelView(Department, db.session))
