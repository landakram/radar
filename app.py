import functools

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, Response
from flask.ext.mongokit import MongoKit
from mongokit import ObjectId
from models import Entry, Feed, User, GoodToken, BadToken
import requests
import operator
import json
import feedparser as fp
import datetime
from time import mktime
import naive_bayes as nb

app = Flask(__name__)
app.config.from_object('config')

db = MongoKit(app)
db.register([Entry, Feed, User, GoodToken, BadToken])

def login_required(view):
    @functools.wraps(view)
    def decorated_view(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('index'))
        user = db.User.get_from_id(user_id)
        return view(user=user, *args, **kwargs)
    return decorated_view

@app.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        user = None
        return render_template('index.html')
    else:
        user = db.User.get_from_id(user_id)
        entries = []
        if user:
            for feed in user.feeds:
                for entry in feed['entries']:
                    entry['feed_title'] = feed['title']
                    hidden_entries = user.hidden_entries
                    if entry['_id'] not in hidden_entries:
                        entries.append(entry)
            entries.sort(key=lambda e: e['published'])

        # strftime('%A, %B %d, %I:%M%p')
        return render_template('show_entries.html', user=user, entries=entries)


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    code = request.args.get('code')
    data = {
        'app_id': app.config['CLEF_APP_ID'],
        'app_secret': app.config['CLEF_APP_SECRET'],
        'code': code
    }
    response = requests.post('https://clef.io/api/v1/authorize', data=data)
    json_response = json.loads(response.text)

    if json_response.get('error'):
        return json_response['error']

    token = json_response['access_token']
    response = requests.get('https://clef.io/api/v1/info?access_token=%s' % token)
    json_response = json.loads(response.text)

    if json_response.get('error'):
        return json_response['error']

    user_info = json_response['info']

    # Look up the user
    user = db.User.find_one({'clef_id': long(user_info['id'])})
    if not user:
        user = db.User()
        user.email = user_info['email']
        user.first_name = user_info['first_name']
        user.clef_id = long(user_info['id'])
        user.feeds = []

        user.save()

    session['user_id'] = user._id
    return redirect(url_for('index'))


@app.route('/test')
def test(user=None):
    entries = db.Entry.find()
    return repr([entry for entry in entries])

@app.route('/feed', methods=['POST'])
@login_required
def add_feed(user=None):
    feed_url = request.form['url']
    feed = create_feed(url=feed_url)
    user.feeds.append(feed)
    user.save()
    return redirect(url_for('index'))


@app.route('/log_click', methods=['GET'])
@login_required
def log_click(user=None):
    entry = db.Entry.get_from_id(ObjectId(request.args['entry_id']))
    if bool(request.args['bad']):
        create_tokens(entry=entry, user=user, good=False)

        user.hidden_entries.append(entry['_id'])
        user.save()

        return redirect(url_for('index'))
    else:
        create_tokens(entry=entry, user=user, good=True)
        return redirect(entry.url)

def entry_unique_tokens(entry):
    tokens = nb.tokenize_title(entry.title) + nb.tokenize_title(entry.description)
    # assigns frequency value to each token:
    unique_tokens = {}
    for w in tokens:
        if w in unique_tokens:
            unique_tokens[w] += 1
        else:
            unique_tokens[w] = 1
    return unique_tokens

def create_tokens(*args,**kwargs):
    # assigns frequency value to each token:
    unique_tokens = entry_unique_tokens(kwargs.get('entry'))
    user = kwargs.get('user')
    for token, count in unique_tokens.iteritems():
        utoken = unicode(token)
        if kwargs.get('good') == True:
            # good token
            g_token = db.GoodToken.find_one({"user": user, "value": utoken})
            if g_token:
                g_token.count += count
            else:
                g_token = db.GoodToken()
                g_token.value = utoken
                g_token.count = count
                g_token.user  = user

            g_token.save()
        else:
            # bad token
            b_token = db.BadToken.find_one({"user": user, "value": utoken})
            if b_token:
                b_token.count += count
            else:
                b_token = db.BadToken()
                b_token.value = utoken
                b_token.count = count
                b_token.user  = user

            b_token.save()
    return unique_tokens


def create_feed(*args, **kwargs):
    # parse the url from the arguments
    url              = kwargs.get('url')
    found_feed       = fp.parse(url)
    feed = db.Feed.find_one({'url' : found_feed.url})
    if feed:
        return feed
    else:
        # parsed feed creates new feed object if feed does
        # not exist yet.
        feed             = db.Feed()
        feed.title       = found_feed.feed.title
        feed.url         = found_feed.url
        feed.description = found_feed.feed.description
        feed.published   = datetime.datetime.fromtimestamp(mktime(found_feed.feed.updated_parsed))
        feed.date_added  = datetime.datetime.now()
        feed.entries     = []
        # iterate through entries (this method should)
        # be isolated to allow updating of feeds later on
        for found_entry in found_feed.entries:
            entry = create_entry(parser=found_entry)
            feed.entries.append(entry)

        feed.save()
        return feed

def create_entry(*args, **kwargs):
    # creates a new entry either from parse data,
    # or by inputing title, desc, url...
    parsed_entry = kwargs.get('parser')
    if parsed_entry:
        entry = db.Entry.find_one({'url': parsed_entry.link})
        if entry:
            return entry
        else:
            entry             = db.Entry()
            entry.date_added  = datetime.datetime.now()
            entry.title       = parsed_entry.title
            entry.description = parsed_entry.description
            entry.url         = parsed_entry.link
            entry.published   = datetime.datetime.fromtimestamp(mktime(parsed_entry.published_parsed))
            print entry.title
            entry.save()
            return entry
    else:
        entry = db.Entry.find_one({'url':kwargs.get('url')})
        if entry:
            return entry
        else:
            entry             = db.Entry()
            entry.date_added  = datetime.datetime.now()
            entry.title       = kwargs.get('title')
            entry.url         = kwargs.get('url')
            entry.description = kwargs.get('description')
            entry.published   = kwargs.get('published')
            entry.save()
            return entry
            # can get pubdate through parsing... next time perhaps

def naive_bayes(*args,**kwargs):
    entry            = kwargs.get['entry']
    user             = kwargs.get['user']
    unique_tokens    = entry_unique_tokens(entry)
    all_prob_good    = []
    all_prob_bad     = []
    total_bad_count  = db.BadToken.find({"user":user}).count
    total_good_count = db.GoodToken.find({"user":user}).count
    for token in unique_tokens:
        bad_token  = db.BadToken.find({"user":user,  "value":token["value"]})
        good_token = db.GoodToken.find({"user":user, "value":token["value"]})
        prob_good  = 1.0
        prob_bad   = 1.0
        # find probability that token is good or bad based on frequency.
        if bad_token:
            prob_bad  = float(bad_token.count+1)/float(total_bad_count+1)
        if good_token:
            prob_good = float(good_token.count+1)/float(total_good_count+1)
        all_prob_bad.append(prob_bad)
        all_prob_good.append(prob_good)
    all_prob_bad       = float(reduce(operator.mul, all_prob_bad,  1))
    all_prob_good      = float(reduce(operator.mul, all_prob_good, 1))
    total_probability  = all_prob_bad+all_prob_good
    all_prob_bad      /= total_probability
    all_prob_good     /= total_probability
    return {"bad":all_prob_bad, "good":all_prob_good}


if __name__ == '__main__':
    app.run(debug=True)
