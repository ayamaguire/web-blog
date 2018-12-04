import flask
import uuid

from src.common import constants
from src.common import database
from src.models import blog
from src.models import user
from src.models import post


web_app = flask.Flask(__name__)
web_app.secret_key = uuid.uuid4().hex


# initialize the database before anything else!!!
@web_app.before_first_request
def initialize_database():
    database.Database.initialize()


@web_app.route('/home')
def home_template():
    return flask.render_template('home.html')


@web_app.route('/login')
def login_template():
    return flask.render_template('login.html')


@web_app.route('/register')
def register_template():
    return flask.render_template('register.html')


@web_app.route('/auth/login', methods=['POST'])
def login():
    email = flask.request.form[constants.EMAIL]
    password = flask.request.form[constants.PASSWORD]
    valid = user.User.login_valid(email, password)
    if valid:
        user.User.login(email)
        return flask.make_response(user_blogs())
        # return flask.render_template('profile.html', email=flask.session[constants.EMAIL])
    else:
        flask.session[constants.EMAIL] = None
        return flask.render_template('register.html')


@web_app.route('/auth/register', methods=['POST'])
def register():
    email = flask.request.form[constants.EMAIL]
    password = flask.request.form[constants.PASSWORD]

    new_user = user.User.register(email, password)
    if new_user:
        return flask.make_response(user_blogs())
        # return flask.render_template('profile.html', email=flask.session[constants.EMAIL])
    else:
        flask.session[constants.EMAIL] = None
        return flask.render_template('register.html')


@web_app.route('/blogs/<string:user_id>')
@web_app.route('/blogs')
def user_blogs(user_id=None):
    if user_id is None:
        active_user = user.User.from_mongodb_by_email(email=flask.session[constants.EMAIL])
    else:
        active_user = user.User.from_mongodb_by_id(_id=user_id)
    active_blogs = active_user.get_blogs()
    return flask.render_template('user_blogs.html', email=active_user.email, blogs=active_blogs)


@web_app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    active_blog = blog.Blog.from_mongodb_by_blog_id(blog_id=blog_id)
    posts = active_blog.posts()
    return flask.render_template('posts.html', posts=posts, blog_title=active_blog.title, blog_id=blog_id)


@web_app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    if flask.request.method == 'GET':
        return flask.render_template('new_blog.html')
    elif flask.request.method == 'POST':
        title = flask.request.form[constants.TITLE]
        description = flask.request.form[constants.DESCRIPTION]
        current_user = user.User.from_mongodb_by_email(email=flask.session[constants.EMAIL])
        new_blog = blog.Blog(author=current_user.email,
                             title=title,
                             description=description,
                             author_id=current_user._id)
        new_blog.save_to_mongodb()
        return flask.make_response(user_blogs(user_id=current_user._id))


@web_app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
def create_new_post(blog_id):
    if flask.request.method == 'GET':
        return flask.render_template('new_post.html', blog_id=blog_id)
    elif flask.request.method == 'POST':
        title = flask.request.form[constants.TITLE]
        content = flask.request.form[constants.CONTENT]
        current_user = user.User.from_mongodb_by_email(email=flask.session[constants.EMAIL])
        new_post = post.Post(author=current_user.email,
                             title=title,
                             content=content,
                             blog_id=blog_id)
        new_post.save_to_mongodb()
        return flask.make_response(blog_posts(blog_id=blog_id))


if __name__ == '__main__':
    web_app.run(port=8000, debug=True)
