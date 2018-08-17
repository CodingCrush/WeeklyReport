#coding:utf-8
from flask import render_template, redirect,request, url_for, \
    current_app, flash, Markup
from flask_babelex import lazy_gettext as _
from flask_login import current_user
from datetime import datetime, timedelta, date
from . import report
from .forms import WriteForm, ReadDepartmentForm, \
    ReadCrewForm, EmailReminderForm
from .. import db
from ..email import send_email
from ..models import Permission, User, Report, Department
from ..utils import get_week_count, permission_required, get_this_monday, \
    get_last_week, get_last_week_start_at, get_last_week_end_at, get_last_week_content


@report.route('/write/', methods=['GET', 'POST'])
@permission_required(Permission.WRITE_REPORT)
def write():
    form = WriteForm()
    last_content_display = ""
    report = Report.query.filter_by(
        author_id=current_user.id,
        week_count=get_week_count(),
        year=datetime.today().year
    ).first()
    
    last_report = Report.query.filter_by(
        author_id=current_user.id,
        week_count=get_week_count() - 1,
        year=datetime.today().year
    ).first()
            
    if form.submit.data and form.validate_on_submit():
        if report:
            report.content = form.body.data.replace('<br>', '')
            report.last_content = form.last_content.data.replace('<br>', '')
            db.session.add(report)
        else:
            report = Report(
                content=form.body.data.replace('<br>', ''),
                last_content=form.last_content.data.replace('<br>', ''),
                author_id=current_user.id,
                week_count=get_week_count(),
                year=datetime.today().year)
            db.session.add(report)
        db.session.commit()
        flash(_('Successfully submitted report'))

        current_app.logger.info(
            '{} submitted report'.format(current_user.email))

        return redirect(url_for('report.write'))

    if report:
        form.body.data = report.content
    else:
        form.body.data = current_app.config['DEFAULT_CONTENT']
        
    if last_report:
        form.last_content.data = last_report.content
        last_content_display = get_last_week_content(last_report.content)

    return render_template('report/write.html',
                           form=form,
                           week_count=get_week_count(),
                           start_at=get_this_monday(),
                           end_at=get_this_monday()+timedelta(days=6),
                           last_content_display=last_content_display)


@report.route('/write/last_week', methods=['GET', 'POST'])
@permission_required(Permission.WRITE_REPORT)
def write_last_week():
    form = WriteForm()
    last_content_display = ""
    
    report = Report.query.filter_by(
        author_id=current_user.id,
        week_count=get_week_count(get_last_week()),
        year=get_last_week().year).first()
        
    last_report = Report.query.filter_by(
        author_id=current_user.id,
        week_count=get_week_count(get_last_week()) - 1,
        year=get_last_week().year).first()

    if form.submit.data and form.validate_on_submit():
        if report:
            report.content = form.body.data.replace('<br>', '')
            report.last_content = form.last_content.data.replace('<br>', '')
        else:
            report = Report(
                content=form.body.data.replace('<br>', ''),
                author_id=current_user.id,
                week_count=get_week_count(get_last_week()),
                year=get_last_week().year)
        db.session.add(report)
        db.session.commit()
        flash(_('Successfully submitted report'))

        current_app.logger.info(
            "{} edited last week's report".format(current_user.email))

        return redirect(url_for('report.write_last_week'))

    if report:
        form.body.data = report.content
    else:
        form.body.data = current_app.config['DEFAULT_CONTENT']
        
    if last_report:
        form.last_content.data = last_report.content
        last_content_display = get_last_week_content(last_report.content)
                
    return render_template('report/write.html',
                           form=form,
                           week_count=get_week_count(get_last_week()),
                           start_at=get_last_week_start_at(),
                           end_at=get_last_week_end_at() - timedelta(days=1),
                           last_content_display=last_content_display)


