from flask.ext.mongokit import MongoKit
from models import Entry, Feed, User, GoodToken, BadToken

db = MongoKit()
db.register([Entry, Feed, User, GoodToken, BadToken])
