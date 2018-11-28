# I fight for the users!
import uuid
import flask

from src.models import blog
from src.common import database
from src.common import constants


class User(object):
    """ let those bitches log in, i guess
    """
    def __init__(self, email, password, username=None, _id=None):
        """
        :param email: The unique email used to identify the user
        :param password: The secure password used to log in
        :param username: Optional alias that will appear as 'author name'
        :param _id: The unique assigned ID. Have to take it in as a parameter when retrieved from database.
        TODO: figure out how to not have to take in _id because we don't want it getting set by the user
        """
        self.email = email
        self.password = password
        self.username = username or email
        self._id = _id or uuid.uuid4().hex

    @classmethod
    def from_mongodb_by_email(cls, email):
        user_data = database.Database.find_one(collection=constants.USERS_COLLECTION,
                                               query={constants.EMAIL: email})
        if user_data is not None:
            # user_data = user_data[0]
            return cls(**user_data)

    @classmethod
    def from_mongodb_by_id(cls, _id):
        user_data = database.Database.find_one(collection=constants.USERS_COLLECTION,
                                               query={constants.USER_ID: _id})
        if user_data is not None:
            # user_data = user_data[0]
            return cls(**user_data)

    @classmethod
    def login_valid(cls, email, password):
        user = cls.from_mongodb_by_email(email=email)
        if user is not None:
            return user.password == password
        raise IncorrectPasswordException("Email {} does not match given password.".format(email))

    @classmethod
    def register(cls, email, password):
        user = cls.from_mongodb_by_email(email=email)
        if user is not None:
            raise UserAlreadyExistsException("User {} is already registered.".format(email))
        new_user = cls(email=email, password=password)
        new_user.save_to_mongodb()
        flask.session[constants.EMAIL] = email
        return True

    @staticmethod
    def login(email, password):
        if User.login_valid(email, password):
            flask.session[constants.EMAIL] = email

    @staticmethod
    def logout():
        flask.session[constants.EMAIL] = None

    def make_json(self):
        json_line = {constants.EMAIL:    self.email,
                     constants.PASSWORD: self.password,
                     constants.USERNAME: self.username,
                     constants.SELF_ID:  self._id
                     }
        return json_line

    def save_to_mongodb(self):
        database.Database.insert(collection=constants.USERS_COLLECTION,
                                 data=self.make_json())

    def get_blogs(self):
        """ The user _id is used as the author id to uniquely identify author.
        Use it to get the blogs authored by this user."""
        return blog.Blog.from_mongodb_by_author_id(author_id=self._id)

    def create_blog(self, title, description):
        new_blog = blog.Blog(author=self.username, title=title, description=description, author_id=self._id)
        return new_blog

    def create_post(self, blog_id, title, content):
        post_blog = blog.Blog.from_mongodb_by_blog_id(blog_id=blog_id)
        post_blog.create_post(post_title=title, post_content=content)


class UserAlreadyExistsException(Exception):
    """ Exception for if you try to register an existing user. """


class IncorrectPasswordException(Exception):
    """ Exception for when given email and password do not match """