@report.route('/read/', methods=['GET'])
@report.route('/read/<int:page_count>', methods=['GET'])
@permission_required(Permission.WRITE_REPORT)
def read(page_count=1):
    if not Report.query.filter_by(
            author_id=current_user.id,
            week_count=get_week_count(get_last_week()),
            year=get_last_week().year).first():
        flash(Markup(_("Do you want to <a href='/report/write/last_week'>"
                       "edit last week's report?</a>")))

    pagination = Report.query.filter_by(author_id=current_user.id).order_by(
        Report.year.desc()).order_by(Report.week_count.desc()).paginate(
        page=page_count, per_page=current_app.config['PER_PAGE'])
    if not Report.query.filter_by(
            author_id=current_user.id,
            week_count=get_week_count(),
            year=datetime.today().year):
        flash(_("You haven't submitted your weekly report"))
    return render_template('report/read.html', pagination=pagination)


@report.route('/read/department/', methods=['GET', 'POST'])
@permission_required(Permission.READ_DEPARTMENT_REPORT)
def read_department():
    form = ReadDepartmentForm()

    user_choices = [('0', '*')]
    user_choices.extend([(
        str(user.id), user.username) for user in User.query.all()])
    form.user.choices = user_choices

    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user', 0, type=int)
    start_at = request.args.get('start_at', '', type=str)
    end_at = request.args.get('end_at', '', type=str)

    start_at = get_last_week_start_at() if not start_at \
        else datetime.strptime(start_at[:10], '%Y-%m-%d')
    end_at = date.today()+timedelta(hours=24) if not end_at \
        else datetime.strptime(end_at[:10], '%Y-%m-%d')

    form.start_at.data = start_at
    form.end_at.data = end_at
    form.user.data = str(user_id)

    ids = [user.id for user in User.query.filter_by(
        department_id=current_user.department_id)]

    qst = Report.query.filter_by().filter(
        Report.created_at.between(start_at, end_at)).filter(
        Report.author_id.in_(ids))

    if user_id:
        qst = qst.filter_by(author_id=user_id)

    if form.validate_on_submit():
        pass

    pagination = qst.filter_by().order_by(Report.year.desc()).order_by(
        Report.week_count.desc()).order_by(Report.created_at.desc()).paginate(
            page=page, per_page=current_app.config['PER_PAGE'])

    return render_template('report/read_department.html',
                           form=form,
                           pagination=pagination)


@report.route('/read/crew/', methods=['GET', 'POST'])
@permission_required(Permission.READ_ALL_REPORT)
def read_crew():
    form = ReadCrewForm()
    user_choices = [('0', '*')]
    department_choices = user_choices[:]

    for dept in Department.query.all():
        department_choices.extend([(str(dept.id), dept.name)])
        user_choices.extend([(str(user.id), user.username) for user in
                             User.query.filter_by(department_id=dept.id)])

    form.user.choices = user_choices
    form.department.choices = department_choices

    page = request.args.get('page', 1, type=int)
    department_id = request.args.get('department', 0, type=int)
    user_id = request.args.get('user', 0, type=int)
    start_at = request.args.get('start_at', '', type=str)
    end_at = request.args.get('end_at', '', type=str)

    start_at = get_last_week_start_at() if not start_at \
        else datetime.strptime(start_at[:10], '%Y-%m-%d')
    end_at = date.today()+timedelta(hours=24) if not end_at \
        else datetime.strptime(end_at[:10], '%Y-%m-%d')

    form.start_at.data = start_at
    form.end_at.data = end_at
    form.user.data = str(user_id)
    form.department.data = str(department_id)

    qst = Report.query.filter_by().filter(
        Report.created_at.between(start_at, end_at))

    if department_id:
        ids = [user.id for user in User.query.filter_by(
            department_id=department_id)]
        qst = qst.filter(Report.author_id.in_(ids))

    if user_id:
        qst = qst.filter_by(author_id=user_id)

    if form.validate_on_submit():
        pass

    pagination = qst.filter_by().order_by(Report.year.desc()).order_by(
        Report.week_count.desc()).order_by(Report.created_at.desc()).paginate(
            page=page, per_page=current_app.config['PER_PAGE'])

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
        report.author for report in qst.filter_by(
            week_count=get_week_count(),
            year=datetime.today().year)]
    unsubmitted_users = set(dept_users) - set(submitted_users)

    data = {'已交': len(submitted_users),
            '未交': len(unsubmitted_users)}
    names = {'has_submitted': [user.username for user in submitted_users],
             'not_yet': [user.username for user in unsubmitted_users]}

    return render_template('report/statistics_department.html',
                           data=data,
                           names=names,
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
        report.author for report in qst.filter_by(
            week_count=get_week_count(get_last_week()),
            year=get_last_week().year)]
    unsubmitted_users = set(dept_users) - set(submitted_users)

    data = {'已交': len(submitted_users),
            '未交': len(unsubmitted_users)}
    names = {'has_submitted': [user.username for user in submitted_users],
             'not_yet': [user.username for user in unsubmitted_users]}

    return render_template('report/statistics_department.html',
                           data=data,
                           names=names,
                           week_count=get_week_count(get_last_week()),
                           start_at=get_last_week_start_at(),
                           end_at=get_last_week_end_at() - timedelta(days=1))


