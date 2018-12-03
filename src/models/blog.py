# make the blog class
import uuid
from src.models import post
from src.common import database
from src.common import constants


class Blog(object):

    def __init__(self, author, title, description, author_id, _id=None):
        self.author = author
        self.title = title
        self.description = description
        self.author_id = author_id
        self._id = _id or uuid.uuid4().hex

    def create_post(self, post_title, post_content):
        new_post = post.Post(author=self.author,
                             title=post_title,
                             blog_id=self._id,
                             content=post_content
                             )
        new_post.save_to_mongodb()

    def posts(self):
        return post.Post.from_blog(blog_id=self._id)

    def save_to_mongodb(self):
        database.Database.insert(collection=constants.BLOGS_COLLECTION,
                                 data=self.make_json()
                                 )

    def make_json(self):
        json_line = {constants.SELF_ID:     self._id,
                     constants.AUTHOR:      self.author,
                     constants.DESCRIPTION: self.description,
                     constants.TITLE:       self.title,
                     constants.AUTHOR_ID:   self.author_id
                     }
        return json_line

    @classmethod
    def from_mongodb_by_blog_id(cls, blog_id):
        blog_data = database.Database.find_one(collection=constants.BLOGS_COLLECTION,
                                               query={constants.SELF_ID: blog_id})
        return cls(**blog_data)

    @classmethod
    def from_mongodb_by_author_id(cls, author_id):
        blogs = database.Database.find(collection=constants.BLOGS_COLLECTION,
                                       query={constants.AUTHOR_ID: author_id})
        return [cls(**blog_data) for blog_data in blogs]
