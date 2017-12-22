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

MAIL_SERVER = 'smtp.163.com'
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

DEFAULT_CONTENT = "<p><strong>本周工作内容:</strong></p><ol><li></li></ol>" \
                  "<p>&nbsp;<strong>下周计划:</strong></p><ol><li></li></ol>"


SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@db/wr_prd'
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'wr_prd.sqlite')
