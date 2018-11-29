import flask
import uuid

from src.common import constants
from src.common import database
from src.models import user


web_app = flask.Flask(__name__)
web_app.secret_key = uuid.uuid4().hex


# initialize the database before anything else!!!
@web_app.before_first_request
def initialize_database():
    database.Database.initialize()


@web_app.route('/login')
def hello_world():
    return flask.render_template('login.html')


@web_app.route('/auth/login', methods=['POST'])
def login():
    email = flask.request.form[constants.EMAIL]
    password = flask.request.form[constants.PASSWORD]
    valid = user.User.login_valid(email, password)
    if valid:
        user.User.login(email)
        return flask.render_template('profile.html', email=flask.session[constants.EMAIL])
    else:
        flask.session[constants.EMAIL] = None
        return flask.render_template('register.html')


@web_app.route('/auth/register', methods=['POST'])
def register():
    email = flask.request.form[constants.EMAIL]
    password = flask.request.form[constants.PASSWORD]

    new_user = user.User.register(email, password)
    if new_user:
        return flask.render_template('profile.html', email=flask.session[constants.EMAIL])
    else:
        flask.session[constants.EMAIL] = None
        return flask.render_template('register.html')


if __name__ == '__main__':
    web_app.run()
