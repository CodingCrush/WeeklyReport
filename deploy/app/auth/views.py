from flask import render_template, redirect, url_for, \
    flash, current_app, request
from flask_babelex import lazy_gettext as _
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..email import send_email
from ..models import Role, Department, User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    ChangeUsernameForm, PasswordResetRequestForm, PasswordResetForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            current_app.logger.info(
                '{} login'.format(current_user.email))

            return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out'))
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    form.department.choices = [
        (str(dept.id), dept.name) for dept in Department.query.all()]

    if form.validate_on_submit():
        exist_users = bool(User.query.all())

        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            role=Role.query.filter_by(name='EMPLOYEE').first(),
            department=Department.query.get(form.department.data))

        if not exist_users:
            user.role = Role.query.filter_by(name='ADMINISTRATOR').first()
            user.is_super_admin = True
            user.is_ignored = True

        db.session.add(user)
        db.session.commit()
        login_user(user, False)
        flash(_('Successfully Registered, Please Login'))

        current_app.logger.info(
            '{} register'.format(user.email))

        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash(_('Your password has been updated'))

            current_app.logger.info(
                '{} changes password'.format(current_user.email))

            return redirect(url_for('main.index'))
    return render_template("auth/change_password.html", form=form)


@auth.route('/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.username = form.username.data
            db.session.add(current_user)
            flash(_('Your username has been updated'))

            current_app.logger.info(
                '{} changes username from {} to {}'.format(
                    current_user.email, form.username.data, current_user.username))

            return redirect(url_for('main.index'))
    return render_template("auth/change_username.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email([user.email], 'Reset Your Password',
                       'email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))

        current_app.logger.info(
            '{} request for reset password'.format(user.email))

        flash(_('An email with instructions to reset your password has been '
              'sent to ') + user.email)
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):

            current_app.logger.info(
                '{} reset password'.format(user.email))

            flash(_('Your password has been updated.'))
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
