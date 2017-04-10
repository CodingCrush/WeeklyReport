from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import DateField
from ..models import User, Project, Department


class ReportForm(FlaskForm):
    body = TextAreaField('本周工作内容与下周计划',
                         validators=[DataRequired()])
    project = SelectField('项目', choices=[
        (project.name, project.name) for project in Project.objects(is_closed=False)])
    save = SubmitField('保存')


class ReportSubmitForm(FlaskForm):
    submit = SubmitField('提交考核')


class ReportFilterForm(FlaskForm):
    user_choices = [('*', '*')]
    department_choices = user_choices[:]
    projects_choices = user_choices[:]

    user_choices.extend([(user.username, user.username) for user in User.objects.all()])
    department_choices.extend([(dept.name, dept.name) for dept in Department.objects.all()])
    projects_choices.extend([(proj.name, proj.name) for proj in Project.objects.all()])

    user = SelectField('姓名', choices=user_choices)
    department = SelectField('部门', choices=department_choices)
    project = SelectField('项目', choices=projects_choices)
    start_at = DateField('开始日期', format='%Y-%m-%d')
    end_at = DateField('结束日期', format='%Y-%m-%d')
    submit = SubmitField('查询')
