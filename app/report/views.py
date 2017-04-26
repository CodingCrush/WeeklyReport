from flask import render_template, redirect, url_for, current_app, flash
from flask_login import current_user
from datetime import datetime, timedelta
from . import report
from .forms import WriteForm, ReadDepartmentForm, ReadCrewForm
from .. import db
from ..models import Permission, User, Report, Department
from ..utils import get_week_count, permission_required, get_this_monday, \
    get_last_week, get_last_week_start_at, get_last_week_end_at


@report.route('/write/', methods=['GET', 'POST'])
@permission_required(Permission.WRITE_REPORT)
def write():
    form = WriteForm()
    report = Report.query.filter_by(
        author_id=current_user.id,
        week_count=get_week_count(),
        year=datetime.today().year
    ).first()
    if form.save.data and form.validate_on_submit():
        if report:
            report.content = form.body.data.replace('<br>', '')
            db.session.add(report)
        else:
            report = Report(
                content=form.body.data.replace('<br>', ''),
                author_id=current_user.id,
                week_count=get_week_count(),
                year=datetime.today().year)
            db.session.add(report)
        db.session.commit()
        flash('周报提交成功')

        current_app.logger.info(
            '{} submitted report'.format(current_user.email))

        return redirect(url_for('report.write'))

    if report:
        form.body.data = report.content
    else:
        form.body.data = current_app.config['DEFAULT_CONTENT']

    return render_template('report/write.html',
                           form=form,
                           week_count=get_week_count(),
                           start_at=get_this_monday(),
                           end_at=get_this_monday()+timedelta(days=6))


@report.route('/write/last_week', methods=['GET', 'POST'])
@permission_required(Permission.WRITE_REPORT)
def write_last_week():
    form = WriteForm()

    report = Report.query.filter_by(
        author_id=current_user.id,
        week_count=get_week_count(get_last_week()),
        year=get_last_week().year).first()

    if form.save.data and form.validate_on_submit():
        if report:
            report.content = form.body.data.replace('<br>', '')
        else:
            report = Report(
                content=form.body.data.replace('<br>', ''),
                author_id=current_user.id,
                week_count=get_week_count(get_last_week()),
                year=get_last_week().year)
        db.session.add(report)
        db.session.commit()
        flash('周报提交成功')

        current_app.logger.info(
            "{} edited last week's report".format(current_user.email))

        return redirect(url_for('report.write_last_week'))

    if report:
        form.body.data = report.content
    else:
        form.body.data = current_app.config['DEFAULT_CONTENT']
    return render_template('report/write.html',
                           form=form,
                           week_count=get_week_count(get_last_week()),
                           start_at=get_last_week_start_at(),
                           end_at=get_last_week_end_at() - timedelta(days=1))


@report.route('/read/', methods=['GET'])
@report.route('/read/<int:page_count>', methods=['GET'])
@permission_required(Permission.WRITE_REPORT)
def read(page_count=1):
    pagination = Report.query.filter_by(author_id=current_user.id).order_by(
        Report.created_at.desc()).paginate(
        page=page_count, per_page=current_app.config['PER_PAGE'])
    if not Report.query.filter_by(
            author_id=current_user.id,
            week_count=get_week_count(),
            year=datetime.today().year):
        flash('您的本周周报还未提交')
    return render_template('report/read.html', pagination=pagination)


@report.route('/read/department/', methods=['GET', 'POST'])
@report.route('/read/department/<int:page_count>', methods=['GET', 'POST'])
@permission_required(Permission.READ_DEPARTMENT_REPORT)
def read_department(page_count=1):
    form = ReadDepartmentForm()

    user_choices = [('*', '*')]
    user_choices.extend([(str(user.id), user.username) for user in User.query.all()])
    form.user.choices = user_choices

    qst = Report.query.filter_by()

    if form.validate_on_submit():
        qst = qst.filter(Report.created_at.between(
            form.start_at.data, form.end_at.data))

        if not form.user.data == '*':
            qst = qst.filter_by(author_id=form.user.data)

        pagination = qst.paginate(
            page=page_count, per_page=current_app.config['PER_PAGE'])
        return render_template('report/read_department.html',
                               form=form,
                               pagination=pagination)

    ids = [user.id for user in User.query.filter_by(
        department_id=current_user.department_id)]
    qst = qst.filter(Report.author_id.in_(ids))

    form.start_at.data = get_this_monday()
    form.end_at.data = datetime.now()+timedelta(hours=24)

    pagination = qst.filter_by().order_by(Report.created_at.desc()).paginate(
            page=page_count, per_page=current_app.config['PER_PAGE'])
    return render_template('report/read_department.html',
                           form=form,
                           pagination=pagination)


