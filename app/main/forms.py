from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, TextAreaField, SelectField
from ..models import Project
from flaskckeditor import CKEditor


class ReportForm(FlaskForm, CKEditor):
    body = TextAreaField('本周工作内容与下周计划',
                         validators=[DataRequired()])
    project = SelectField('项目', choices=[
        (project.name, project.name) for project in Project.objects(is_closed=False)])
    save = SubmitField('保存')


class ReportSubmitForm(FlaskForm):
    submit = SubmitField('提交考核')
