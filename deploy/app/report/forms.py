#coding:utf-8
from flask_babelex import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.fields.html5 import DateField


class WriteForm(FlaskForm):
    body = TextAreaField(_("This week's work content and plan of next week"),
                         validators=[DataRequired()])
    last_content = HiddenField(_("This week's work content and plan of last week"))                         
    submit = SubmitField(_('Submit'))


class ReadDepartmentForm(FlaskForm):
    user = SelectField(_('Username'))
    start_at = DateField(_('Start'), format='%Y-%m-%d')
    end_at = DateField(_('End'), format='%Y-%m-%d')
    submit = SubmitField(_('Query'))


class ReadCrewForm(ReadDepartmentForm):
    department = SelectField(_('Department'))


class EmailReminderForm(FlaskForm):
    submit = SubmitField(_('Send Reminder Email'))