@report.route('/read/crew/', methods=['GET', 'POST'])
@report.route('/read/crew/<int:page_count>', methods=['GET', 'POST'])
@permission_required(Permission.READ_ALL_REPORT)
def read_crew(page_count=1):
    form = ReadCrewForm()

    user_choices = [('*', '*')]
    department_choices = user_choices[:]

    user_choices.extend([(str(user.id), user.username) for user in User.query.all()])
    department_choices.extend([(str(dept.id), dept.name) for dept in Department.query.all()])

    form.user.choices = user_choices
    form.department.choices = department_choices

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

        pagination = qst.paginate(
            page=page_count, per_page=current_app.config['PER_PAGE'])
        return render_template('report/read_crew.html',
                               form=form,
                               pagination=pagination)

    form.start_at.data = get_this_monday()
    form.end_at.data = datetime.now()+timedelta(hours=24)

    pagination = qst.filter_by().order_by(Report.created_at.desc()).paginate(
            page=page_count, per_page=current_app.config['PER_PAGE'])
    return render_template('report/read_crew.html',
                           form=form,
                           pagination=pagination)


@report.route('/statistics/department/', methods=['GET'])
@permission_required(Permission.READ_DEPARTMENT_REPORT)
def statistics_department():
    qst = Report.query.filter_by()
    dept_users = [user for user in User.query.filter_by(
        department_id=current_user.department_id) if not user.is_ignored]
    ids = [user.id for user in dept_users]
    if ids:
        qst = qst.filter(Report.author_id.in_(ids))
    else:
        qst = qst.filter(False)
    submitted_users = [
        report.get_author_name() for report in qst.filter_by(
            week_count=get_week_count(),
            year=datetime.today().year)]

    data = {'已交': len(submitted_users),
            '未交': len(dept_users)-len(submitted_users)}
    names = {'has_submitted': submitted_users,
             'not_yet': set([user.username for user in dept_users]
                            )-set(submitted_users)}

    return render_template('report/statistics_department.html',
                           data=data,
                           names=names,
                           week_count=get_week_count(),
                           start_at=get_this_monday(),
                           end_at=get_this_monday() + timedelta(days=6))


@report.route('/statistics/crew/', methods=['GET'])
@permission_required(Permission.READ_ALL_REPORT)
def statistics_crew():
    stash = []
    contrast = {}
    for dept in Department.query.filter_by():
        qst = Report.query.filter_by()
        dept_users = [user for user in User.query.filter_by(
            department_id=dept.id) if not user.is_ignored]
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

    return render_template('report/statistics_crew.html',
                           contrast=contrast,
                           stash=stash,
                           week_count=get_week_count(),
                           start_at=get_this_monday(),
                           end_at=get_this_monday() + timedelta(days=6))


@report.route('/statistics/department/last_week', methods=['GET'])
@permission_required(Permission.READ_DEPARTMENT_REPORT)
def statistics_department_last_week():
    qst = Report.query.filter_by()
    dept_users = [user for user in User.query.filter_by(
        department_id=current_user.department_id) if not user.is_ignored]
    ids = [user.id for user in dept_users]
    if ids:
        qst = qst.filter(Report.author_id.in_(ids))
    else:
        qst = qst.filter(False)
    submitted_users = [
        report.get_author_name() for report in qst.filter_by(
            week_count=get_week_count(get_last_week()),
            year=get_last_week().year)]

    data = {'已交': len(submitted_users),
            '未交': len(dept_users)-len(submitted_users)}
    names = {'has_submitted': submitted_users,
             'not_yet': set([user.username for user in dept_users]
                            )-set(submitted_users)}

    return render_template('report/statistics_department.html',
                           data=data,
                           names=names,
                           week_count=get_week_count(get_last_week()),
                           start_at=get_last_week_start_at(),
                           end_at=get_last_week_end_at() - timedelta(days=1))


@report.route('/statistics/crew/last_week', methods=['GET'])
@permission_required(Permission.READ_ALL_REPORT)
def statistics_crew_last_week():
    stash = []
    contrast = {}
    for dept in Department.query.filter_by():
        qst = Report.query.filter_by()
        dept_users = [user for user in User.query.filter_by(
            department_id=dept.id) if not user.is_ignored]
        ids = [user.id for user in dept_users]
        if ids:
            qst = qst.filter(Report.author_id.in_(ids))
        else:
            qst = qst.filter(False)
        submitted_users = [
            report.get_author_name() for report in qst.filter_by(
                week_count=get_week_count(get_last_week()),
                year=get_last_week().year)]

        names = {'has_submitted': submitted_users,
                 'not_yet': set([user.username for user in dept_users]
                                )-set(submitted_users)}

        stash.append({'names': names,
                      'dept_name': dept.name
                      })
        contrast[dept.name] = len(dept_users) - len(submitted_users)

    return render_template('report/statistics_crew.html',
                           contrast=contrast,
                           stash=stash,
                           week_count=get_week_count(get_last_week()),
                           start_at=get_last_week_start_at(),
                           end_at=get_last_week_end_at() - timedelta(days=1))
