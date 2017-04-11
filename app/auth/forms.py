from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import BooleanField, SubmitField, \
    StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import User, Department


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), Length(2, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('提交')


class RegistrationForm(FlaskForm):
    email = EmailField('邮箱', validators=[
         DataRequired(), Length(1, 64)])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64)
        ])

    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    department = SelectField('部门', choices=[
        (str(dept.id), dept.name) for dept in Department.objects.all()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.objects(name=field.data):
            raise ValidationError('用户名已被注册')

    def validate_email(self, field):
        if User.objects(email=field.data):
            raise ValidationError('邮箱已被注册')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')
