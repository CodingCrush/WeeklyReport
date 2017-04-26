from flask_babelex import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import BooleanField, SubmitField, \
    StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = EmailField(_('Email'), validators=[
        DataRequired(), Length(2, 64)])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_('Remember Password'))
    submit = SubmitField(_('Submit'))


class RegistrationForm(FlaskForm):
    email = EmailField(_('Email'), validators=[
         DataRequired(), Length(1, 64)])
    username = StringField(_('Username'), validators=[
        DataRequired(), Length(1, 64)
        ])

    password = PasswordField(_('Password'), validators=[
        DataRequired(), EqualTo('password2', message=_("Passwords doesn't match"))])
    password2 = PasswordField(_('Confirm Password'), validators=[DataRequired()])
    department = SelectField(_('Department'))
    submit = SubmitField(_('Register'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_('Username has been used'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(_('Email has been registered'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_('Old Password'), validators=[DataRequired()])
    password = PasswordField(_('New Password'), validators=[
        DataRequired(), EqualTo('password2', message=_("Passwords doesn't match"))])
    password2 = PasswordField(_('Confirm New Password'), validators=[DataRequired()])
    submit = SubmitField(_('Update Password'))


class ChangeUsernameForm(FlaskForm):
    password = PasswordField(_('Password'), validators=[
        DataRequired()])
    username = StringField(_('New Username'), validators=[
        DataRequired(), Length(1, 64), EqualTo('username2', message=_("Usernames doesn't match"))])
    username2 = StringField(_('Confirm New Username'), validators=[
        DataRequired(), Length(1, 64)])
    submit = SubmitField(_('Update Username'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_('Username has been used'))
