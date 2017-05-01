from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .utils import get_week_count, get_last_week


class Permission:
    DO_NOTHING = 0x00
    WRITE_REPORT = 0x01
    READ_DEPARTMENT_REPORT = 0x02
    READ_ALL_REPORT = 0X04
    ENTER_ADMIN = 0x08


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'QUIT': Permission.DO_NOTHING,
            'EMPLOYEE': Permission.WRITE_REPORT,
            'MANAGER': (Permission.WRITE_REPORT |
                        Permission.READ_DEPARTMENT_REPORT |
                        Permission.ENTER_ADMIN),
            'HR': (Permission.WRITE_REPORT |
                   Permission.READ_DEPARTMENT_REPORT |
                   Permission.READ_ALL_REPORT),
            'ADMINISTRATOR': 0xff,
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r,
                            permissions=roles[r])
            db.session.add(role)
        db.session.commit()

    def __str__(self):
        return self.name


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='department', lazy='dynamic')

    @staticmethod
    def insert_departments():
        for dept in current_app.config['DEPARTMENTS']:
            if not Department.query.filter_by(name=dept).first():
                dept = Department(name=dept)
                db.session.add(dept)
            db.session.commit()

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_ignored = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

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

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True


    @property
    def is_admin(self):
        return self.email == current_app.config['FLASK_ADMIN_EMAIL'] or \
               self.role.name == 'ADMINISTRATOR'

    @property
    def is_hr(self):
        return self.role is not None and self.role.name == 'HR'

    @property
    def is_manager(self):
        return self.role is not None and self.role.name == 'MANAGER'

    @property
    def is_authenticated(self):
        return self.can(Permission.WRITE_REPORT)

    def __str__(self):
        return self.email


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    @property
    def is_authenticated(self):
        return False

    @property
    def email(self):
        return 'AnonymousUser'

    @property
    def is_admin(self):
        return False


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    week_count = db.Column(db.Integer)
    year = db.Column(db.Integer)

    @property
    def author(self):
        return User.query.get(self.author_id)

    @property
    def department(self):
        return User.query.get(self.author_id).department

    @property
    def is_of_current_week(self):
        if self.week_count == get_week_count() \
                and self.year == datetime.today().year:
            return True
        return False

    @property
    def is_of_last_week(self):
        if self.week_count == get_week_count(get_last_week()) \
                and self.year == get_last_week().year:
            return True
        return False

    def __str__(self):
        return 'Posted by {} at {}'.format(
            User.query.get(self.author_id).email, self.created_at)


@login_manager.user_loader
def load_user(user_id):
    assert type(user_id) == str
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
