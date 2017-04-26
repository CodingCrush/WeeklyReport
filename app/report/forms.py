from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import DateField


class WriteForm(FlaskForm):
    body = TextAreaField('本周工作内容与下周计划',
                         validators=[DataRequired()])
    save = SubmitField('提交')


class ReadDepartmentForm(FlaskForm):
    user = SelectField('姓名')
    start_at = DateField('开始', format='%Y-%m-%d')
    end_at = DateField('结束', format='%Y-%m-%d')
    submit = SubmitField('查询')


class ReadCrewForm(FlaskForm):
    user = SelectField('姓名')
    department = SelectField('部门')
    start_at = DateField('开始', format='%Y-%m-%d')
    end_at = DateField('结束', format='%Y-%m-%d')
    submit = SubmitField('查询')
