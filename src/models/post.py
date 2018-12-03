# make the posts of our terminal blog
import datetime
import uuid
from src.common import database
from src.common import constants


class Post(object):

    def __init__(self, author, title, blog_id, content=None, _id=None, date=None):
        self.author = author
        self.title = title
        self.blog_id = blog_id
        self._id = _id or uuid.uuid4().hex
        self.content = content
        self.date = date or datetime.datetime.utcnow()

    def save_to_mongodb(self):
        database.Database.insert(collection=constants.POSTS_COLLECTION,
                                 data=self.make_json())

    def make_json(self):
        json_line = {constants.BLOG_ID: self.blog_id,
                     constants.SELF_ID: self._id,
                     constants.AUTHOR:  self.author,
                     constants.TITLE:   self.title,
                     constants.CONTENT: self.content,
                     constants.DATE:    self.date
                     }
        return json_line

    @classmethod
    def from_mongodb(cls, _id):
        post_data = database.Database.find_one(collection=constants.POSTS_COLLECTION,
                                               query={constants.SELF_ID: _id})
        # post_data = post_data[0]
        return cls(**post_data)

    @classmethod
    def from_blog(cls, blog_id):
        return [cls(**post) for post in database.Database.find(collection=constants.POSTS_COLLECTION,
                                                               query={constants.BLOG_ID: blog_id})]
