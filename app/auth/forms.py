from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import BooleanField, SubmitField, \
    StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = EmailField('邮箱', validators=[
        DataRequired(), Length(2, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField('提交')


class RegistrationForm(FlaskForm):
    email = EmailField('邮箱', validators=[
         DataRequired(), Length(1, 64)])
    username = StringField('姓名', validators=[
        DataRequired(), Length(1, 64)
        ])

    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码不匹配')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    department = SelectField('部门')
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('姓名已被注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码不匹配')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('更新密码')


class ChangeUsernameForm(FlaskForm):
    password = PasswordField('密码', validators=[
        DataRequired()])
    username = StringField('新用户名', validators=[
        DataRequired(), Length(1, 64), EqualTo('username2', message='两次用户名不匹配')])
    username2 = StringField('确认新用户名', validators=[
        DataRequired(), Length(1, 64)])
    submit = SubmitField('更新密码')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('姓名已被注册')


# class PasswordResetRequestForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Length(1, 64),
#                                              Email()])
#     submit = SubmitField('Reset Password')
#
#
# class PasswordResetForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Length(1, 64),
#                                              Email()])
#     password = PasswordField('New Password', validators=[
#         DataRequired(), EqualTo('password2', message='Passwords must match')])
#     password2 = PasswordField('Confirm password', validators=[DataRequired()])
#     submit = SubmitField('Reset Password')
#
#     def validate_email(self, field):
#         if User.query.filter_by(email=field.data).first() is None:
#             raise ValidationError('Unknown email address.')