@report.route('/statistics/crew/', methods=['GET', 'POST'])
@permission_required(Permission.READ_ALL_REPORT)
def statistics_crew():
    stash = []
    contrast = {}
    reminder_emails = set()
    form = EmailReminderForm()
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
            report.author for report in qst.filter_by(
                week_count=get_week_count(),
                year=datetime.today().year)]

        unsubmitted_users = set(dept_users)-set(submitted_users)
        reminder_emails |= set([user.email for user in unsubmitted_users])

        names = {'has_submitted': [user.username for user in submitted_users],
                 'not_yet': [user.username for user in unsubmitted_users]}

        stash.append({'names': names,
                      'dept_name': dept.name})

        contrast[dept.name] = len(dept_users) - len(submitted_users)

    if form.validate_on_submit():
        subject = 'Reminder of Report of week' + str(get_week_count()) + \
                  ' From:' + str(get_this_monday()) + \
                  ' To:' + str(get_this_monday() + timedelta(days=6))
        send_email(reminder_emails, subject,
                   'email/reminder',
                   user=current_user,
                   week_count=get_week_count(),
                   start_at=get_this_monday(),
                   end_at=get_this_monday() + timedelta(days=6))
        flash(_('Email has been sent to:') + '\n{}'.format(reminder_emails))

    return render_template('report/statistics_crew.html',
                           contrast=contrast,
                           stash=stash,
                           week_count=get_week_count(),
                           form=form,
                           start_at=get_this_monday(),
                           end_at=get_this_monday() + timedelta(days=6))


@report.route('/statistics/crew/last_week', methods=['GET', 'POST'])
@permission_required(Permission.READ_ALL_REPORT)
def statistics_crew_last_week():
    stash = []
    contrast = {}
    reminder_emails = set()
    form = EmailReminderForm()
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
            report.author for report in qst.filter_by(
                week_count=get_week_count(get_last_week()),
                year=get_last_week().year)]

        unsubmitted_users = set(dept_users)-set(submitted_users)
        reminder_emails |= set([user.email for user in unsubmitted_users])

        names = {'has_submitted': [user.username for user in submitted_users],
                 'not_yet': [user.username for user in unsubmitted_users]}

        stash.append({'names': names,
                      'dept_name': dept.name})
        contrast[dept.name] = len(dept_users) - len(submitted_users)

    if form.validate_on_submit():
        subject = 'Reminder of Report of week' + str(get_week_count(get_last_week())) + \
                  ' From:' + str(get_last_week_start_at()) + \
                  ' To:' + str(get_last_week_end_at() - timedelta(days=1))
        send_email(reminder_emails, subject,
                   'email/reminder',
                   user=current_user,
                   week_count=get_week_count(get_last_week()),
                   start_at=get_last_week_start_at(),
                   end_at=get_last_week_end_at() - timedelta(days=1))
        flash(_('Email has been sent to:') + '\n{}'.format(reminder_emails))
    return render_template('report/statistics_crew.html',
                           contrast=contrast,
                           stash=stash,
                           form=form,
                           week_count=get_week_count(get_last_week()),
                           start_at=get_last_week_start_at(),
                           end_at=get_last_week_end_at() - timedelta(days=1))
