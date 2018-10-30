#coding:utf-8
import os


base_dir = os.path.dirname(os.path.realpath(__file__))

DEBUG = True

SECRET_KEY = os.environ.get('SECRET_KEY') or 'nobody knows the password'
PER_PAGE = 10

SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = True

IMAGE_UPLOAD_DIR = 'static/upload/'
UPLOAD_FOLDER = os.path.join(base_dir, 'app/static/upload/')

#MAIL_SERVER = 'smtp.163.com'
MAIL_SERVER = ''
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = '<EMAIL@ADDRESS>'
MAIL_PASSWORD = '<EMAIL_PASSWORD>'

WR_MAIL_SUBJECT_PREFIX = '[WeeklyReport]'
WR_MAIL_SENDER = 'WeeklyReport <weeklyreport@163.com>'


DEPARTMENTS = (
    '人事行政部',
    '软件测试部',
    '产品开发部',
    '新技术研发部'
)

DEFAULT_CONTENT = "<p><strong>1、上周计划完成情况：</strong></p><ol><li></li></ol>" \
                  "<p>&nbsp;<strong>2、计划外工作（包含协助运维工作）：</strong></p><ol><li></li></ol>" \
                  "<p>&nbsp;<strong>3、重要问题：</strong></p><ol><li></li></ol>" \
                  "<p>&nbsp;<strong>4、持续未处理解决的事情：</strong></p><ol><li></li></ol>" \
                  "<p>&nbsp;<strong id=\"next_week\">5、下周计划：</strong></p><ol><li></li></ol>"


#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@db/wr_prd'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'wr_prd.sqlite')
