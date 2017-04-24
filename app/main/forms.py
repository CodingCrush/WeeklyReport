from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import DateField


class ReportForm(FlaskForm):
    body = TextAreaField('本周工作内容与下周计划',
                         validators=[DataRequired()])
    project = SelectField('项目')
    save = SubmitField('提交')


class ReportFilterForm(FlaskForm):
    user = SelectField('姓名')
    department = SelectField('部门')
    project = SelectField('项目')
    start_at = DateField('开始日期', format='%Y-%m-%d')
    end_at = DateField('结束日期', format='%Y-%m-%d')
    submit = SubmitField('查询')
