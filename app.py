from flask import Flask
from flask.ext.mongokit import MongoKit
from models import Entry, Feed, TotalCount, Token
import datetime

app = Flask(__name__)
app.config.from_object('config')

db = MongoKit(app)
db.register([Entry, Feed, TotalCount, Token])

@app.route('/')
def index():
    entry = db.Entry()
    entry.title = u'foo'
    entry.url = u'http://example.com'
    entry.description = u'Foo description'
    entry.published = datetime.datetime.now()
    entry.date_added = datetime.datetime.now()
    entry.save()
    return 'Surprise'

@app.route('/test')
def test():
    entries = db.Entry.find()
    return repr([entry for entry in entries])


if __name__ == '__main__':
    app.run(debug=True)
