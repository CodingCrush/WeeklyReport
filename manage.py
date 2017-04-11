from app import create_app, db
from flask_script import Manager, Shell
import os
from app.models import Role, Department, Project, Report


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Role=Role, Department=Department,
                Project=Project, Report=Report)

manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from app.models import Role, Department, Project

    # create user roles departments
    Role.insert_roles()
    Department.insert_departments()
    Project.insert_projects()


if __name__ == '__main__':
    manager.run()
