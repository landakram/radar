import datetime

from flask.ext.mongokit import Document
from mongokit import ObjectId

class Entry(Document):
    __collection__ = 'entries'
    structure = {
        'title': unicode,
        'url': unicode,
        'author': unicode,
        'description': unicode,
        'published': datetime.datetime,
        'date_added': datetime.datetime,
        'keywords':[unicode]
    }
    use_dot_notation = True

class Feed(Document):
    __collection__ = 'feeds'
    structure = {
        'title': unicode,
        'url': unicode,
        'description': unicode,
        'published':  datetime.datetime, # feed.published_parsed
        'date_added': datetime.datetime,
        'entries': [Entry]
    }
    use_dot_notation = True

class User(Document):
    __collection__ = 'users'

    structure = {
        'email': unicode,
        'first_name': unicode,
        'feeds': [Feed],
        'clef_id': long,
        'hidden_entries': [ObjectId]
    }

    use_dot_notation = True

class GoodToken(Document):
    __collection__ = 'goodtokens'

    structure = {
        'value': unicode,
        'count': int,
        'user_id': ObjectId
    }
    use_dot_notation = True

class BadToken(Document):
    __collection__ = 'badtokens'

    structure = {
        'value': unicode,
        'count': int,
        'user_id': ObjectId
    }
    use_dot_notation = True

