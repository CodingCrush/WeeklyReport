from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from flask import current_app
from flask_login import UserMixin


class Permission:
    DO_NOTHING = 0x00
    WRITE_REPORT = 0x01
    READ_DEPARTMENT_REPORT = 0x02
    READ_ALL_REPORT = 0X04
    ENTER_ADMIN = 0x08


class Role(db.DynamicDocument):
    name = db.StringField(unique=True)
    permissions = db.IntField()

    @staticmethod
    def insert_roles():
        roles = {
            'BAD_GUY': Permission.DO_NOTHING,
            'EMPLOYEE': Permission.WRITE_REPORT,
            'MANAGER': (Permission.WRITE_REPORT |
                        Permission.READ_DEPARTMENT_REPORT |
                        Permission.ENTER_ADMIN),
            'HR': (Permission.WRITE_REPORT |
                   Permission.READ_DEPARTMENT_REPORT |
                   Permission.READ_ALL_REPORT),
            'BOSS': (Permission.WRITE_REPORT |
                     Permission.READ_DEPARTMENT_REPORT |
                     Permission.READ_ALL_REPORT),
            'Administrator': 0xff,
        }
        for r in roles:
            role = Role.objects(name=r).first()
            if role is None:
                Role(name=r,
                     permissions=roles[r]).save()

    def __str__(self):
        return self.name


class Department(db.DynamicDocument):
    name = db.StringField(required=True)

    @staticmethod
    def insert_departments():
        for dept in current_app.config['DEPARTMENTS']:
            if not Department.objects(name=dept).first():
                Department(name=dept).save()

    def __str__(self):
        return self.name


class Project(db.DynamicDocument):
    name = db.StringField(required=True)
    is_closed = db.BooleanField(default=False)

    @staticmethod
    def insert_projects():
        for proj in current_app.config['PROJECTS']:
            if not Project.objects(name=proj).first():
                Project(name=proj).save()

    def __str__(self):
        return self.name


class User(db.DynamicDocument, UserMixin):
    email = db.EmailField(required=True)
    username = db.StringField(max_length=50, required=True)
    password = db.StringField(max_length=50, required=True)
    password_hash = db.StringField(max_length=255)
    role = db.ReferenceField(Role)
    department = db.ReferenceField(Department)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permisson):
        return self.role is not None and \
               (self.role.permissions & permisson) == permisson

    def is_leader(self):
        return self.role is not None and \
               (self.role.permissions & Permission.READ_DEPARTMENT_REPORT)\
               == Permission.READ_DEPARTMENT_REPORT

    @property
    def is_admin(self):
        return self.email == current_app.config['FLASK_ADMIN_EMAIL']

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username


class Report(db.DynamicDocument):
    created_at = db.DateTimeField(default=datetime.now)
    author = db.StringField()
    project = db.ReferenceField(Project)
    content = db.StringField(required=True)
    week_count = db.IntField()
    year = db.IntField()

    def get_department_name(self):
        try:
            return User.objects.get(username=self.author).department.name
        except User.DoesNotExist:
            return None


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
