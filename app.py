import functools

import datetime
import requests
import json

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from mongokit import ObjectId

from db import db
from feeds import update_feed, create_feed
from naive_bayes import stopwords, create_tokens, naive_bayes

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

def login_required(view):
    @functools.wraps(view)
    def decorated_view(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('index'))
        user = db.User.get_from_id(user_id)
        return view(user=user, *args, **kwargs)
    return decorated_view


@app.route('/keyword', methods=['POST'])
@login_required
def add_good_keyword(user=None):
    token = unicode(request.form['keyword'])

    if token in stopwords:
        return jsonify(success=True)

    is_bad = int(request.form['bad']) == 1
    if is_bad:
        TokenClass = db.BadToken
    else:
        TokenClass = db.GoodToken
    g_token = TokenClass.find_one({"user_id": user._id, "value": token})
    if not g_token:
        g_token = TokenClass()
        g_token['value'] = token
        g_token['count'] = 0
        g_token['user_id'] = user._id

    g_token['count'] += 3
    g_token.save()
    return jsonify(success=True)


@app.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('index.html')
    else:
        user = db.User.get_from_id(user_id)
        if not user:
            return render_template('index.html')

        entries = []
        for feed in user.feeds:
            update_feed(feed)
            user.save()

            for entry in feed['entries']:
                entry['feed_title'] = feed['title']
                hidden_entries = user.hidden_entries
                if entry['_id'] not in hidden_entries:
                    entries.append(entry)
        entries.sort(key=lambda e: compute_score(user=user, entry=e), reverse=True)

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
    is_bad = int(request.args['bad']) == 1
    if is_bad:
        create_tokens(entry=entry, user=user, good=False)

        user.hidden_entries.append(entry['_id'])
        user.save()

        return redirect(url_for('index'))
    else:
        create_tokens(entry=entry, user=user, good=True)
        return redirect(entry.url)


def compute_score(*args,**kwargs):
    time_norm = 1-float((kwargs.get('entry')["published"]-(datetime.datetime.now()-datetime.timedelta(days=1))).seconds)/86400.0
    naive_bayes_result = naive_bayes(user=kwargs.get('user'),entry=kwargs.get('entry'))
    bayes_norm = (naive_bayes_result["good"]-naive_bayes_result["bad"]) if naive_bayes_result["bad"]<0.5 else 0
    sorted_important_words = sorted(naive_bayes_result["important_words"], key=lambda e: e["frequency"], reverse=True)
    kwargs.get('entry')["keywords"] = ([w["value"] for w in sorted_important_words][:5]) if (sorted_important_words) else []
    # kwargs.get('entry').save()
    kwargs.get('user').save()
    return (time_norm**2+bayes_norm**2)**0.5


if __name__ == '__main__':
    app.run(debug=True)
