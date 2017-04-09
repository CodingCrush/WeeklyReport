import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nobody knows the password'
    PER_PAGE = 10
    FLASK_ADMIN_EMAIL = "codingcrush@163.com"
    MONGODB_SETTINGS = {'db': 'wr',
                        'host': '127.0.0.1',
                        'port': 27017,
                        'username': 'wr_usr',
                        'password': 'wr_pwd',
                        }

    IMAGE_UPLOAD_DIR = 'static/upload/'
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'app/static/upload/')

    @staticmethod
    def init_app(app):
        pass

    Departments = (
        '人力资源部',
        '行政部',
        '测试部',
    )

    Projects = (
        'project1',
        'project2	',
        'project3',
        'project4',
    )
config = {'default': Config}
