from flask.ext.mongokit import Document

import datetime

class Entry(Document):
    __collection__ = 'entries'
    structure = {
        'title': unicode,
        'url': unicode,
        'author': unicode,
        'description': unicode,
        'published': datetime.datetime,
        'date_added': datetime.datetime
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

class TotalCount(Document):
    __collection__ = 'counts'
    structure = {
        'good': int,
        'bad': int
    }
    use_dot_notation = True

class Token(Document):
    __collection__ = 'tokens'
    structure = {
        'value': unicode,
        'good': int,
        'bad': int
    }
    use_dot_notation = True

